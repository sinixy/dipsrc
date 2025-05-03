import React, { createContext, useState, useEffect } from 'react';
import { fetchPickers, fetchRiskModels, optimize } from '../api';

export const PortfolioContext = createContext();

export function PortfolioProvider({ children }) {
  const [pickers, setPickers] = useState([]);
  const [riskModels, setRiskModels] = useState([]);
  const [selectedPicker, setSelectedPicker] = useState(null);
  const [selectedRiskModel, setSelectedRiskModel] = useState(null);
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
      const data = await optimize(selectedPicker, selectedRiskModel);
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
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
        runOptimize,
        loading,
        error,
        result,
      }}
    >
      {children}
    </PortfolioContext.Provider>
  );
}