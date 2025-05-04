import React, { createContext, useState, useEffect, useContext } from 'react';
import { getPortfolioById, getReminders, updateReminder, rebalancePortfolio, updatePortfolio, fetchRiskModels } from '../api';
import { toast } from 'react-toastify';

const PortfolioDetailContext = createContext();
export function usePortfolioDetail() { return useContext(PortfolioDetailContext); }

export function PortfolioDetailProvider({ portfolioId, children }) {
  const [originalPortfolio, setOriginalPortfolio] = useState(null);
  const [reminders, setReminders] = useState({});
  const [loadingReminders, setLoadingReminders] = useState(false);
  const [errorReminders, setErrorReminders] = useState(null);

  const [rebalanceMethods, setRebalanceMethods] = useState([]);
  const [rebalanceParams, setRebalanceParams] = useState({ method: '', capital: null, asOf: '' });
  const [proposedAllocation, setProposedAllocation] = useState(null);
  const [isRebalancing, setIsRebalancing] = useState(false);
  const [isAccepting, setIsAccepting] = useState(false);

  // load portfolio and reminders
  useEffect(() => {
    getPortfolioById(portfolioId).then(ptf => {
      setOriginalPortfolio(ptf);
      setRebalanceParams({ method: ptf.optimizer, capital: ptf.capital, asOf: ptf.end_date.slice(0,10) });
    });
    setLoadingReminders(true);
    getReminders(portfolioId)
      .then(list => list.reduce((acc, r) => { acc[r.type] = r; return acc; }, {}))
      .then(map => setReminders(map))
      .catch(e => setErrorReminders(e.message))
      .finally(() => setLoadingReminders(false));

    fetchRiskModels()
      .then(setRebalanceMethods)
      .catch(e => console.error('Failed to load methods', e));
  }, [portfolioId]);

  const toggleReminder = async (type) => {
    const rem = reminders[type];
    if (!rem) return;
    try {
      const updated = await updateReminder(portfolioId, rem.id || rem._id, !rem.active);
      setReminders(prev => ({ ...prev, [type]: updated }));
    } catch (e) {
      toast.error(`Could not update ${type} reminder: ${e.message}`);
    }
  };

  const runRebalance = async () => {
    const { method, capital, asOf } = rebalanceParams;
    setIsRebalancing(true);
    try {
      const res = await rebalancePortfolio(portfolioId, method, capital, asOf);
      setProposedAllocation(res.allocation);
    } catch(e) {
      toast.error(e.message);
    } finally {
      setIsRebalancing(false);
    }
  };

  const acceptRebalance = async () => {
    if (!proposedAllocation) return;
    setIsAccepting(true);
    try {
      const payload = { allocation: proposedAllocation, capital: rebalanceParams.capital, end_date: rebalanceParams.asOf };
      const updated = await updatePortfolio(portfolioId, payload);
      setOriginalPortfolio(updated);
      setProposedAllocation(null);
      toast.success('Rebalance accepted');
    } catch(e) {
      toast.error(e.message);
    } finally {
      setIsAccepting(false);
    }
  };

  const cancelRebalance = () => setProposedAllocation(null);

  return (
    <PortfolioDetailContext.Provider value={{
      originalPortfolio,
      reminders,
      loadingReminders,
      errorReminders,
      toggleReminder,
      rebalanceParams,
      rebalanceMethods,
      setRebalanceParams,
      proposedAllocation,
      isRebalancing,
      isAccepting,
      runRebalance,
      acceptRebalance,
      cancelRebalance
    }}>
      {children}
    </PortfolioDetailContext.Provider>
  );
}