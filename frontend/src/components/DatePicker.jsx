import React, { useContext } from 'react';
import { PortfolioContext } from '../context/PortfolioContext';

export default function DatePicker() {
  const { endDate, setEndDate } = useContext(PortfolioContext);
  return (
    <div className="flex items-center space-x-2 ml-auto">
      <label className="text-xl">Snapshot Date:</label>
      <input
        type="date"
        className="border p-2 rounded"
        value={endDate}
        onChange={e => setEndDate(e.target.value)}
      />
    </div>
  );
}