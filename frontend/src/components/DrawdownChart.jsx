import React from 'react';
import { Bar } from 'react-chartjs-2';
import '../chartjs-config';

export function DrawdownChart({ dates, drawdowns }) {
  return (
    <Bar
      data={{
        labels: dates,
        datasets: [{
          label: 'Drawdown',
          data: drawdowns,
          backgroundColor: drawdowns.map(v => (v < 0 ? 'red' : 'green')),
        }],
      }}
      options={{
        scales: { y: { beginAtZero: false, max: 0 } }
      }}
    />
  );
}
