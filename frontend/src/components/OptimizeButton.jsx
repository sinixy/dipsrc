import React, { useContext } from 'react';
import { PortfolioContext } from '../context/PortfolioContext';

export default function OptimizeButton() {
  const { selectedPicker, selectedRiskModel, runOptimize, loading } = useContext(PortfolioContext);
  const disabled = !selectedPicker || !selectedRiskModel || loading;
  return (
    <button
      className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
      onClick={runOptimize}
      disabled={disabled}
    >
      {loading ? 'Optimizing...' : 'Optimize'}
    </button>
  );
}