const API_BASE = window.APP_CONFIG?.apiBaseUrl ?? "";

const listEl = document.getElementById("pdf-list");
const statusEl = document.getElementById("status");
const countEl = document.getElementById("count");
const viewerEl = document.getElementById("viewer");
const viewerTitleEl = document.getElementById("viewer-title");
const viewerFrameEl = document.getElementById("viewer-frame");

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function pdfUrl(name, download = false) {
  const url = `${API_BASE}/api/pdfs/${encodeURIComponent(name)}`;
  return download ? `${url}?download=true` : url;
}

function openViewer(name) {
  viewerTitleEl.textContent = name;
  viewerFrameEl.src = pdfUrl(name);
  viewerEl.hidden = false;
  viewerEl.scrollIntoView({ behavior: "smooth" });
}

function closeViewer() {
  viewerEl.hidden = true;
  viewerFrameEl.src = "about:blank";
}

function renderList(files) {
  listEl.replaceChildren();
  countEl.textContent = `(${files.length})`;

  if (files.length === 0) {
    statusEl.textContent = "No documents yet.";
    return;
  }
  statusEl.textContent = "";

  for (const file of files) {
    const item = document.createElement("li");

    const info = document.createElement("div");
    const name = document.createElement("strong");
    name.textContent = file.name;
    const size = document.createElement("small");
    size.textContent = formatSize(file.size_bytes);
    info.append(name, size);

    const readBtn = document.createElement("button");
    readBtn.type = "button";
    readBtn.textContent = "Read";
    readBtn.addEventListener("click", () => openViewer(file.name));

    const downloadLink = document.createElement("a");
    downloadLink.href = pdfUrl(file.name, true);
    downloadLink.textContent = "Download";
    downloadLink.className = "button secondary";

    item.append(info, readBtn, downloadLink);
    listEl.append(item);
  }
}

async function loadPdfs() {
  try {
    const response = await fetch(`${API_BASE}/api/pdfs`);
    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }
    const data = await response.json();
    renderList(data.files);
  } catch (error) {
    statusEl.textContent = `Could not load documents: ${error.message}`;
    console.error(error);
  }
}

document.getElementById("close-viewer").addEventListener("click", closeViewer);
loadPdfs();
