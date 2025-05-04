// src/components/Heatmap.jsx
import React from 'react';
import { Chart } from 'react-chartjs-2';
import '../chartjs-config';

export function Heatmap({ labels, matrix }) {
  // flatten matrix to { x, y, v } points
  const dataPoints = [];
  labels.forEach((rowLab, i) =>
    labels.forEach((colLab, j) =>
      dataPoints.push({ x: j, y: i, v: matrix[i][j] })
    )
  );

  return (
    <Chart
      type="matrix"
      data={{
        labels,
        datasets: [{
          label: 'Correlation',
          data: dataPoints,
          width: ({ chart }) => chart.chartArea.width / labels.length - 1,
          height: ({ chart }) => chart.chartArea.height / labels.length - 1,
          backgroundColor: ctx => {
            const v = ctx.dataset.data[ctx.dataIndex].v;
            const t = (v + 1) / 2;
            return `rgba(${255*(1-t)},${255*t},0,0.8)`;
          },
        }],
      }}
      options={{
        scales: {
          x: { type: 'category', labels, offset: true },
          y: { type: 'category', labels: labels.slice().reverse(), offset: true }
        },
        plugins: { legend: { display: false } }
      }}
    />
  );
}
