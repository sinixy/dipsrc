const defaultColors = ['#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'];
const sectorColorMap = {};
let colorIndex = 0;

export function getSectorColors(labels) {
  return labels.map(label => {
    if (!sectorColorMap[label]) {
      sectorColorMap[label] = defaultColors[colorIndex % defaultColors.length];
      colorIndex++;
    }
    return sectorColorMap[label];
  });
}