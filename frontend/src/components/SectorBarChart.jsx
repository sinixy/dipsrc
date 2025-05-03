import React, { useContext } from 'react';
import { Bar } from 'react-chartjs-2';
import { PortfolioContext } from '../context/PortfolioContext';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export default function SectorBarChart() {
  const { result } = useContext(PortfolioContext);
  if (!result) return null;
  const sortedSectors = Object.fromEntries(Object.entries(result.sector_weights).sort((a, b) => b[1] - a[1]));
  const data = {
    labels: Object.keys(sortedSectors),
    datasets: [
      {
        label: 'Sector %',
        data: Object.values(sortedSectors).map(w => w * 100),
        borderRadius: 4,
      },
    ],
  };
  const options = {
    indexAxis: 'y',
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: context => {
            return ` ${context.parsed.x.toFixed(2)}%`;
          },
        },
      },
    },
    scales: {
      x: {
        ticks: {
          callback: val => `${val.toFixed(0)}%`,
        },
        max: 100,
      },
      y: { ticks: { autoSkip: false } },
    },
  };
  return <Bar data={data} options={options} className="h-48" />;
}
