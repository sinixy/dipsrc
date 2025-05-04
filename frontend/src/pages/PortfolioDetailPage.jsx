import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getPortfolioById, getReminders, updateReminder } from '../api';
import TickerCardsGrid from '../components/TickerCardsGrid';

export default function PortfolioDetailPage() {
  const { id } = useParams();
  const [portfolio, setPortfolio] = useState(null);
  const [reminders, setReminders] = useState({}); // map type -> reminder object
  const [loadingReminders, setLoadingReminders] = useState(false);
  const [errorReminders, setErrorReminders] = useState(null);

  useEffect(() => {
    getPortfolioById(id)
      .then(setPortfolio)
      .catch(console.error);

    setLoadingReminders(true);
    getReminders(id)
      .then(list => {
        const map = {};
        list.forEach(r => map[r.type] = r);
        setReminders(map);
      })
      .catch(e => setErrorReminders(e.message))
      .finally(() => setLoadingReminders(false));
  }, [id]);

  const handleToggle = async (type) => {
    const rem = reminders[type];
    if (!rem) return;
    const newActive = !rem.active;
    try {
      const updated = await updateReminder(id, rem._id || rem.id, newActive);
      setReminders(prev => ({ ...prev, [type]: updated }));
    } catch (e) {
      alert(`Could not update ${type} reminder: ${e.message}`);
    }
  };

  if (!portfolio) return <div>Loading...</div>;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">{portfolio.name || portfolio._id}</h1>
      <div>Created at: {new Date(portfolio.created_at).toLocaleString()}</div>
      <div>Snapshot date: {new Date(portfolio.end_date).toLocaleDateString()}</div>
      <div>Capital: ${portfolio.capital.toLocaleString()}</div>
      <div>Model: {portfolio.model}</div>
      <div>Optimizer: {portfolio.optimizer}</div>
      <div>Notes: {portfolio.notes}</div>
      <h2 className="text-xl font-semibold mt-4">Stocks</h2>
      <TickerCardsGrid
        allocation={portfolio.allocation}
        tickers={portfolio.tickers}
      />
      <div>
        <h2 className="text-xl font-semibold mt-4">Reminders</h2>
        {loadingReminders && <div>Loading reminders...</div>}
        {errorReminders && <div className="text-red-500">{errorReminders}</div>}
        {!loadingReminders && (
          <div className="space-y-2">
            {['daily', 'weekly', 'quarterly'].map(type => {
              const rem = reminders[type];
              return (
                <label key={type} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={rem?.active || false}
                    onChange={() => handleToggle(type)}
                    className="form-checkbox h-5 w-5"
                  />
                  <span className="capitalize">{type} reminder</span>
                </label>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}