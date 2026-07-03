/**
 * Markdown and text utilities.
 */

export function downloadAsMarkdown(content: string, filename: string = "architecture.md") {
  const element = document.createElement("a");
  element.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(content));
  element.setAttribute("download", filename);
  element.style.display = "none";
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}

export function downloadAsText(content: string, filename: string = "export.txt") {
  downloadAsMarkdown(content, filename);
}

export async function downloadAsPNG(svgContent: string, filename: string = "diagram.png") {
  // This would require a library like html2canvas or similar
  // For now, just download as SVG
  const element = document.createElement("a");
  element.setAttribute("href", "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svgContent));
  element.setAttribute("download", filename.replace(".png", ".svg"));
  element.style.display = "none";
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}