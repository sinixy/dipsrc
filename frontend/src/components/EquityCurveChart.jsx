import React, { useContext } from 'react';
import { Line } from 'react-chartjs-2';
import { PortfolioContext } from '../context/PortfolioContext';
import { Chart as ChartJS, TimeScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(TimeScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

export default function EquityCurveChart() {
  const { result } = useContext(PortfolioContext);
  if (!result) return null;

  const { dates, values } = result.equity_curve;
  const data = {
    labels: dates.map(d => new Date(d)),
    datasets: [
      {
        label: 'Equity Curve',
        data: values,
        fill: false,
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      tooltip: {
        callbacks: {
          label: context => {
            const val = context.parsed.y;
            const pct = (val * 100).toFixed(2);
            return ` ${pct}%`;
          },
        },
      },
    },
    scales: {
      x: { type: 'time', time: { unit: 'week' } },
      y: {
        type: 'linear',
        ticks: {
          callback: val => `${(val * 100).toFixed(0)}%`,
        },
      },
    },
  };

  return <Line data={data} options={options} className="h-64" />;
}