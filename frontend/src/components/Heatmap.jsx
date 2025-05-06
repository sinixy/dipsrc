// src/components/Heatmap.jsx
import React from 'react';
import { Chart } from 'react-chartjs-2';
import '../chartjs-config';

export function Heatmap({ labels, dataPoints }) {
  if (!labels || !dataPoints || labels.length === 0 || dataPoints.length === 0) {
    return <div className="text-center text-gray-500 h-64 flex items-center justify-center">Heatmap data not available.</div>;
  }

  const options = {
      responsive: true,
      maintainAspectRatio: false, // Allows height/width control via container
      animation: false,
      events: [],
      scales: {
        x: {
          type: 'category',
          labels: labels,
          offset: true,
          ticks: { display: true }, // Keep ticks for labels
          grid: { display: false }  // Hide grid lines
        },
        y: {
          type: 'category',
          labels: labels, // Reverse y-axis labels for typical heatmap layout
          offset: true,
          ticks: { display: true }, // Keep ticks for labels
          grid: { display: false }  // Hide grid lines
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
            callbacks: {
                title: () => '', // Hide title in tooltip
                label: (context) => {
                    const item = context.dataset.data[context.dataIndex];
                    const v = item.v;
                    const xLabel = labels[item.x];
                    const yLabel = labels[item.y]; // Use original y label index
                    return `${yLabel} / ${xLabel}: ${v.toFixed(3)}`;
                }
            }
        }
      }
  };

  const data = {
    // No top-level labels needed for matrix chart type with category scale
    datasets: [{
      label: 'Correlation',
      data: dataPoints,
      // Safer width/height calculations: check chart.chartArea
      width: ({ chart }) => {
        const area = chart.chartArea;
        // Ensure area and labels exist before calculating
        if (!area || !labels || labels.length === 0) {
          return 10; // Default small width
        }
        return (area.right - area.left) / labels.length - 1; // Use area bounds
      },
      height: ({ chart }) => {
        const area = chart.chartArea;
        // Ensure area and labels exist before calculating
        if (!area || !labels || labels.length === 0) {
          return 10; // Default small height
        }
        return (area.bottom - area.top) / labels.length - 1; // Use area bounds
      },
      backgroundColor: ctx => {
        // Check if context and data are valid
        if (!ctx || !ctx.dataset || !ctx.dataset.data || !ctx.dataset.data[ctx.dataIndex]) {
          console.error("Heatmap backgroundColor - Invalid context or data at index:", ctx?.dataIndex);
          return 'rgba(0,0,0,0.1)'; // Default background
        }
        const v = ctx.dataset.data[ctx.dataIndex].v;
        const item = ctx.dataset.data[ctx.dataIndex];
        if (ctx.dataIndex < 5 || (ctx.dataIndex > (dataPoints.length - 5))) {
          console.log(`Heatmap BG Log - Index: ${ctx.dataIndex}, x: ${item.x}, y: ${item.y}, v: ${v}`);
        }
        // --> End Log <--

        // Check if v is a valid number
        if (typeof v !== 'number' || isNaN(v)) {
          console.error(`Heatmap backgroundColor - Invalid 'v' value: ${v} at index: ${ctx.dataIndex}`);
          return 'rgba(128,128,128,0.5)'; // Gray for invalid number
        }

        const t = (v + 1) / 2; // Normalize correlation (-1 to 1) -> (0 to 1)
        // Red-Yellow-Green color scale (Red=-1, Yellow=0, Green=1)
        const R = 255 * (1 - t);
        const G = 255 * t;
        const B = 0;
        return `rgba(${R.toFixed(0)},${G.toFixed(0)},${B},0.8)`;
      },
      borderWidth: 1, // Add slight border for clarity
      borderColor: 'rgba(0,0,0,0.2)'
    }],
  };

 

  return (
    <div className="h-64 w-full">
        <Chart type="matrix" data={data} options={options} />
    </div>
  );
}
