import React from 'react';
import { Line } from 'react-chartjs-2';
import '../chartjs-config';

export function EquityChart({ dates, equityValues, spyValues }) {
  const data = {
    labels: dates,
    datasets: [
      { label: 'Portfolio', data: equityValues, borderColor: 'blue', fill: false },
      { label: 'SPY',       data: spyValues,    borderColor: 'gold', fill: false },
    ],
  };
  const options = {
    scales: { x: { title: { display: true, text: 'Date' } }, y: { title: { display: true, text: 'Cumulative Return' } } }
  };

  return <Line data={data} options={options} />;
}
