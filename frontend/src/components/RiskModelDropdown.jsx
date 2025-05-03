import React, { useContext } from 'react';
import { PortfolioContext } from '../context/PortfolioContext';

export default function RiskModelDropdown() {
  const { riskModels, selectedRiskModel, setSelectedRiskModel } = useContext(PortfolioContext);
  return (
    <select
      className="border p-2 rounded"
      value={selectedRiskModel || ''}
      onChange={e => setSelectedRiskModel(e.target.value)}
    >
      <option value="" disabled>Select risk model</option>
      {riskModels.map(name => (
        <option key={name} value={name}>{name}</option>
      ))}
    </select>
  );
}