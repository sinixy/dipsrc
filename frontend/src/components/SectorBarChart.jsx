// src/components/SectorBarChart.jsx
import React from 'react'; // Removed useContext
import { Bar } from 'react-chartjs-2';
// Removed PortfolioContext import
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js';
import { getSectorColors } from '../utils/colors'; // Assuming you have a color utility

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

// Accept sectorLabels and sectorWeights as props
export default function SectorBarChart({ sectorLabels, sectorWeights }) {
   // Handle missing data
  if (!sectorLabels || !sectorWeights || sectorLabels.length === 0 || sectorWeights.length === 0) {
    return <div className="text-center text-gray-500">Sector data not available.</div>;
  }

  // Combine labels and weights, then sort
  const sectors = sectorLabels.map((label, index) => ({
    label,
    weight: sectorWeights[index]
  })).sort((a, b) => b.weight - a.weight); // Sort descending by weight

  const data = {
    labels: sectors.map(s => s.label), // Use sorted labels
    datasets: [
      {
        label: 'Sector %',
        data: sectors.map(s => s.weight * 100), // Use sorted weights * 100
        backgroundColor: getSectorColors(sectors.map(s => s.label)), // Get colors based on sorted labels
        borderRadius: 4,
      },
    ],
  };

  const options = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false, // Allow height control via className
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: context => ` ${context.parsed.x.toFixed(2)}%`,
        },
      },
    },
    scales: {
      x: {
        ticks: {
          callback: val => `${val.toFixed(0)}%`,
        },
        max: 100, // Keep max at 100%
        beginAtZero: true,
      },
      y: {
        ticks: { autoSkip: false }
      },
    },
  };
  // Added class for sizing
  return <div className="h-64"><Bar data={data} options={options} /></div>;
}
