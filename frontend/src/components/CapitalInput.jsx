import React, { useContext } from 'react';
import { PortfolioContext } from '../context/PortfolioContext';

export default function CapitalInput() {
  const { capital, setCapital } = useContext(PortfolioContext);
  return (
    <div className="flex items-center space-x-2">
      <label className="text-sm">Capital ($):</label>
      <input
        type="number"
        className="border p-1 rounded w-32"
        value={capital}
        onChange={e => setCapital(Number(e.target.value))}
      />
    </div>
  );
}