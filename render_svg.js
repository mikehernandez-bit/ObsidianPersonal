const fs = require('fs');
const data = JSON.parse(fs.readFileSync('C:/Users/jhoan/Documents/Obsidian/Personal/test_drawing.json', 'utf8'));

const elements = data.elements;
const appState = data.appState;

const scale = 3;
const padding = 20;

let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
elements.forEach(el => {
  if (el.points) {
    el.points.forEach(pt => {
      const x = el.x + pt[0];
      const y = el.y + pt[1];
      minX = Math.min(minX, x);
      minY = Math.min(minY, y);
      maxX = Math.max(maxX, x);
      maxY = Math.max(maxY, y);
    });
  }
});

const width = (maxX - minX + padding * 2) * scale;
const height = (maxY - minY + padding * 2) * scale;

let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="${minX - padding} ${minY - padding} ${maxX - minX + padding * 2} ${maxY - minY + padding * 2}" style="background:${appState.viewBackgroundColor}">`;

elements.forEach(el => {
  if (el.type === 'freedraw' && el.points && el.points.length > 0) {
    let pathD = '';
    el.points.forEach((pt, i) => {
      const x = el.x + pt[0];
      const y = el.y + pt[1];
      pathD += (i === 0 ? 'M' : 'L') + x + ',' + y + ' ';
    });
    svg += `<path d="${pathD}" stroke="${el.strokeColor}" stroke-width="${el.strokeWidth}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;
  }
});

svg += '</svg>';
fs.writeFileSync('C:/Users/jhoan/Documents/Obsidian/Personal/drawing.svg', svg);
console.log('Saved drawing.svg - dimensions:', Math.round(width), 'x', Math.round(height));