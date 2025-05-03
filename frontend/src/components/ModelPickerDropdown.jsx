import React, { useContext } from 'react';
import { PortfolioContext } from '../context/PortfolioContext';

export default function ModelPickerDropdown() {
  const { pickers, selectedPicker, setSelectedPicker } = useContext(PortfolioContext);
  return (
    <select
      className="border p-2 rounded"
      value={selectedPicker || ''}
      onChange={e => setSelectedPicker(e.target.value)}
    >
      <option value="" disabled>Select model</option>
      {pickers.map(name => (
        <option key={name} value={name}>{name}</option>
      ))}
    </select>
  );
}