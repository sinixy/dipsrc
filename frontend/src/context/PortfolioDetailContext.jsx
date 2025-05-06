import React, { createContext, useState, useEffect, useContext } from 'react';
import {
  getPortfolioById, getReminders, updateReminder,
  rebalancePortfolio, updatePortfolio, fetchRiskModels, getChartData
} from '../api';
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

  const [chartData, setChartData] = useState(null);
  const [chartLoading, setChartLoading] = useState(true); // Start loading true
  const [chartError, setChartError] = useState(null);

  // load portfolio and reminders
  useEffect(() => {
    let isMounted = true; // Prevent state updates on unmounted component
    const loadData = async () => {
      try {
        // Fetch portfolio
        const ptf = await getPortfolioById(portfolioId);
        if (!isMounted) return;
        setOriginalPortfolio(ptf);
        setRebalanceParams({ method: ptf.optimizer, capital: ptf.capital, asOf: ptf.end_date.slice(0, 10) });

        // Fetch chart data once portfolio is loaded
        if (ptf && ptf.allocation && ptf.allocation.stocks && ptf.tickers) {
          setChartLoading(true);
          setChartError(null);
          try {
            const charts = await getChartData(ptf.allocation.stocks, ptf.tickers, ptf.end_date);
            if (isMounted) setChartData(charts);
          } catch (chartErr) {
             if (isMounted) setChartError(chartErr.message);
          } finally {
             if (isMounted) setChartLoading(false);
          }
        } else {
           if (isMounted) setChartLoading(false); // No data to fetch charts
        }

        // Fetch reminders (can run in parallel conceptually)
        setLoadingReminders(true);
        getReminders(portfolioId)
          .then(list => list.reduce((acc, r) => { acc[r.type] = r; return acc; }, {}))
          .then(map => { if (isMounted) setReminders(map); })
          .catch(e => { if (isMounted) setErrorReminders(e.message); })
          .finally(() => { if (isMounted) setLoadingReminders(false); });

        // Fetch risk models (can run in parallel)
        fetchRiskModels()
          .then(methods => { if (isMounted) setRebalanceMethods(methods); })
          .catch(e => console.error('Failed to load methods', e));

      } catch (error) {
        console.error("Failed to load portfolio details:", error);
        if (isMounted) {
          setChartError("Failed to load portfolio details."); // General error
          setChartLoading(false);
        }
      }
    };

    loadData();

    return () => { isMounted = false; }; // Cleanup function

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
      chartData,
      chartLoading,
      chartError,
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