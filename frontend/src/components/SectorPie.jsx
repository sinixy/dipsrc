import React from 'react';
import { Pie } from 'react-chartjs-2';
import '../chartjs-config';

export function SectorPie({ labels, weights, colors }) {
  return (
    <Pie
      data={{ labels, datasets: [{ data: weights, backgroundColor: colors }] }}
      options={{ plugins: { legend: { position: 'right' } } }}
    />
  );
}
