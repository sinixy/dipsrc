import React, { createContext, useState, useEffect } from 'react';
import { fetchPickers, fetchRiskModels, optimize, savePortfolio } from '../api';

export const PortfolioContext = createContext();

export function PortfolioProvider({ children }) {
  const [pickers, setPickers] = useState([]);
  const [riskModels, setRiskModels] = useState([]);
  const [selectedPicker, setSelectedPicker] = useState(null);
  const [selectedRiskModel, setSelectedRiskModel] = useState(null);
  const [capital, setCapital] = useState(10000);
  const [endDate, setEndDate] = useState(new Date().toISOString().slice(0, 10));
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPickers().then(setPickers).catch(console.error);
    fetchRiskModels().then(setRiskModels).catch(console.error);
  }, []);

  const runOptimize = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await optimize(selectedPicker, selectedRiskModel, endDate, capital);
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const runSave = async (name, notes) => {
    if (!result) return;
    const payload = {
      name,
      created_at: new Date().toISOString(),
      end_date: endDate,
      capital,
      allocation: result.allocation,
      model: selectedPicker,
      optimizer: selectedRiskModel,
      notes,
    };
    return savePortfolio(payload);
  };

  return (
    <PortfolioContext.Provider
      value={{
        pickers,
        riskModels,
        selectedPicker,
        setSelectedPicker,
        selectedRiskModel,
        setSelectedRiskModel,
        capital,
        setCapital,
        endDate,
        setEndDate,
        runOptimize,
        runSave,
        loading,
        error,
        result,
      }}
    >
      {children}
    </PortfolioContext.Provider>
  );
}