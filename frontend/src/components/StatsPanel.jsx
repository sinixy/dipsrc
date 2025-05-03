import React, { useContext } from 'react';
import { PortfolioContext } from '../context/PortfolioContext';

export default function StatsPanel() {
  const { result } = useContext(PortfolioContext);
  if (!result) return null;

  const stats = result.stats;

  return (
    <div className="grid grid-cols-3 gap-4">
      {Object.entries(stats).map(([label, value]) => (
        <div key={label} className="border rounded p-2 bg-gray-50 dark:bg-gray-600">
          <div className="text-sm text-gray-500 dark:text-gray-400">{label}</div>
          <div className="text-lg font-semibold text-gray-800 dark:text-gray-200">{value}</div>
        </div>
      ))}
    </div>
  );
}