const { serializeAsJSON } = require("@excalidraw/excalidraw/data/json");
const { exportToCanvas } = require("@excalidraw/excalidraw");
const { restoreAppState } = require("@excalidraw/excalidraw/data/restore");
const fs = require("fs");

const drawingData = fs.readFileSync("C:/Users/jhoan/Documents/Obsidian/Personal/test_drawing.json", "utf8");
const data = JSON.parse(drawingData);

async function render() {
  const canvas = await exportToCanvas(data.elements, data.appState, data.files || {}, {
    background: true,
    padding: 20,
    scale: 1,
  });

  const ctx = canvas.getContext("2d");
  const dataUrl = canvas.toDataURL("image/png", 1.0);

  const base64Data = dataUrl.replace(/^data:image\/png;base64,/, "");
  fs.writeFileSync("drawing.png", Buffer.from(base64Data, "base64"));

  console.log("Saved as drawing.png");
  console.log("Canvas size:", canvas.width, "x", canvas.height);
}

render().catch(console.error);