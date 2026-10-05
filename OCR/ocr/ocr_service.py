"""PaddleOCR inference and Maharashtra HSC marksheet extraction."""

import re

from paddleocr import PaddleOCR


ocr = PaddleOCR(lang="en")

_SUBJECT_PREFIX = re.compile(r"^\s*(\d{1,3})\s*[-.]?\s*([A-Z][A-Z &()/.-]*)\s*$", re.I)
_EXAM_PATTERN = re.compile(r"\b(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|OCTOBER|NOVEMBER|DECEMBER)[ -](\d{4})\b", re.I)


def _group_rows(detections, tolerance):
    """Group OCR boxes by their vertical centers, then order each row left to right."""
    rows = []
    for item in sorted(detections, key=lambda value: value["y"]):
        row = next((candidate for candidate in rows
                    if abs(item["y"] - sum(x["y"] for x in candidate) / len(candidate)) <= tolerance), None)
        if row is None:
            rows.append([item])
        else:
            row.append(item)
    for row in rows:
        row.sort(key=lambda value: value["x"])
    return rows


def _text(detections):
    return " ".join(item["text"] for item in detections).strip()


def extract_marksheet(image_path):
    result = ocr.predict(image_path)
    detections = []
    image_width = image_height = None

    for res in result:
        texts = res.get("rec_texts", [])
        scores = res.get("rec_scores", [])
        boxes = res.get("rec_polys", [])
        for text, score, box in zip(texts, scores, boxes):
            text = str(text).strip()
            if not text or float(score) < 0.35:
                continue
            xs = [float(point[0]) for point in box]
            ys = [float(point[1]) for point in box]
            x_min, x_max = min(xs), max(xs)
            y_min, y_max = min(ys), max(ys)
            image_width = max(image_width or 0, x_max)
            image_height = max(image_height or 0, y_max)
            detections.append({
                "text": text,
                "score": float(score),
                "x": (x_min + x_max) / 2,
                "y": (y_min + y_max) / 2,
                "height": y_max - y_min,
            })

    if not detections:
        return {"exam": None, "seat_no": None, "centre_no": None,
                "school_index_no": None, "subjects": [], "total_marks": None,
                "percentage": None}

    # Normalize positions so the same column logic works across scan resolutions.
    width = image_width or 1
    height = image_height or 1
    for item in detections:
        item["nx"] = item["x"] / width
        item["ny"] = item["y"] / height
    rows = _group_rows(detections, max(8, height * 0.012))

    marksheet = {
        "exam": None,
        "seat_no": None,
        "centre_no": None,
        "school_index_no": None,
        "subjects": [],
        "total_marks": None,
        "percentage": None,
    }

    # The exam month/year may be printed as FEBRUARY-2002 or FEBRUARY 2002.
    for item in detections:
        match = _EXAM_PATTERN.search(item["text"].upper().replace("–", "-").replace("—", "-"))
        if match:
            marksheet["exam"] = f"{match.group(1).upper()}-{match.group(2)}"
        if re.fullmatch(r"[A-Z]?\s*\d{5,8}", item["text"].upper().replace("O", "0")):
            candidate = re.sub(r"\s+", "", item["text"]).upper()
            # OCR often reads a zero in the numeric part of an alphanumeric
            # seat number as the letter O (for example, M064043 as MO64043).
            if candidate and candidate[0].isalpha():
                candidate = candidate[0] + candidate[1:].replace("O", "0")
            else:
                candidate = candidate.replace("O", "0")
            if any(char.isdigit() for char in candidate):
                marksheet["seat_no"] = candidate

    # Pull header values from the same horizontal band as their labels, using
    # the fixed printed columns (seat, centre, school index) rather than guesses
    # based on numeric order.
    for row in rows:
        y = sum(item["ny"] for item in row) / len(row)
        if not 0.12 <= y <= 0.31:
            continue
        for item in row:
            value = item["text"].strip()
            if re.fullmatch(r"\d{2,4}", value) and 0.30 <= item["nx"] <= 0.54:
                marksheet["centre_no"] = value
            elif re.fullmatch(r"\d{1,3}\.\d{2,4}", value) and 0.46 <= item["nx"] <= 0.62:
                marksheet["school_index_no"] = value

    # Also recognize header value detections if PaddleOCR placed them on a
    # separate row from the labels.
    for item in detections:
        value = item["text"].strip()
        if 0.12 <= item["ny"] <= 0.31:
            if re.fullmatch(r"\d{2,4}", value) and 0.30 <= item["nx"] <= 0.54:
                marksheet["centre_no"] = value
            if re.fullmatch(r"\d{1,3}\.\d{2,4}", value) and 0.46 <= item["nx"] <= 0.62:
                marksheet["school_index_no"] = value

    for item in detections:
        match = re.fullmatch(r"(\d{1,3})\.(\d{2})", item["text"].strip())
        if match:
            marksheet["percentage"] = float(item["text"])

    for row in rows:
        row_text = _text(row)
        upper = row_text.upper()
        # A total row has the label and typically both the maximum and obtained
        # totals in their own columns. The obtained total is the rightmost
        # numeric value in the figures columns.
        if "TOTAL" in upper and ("MARK" in upper or "गुण" in upper or "600" in upper):
            values = []
            for item in row:
                if 0.46 <= item["nx"] <= 0.68:
                    found = re.findall(r"\b\d{1,4}\b", item["text"])
                    values.extend((int(number), item["nx"]) for number in found)
            if values:
                marksheet["total_marks"] = max(values, key=lambda pair: pair[1])[0]
            continue

        # Subject names sit in the broad left-hand table column. Codes may be
        # combined with the name ("01 ENGLISH") or detected in a separate box.
        left = [item for item in row if item["nx"] < 0.42]
        code = name = None
        for item in left:
            match = _SUBJECT_PREFIX.match(item["text"].upper())
            if match and re.search(r"[A-Z]", match.group(2)):
                code, name = match.group(1), match.group(2).strip(" .-")
                break
        if code is None:
            code_item = next((item for item in left if re.fullmatch(r"\d{1,3}", item["text"].strip())), None)
            name_items = [item for item in left if re.search(r"[A-Za-z]{2,}", item["text"])]
            if code_item and name_items:
                code = code_item["text"].strip()
                name = " ".join(item["text"].strip() for item in name_items).upper()
        if not code or not name or not re.search(r"[A-Z]{2}", name):
            continue

        column_numbers = []
        for item in row:
            if not (0.46 <= item["nx"] <= 0.69):
                continue
            token = item["text"].strip().replace("O", "0").replace("o", "0")
            if re.fullmatch(r"\d{1,3}", token):
                column_numbers.append((item["nx"], int(token)))
        max_values = [value for x, value in column_numbers if 0.46 <= x < 0.57]
        obtained_values = [value for x, value in column_numbers if 0.55 <= x <= 0.69]
        if not max_values or not obtained_values:
            continue
        marksheet["subjects"].append({
            "code": code,
            "name": re.sub(r"\s+", " ", name).strip(),
            "max_marks": max_values[0],
            "obtained_marks": obtained_values[0],
        })

    return marksheet
