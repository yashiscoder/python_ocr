const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const dropZone = document.getElementById("dropZone");
const fileInfo = document.getElementById("fileInfo");
const extractBtn = document.getElementById("extractBtn");
const status = document.getElementById("status");
const result = document.getElementById("result");
const copyBtn = document.getElementById("copyBtn");

let selectedFile = null;
let latestJSON = null;


// -------------------------
// Choose Image button
// -------------------------

browseBtn.addEventListener("click", (event) => {
    event.stopPropagation();
    fileInput.click();
});


// -------------------------
// Drop zone click
// -------------------------

dropZone.addEventListener("click", () => {
    fileInput.click();
});


// -------------------------
// File selected
// -------------------------

fileInput.addEventListener("change", () => {

    if (fileInput.files.length === 0) {
        return;
    }

    handleFile(fileInput.files[0]);
});


// -------------------------
// Handle file
// -------------------------

function handleFile(file) {

    if (!file.type.startsWith("image/")) {
        alert("Please select an image file.");
        return;
    }

    selectedFile = file;

    fileInfo.classList.remove("hidden");

    fileInfo.textContent =
        `${file.name} • ${(file.size / 1024 / 1024).toFixed(2)} MB`;

    extractBtn.disabled = false;

    status.textContent = "Image ready for OCR.";

    result.textContent = "Click \"Extract Text\" to process the image.";

    copyBtn.disabled = true;
}


// -------------------------
// Drag & Drop
// -------------------------

dropZone.addEventListener("dragover", (event) => {

    event.preventDefault();

    dropZone.classList.add("dragover");
});


dropZone.addEventListener("dragleave", () => {

    dropZone.classList.remove("dragover");
});


dropZone.addEventListener("drop", (event) => {

    event.preventDefault();

    dropZone.classList.remove("dragover");

    const file = event.dataTransfer.files[0];

    if (file) {
        handleFile(file);
    }
});


// -------------------------
// Extract OCR
// -------------------------

extractBtn.addEventListener("click", async () => {

    if (!selectedFile) {
        alert("Please select a marksheet image.");
        return;
    }

    const formData = new FormData();

    formData.append("file", selectedFile);

    extractBtn.disabled = true;

    status.textContent = "Processing marksheet...";

    result.textContent = "Running PaddleOCR...";

    copyBtn.disabled = true;

    try {

        const response = await fetch(
            "https://python-ocr-9jib.onrender.com/ocr",
            {
                method: "POST",
                body: formData
            }
        );

        if (!response.ok) {
            throw new Error(
                `Server returned ${response.status}`
            );
        }

        const data = await response.json();

        latestJSON = data;

        result.textContent =
            JSON.stringify(data, null, 2);

        status.textContent = "OCR completed successfully.";

        copyBtn.disabled = false;

    } catch (error) {

        console.error(error);

        result.textContent = JSON.stringify(
            {
                success: false,
                error: error.message
            },
            null,
            2
        );

        status.textContent = "OCR failed.";

    } finally {

        extractBtn.disabled = false;
    }
});


// -------------------------
// Copy JSON
// -------------------------

copyBtn.addEventListener("click", async () => {

    if (!latestJSON) {
        return;
    }

    await navigator.clipboard.writeText(
        JSON.stringify(latestJSON, null, 2)
    );

    copyBtn.textContent = "Copied!";

    setTimeout(() => {
        copyBtn.textContent = "Copy JSON";
    }, 1500);
});
