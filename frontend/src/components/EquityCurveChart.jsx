import React from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, TimeScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(TimeScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

export default function EquityCurveChart({ dates, equity }) {
  if (!dates || !equity || dates.length === 0 || equity.length === 0) {
    return <div className="text-center text-gray-500">Equity data not available.</div>;
  }

  const data = {
    labels: dates.map(d => new Date(d)), // Use dates prop
    datasets: [
      {
        label: 'Equity Curve',
        data: equity, // Use equity prop (API returns values relative to start=1)
        fill: false,
        borderColor: 'rgb(75, 192, 192)', // Example color
        tension: 0.1,
        borderWidth: 2,
        pointRadius: 0, // Hide points for cleaner look
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false, // Allow height control via className
    plugins: {
      legend: { display: false },
      tooltip: {
        mode: 'index',
        intersect: false,
        callbacks: {
          label: context => {
            // Assuming equity values are normalized (start at 1)
            // Adjust calculation if API sends raw values or percentages
            const val = context.parsed.y;
            const startValue = context.dataset.data[0] || 1; // Handle empty data case
            const pctChange = ((val / startValue) - 1) * 100;
            return ` Equity: ${pctChange.toFixed(2)}%`;
          },
        },
      },
    },
    scales: {
      x: {
        type: 'time',
        time: {
            unit: 'month', // Adjust unit based on data density
             tooltipFormat: 'll' // e.g., Sep 4, 1986
        },
         ticks: { major: { enabled: true } },
         grid: { display: false }
      },
      y: {
        type: 'linear',
        ticks: {
          // Format Y-axis based on what 'equity' represents (e.g., normalized value or %)
          callback: val => `${((val -1)*100).toFixed(0)}%`, // Example if equity starts at 1
        },
      },
    },
  };

  return <div className="h-64"><Line data={data} options={options} /></div>;
}