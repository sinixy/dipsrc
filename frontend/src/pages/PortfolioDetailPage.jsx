import React from 'react';
import { useParams } from 'react-router-dom';
import TickerCardsGrid from '../components/TickerCardsGrid';
import { usePortfolioDetail, PortfolioDetailProvider } from '../context/PortfolioDetailContext';

import EquityCurveChart from '../components/EquityCurveChart';
import SectorBarChart from '../components/SectorBarChart';
import { DrawdownChart } from '../components/DrawdownChart';
import { Heatmap } from '../components/Heatmap';

function DetailContent() {
  const {
    originalPortfolio: ptf,
    reminders,
    loadingReminders,
    errorReminders,
    toggleReminder,
    rebalanceMethods,
    rebalanceParams: rb,
    setRebalanceParams,
    proposedAllocation,
    isRebalancing,
    isAccepting,
    runRebalance,
    acceptRebalance,
    cancelRebalance,
    chartData,
    chartLoading,
    chartError
  } = usePortfolioDetail();

  if (!ptf) return <div>Loading portfolio...</div>;
  const displayAllocation = proposedAllocation || ptf.allocation;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">{ptf.name || ptf._id}</h1>
      <div>Created at: {new Date(ptf.created_at).toLocaleString()}</div>
      <div>Snapshot date: {new Date(ptf.end_date).toLocaleDateString()}</div>
      <div>Capital: ${ptf.capital.toLocaleString()}</div>
      <div>Model: {ptf.model}</div>
      <div>Optimizer: {ptf.optimizer}</div>
      <div>Notes: {ptf.notes}</div>
      <h2 className="text-xl font-semibold mt-4">Stocks</h2>
      {!proposedAllocation && (
        <TickerCardsGrid allocation={displayAllocation} tickers={ptf.tickers} />
      )}

      <div className="border p-4 rounded bg-gray-50 bg-gray-700 text-gray-200 space-y-2">
        <h3 className="font-semibold">Rebalance</h3>
        <div className="flex flex-wrap gap-4 items-center">
          <select
            className="border p-2 rounded"
            value={rb.method}
            onChange={e => setRebalanceParams({...rb, method: e.target.value})}
          >
            <option className="text-gray-600 font-semibold" value="" disabled>Select method</option>
            {rebalanceMethods.map(m => (
              <option className="text-gray-600" key={m} value={m}>{m.replace('_', ' ')}</option>
            ))}
          </select>
          <input
            type="number"
            className="border p-1 rounded w-32"
            value={rb.capital}
            onChange={e => setRebalanceParams({...rb, capital: Number(e.target.value)})}
          />
          <input
            type="date"
            className="border p-1 rounded"
            value={rb.asOf}
            onChange={e => setRebalanceParams({...rb, asOf: e.target.value})}
          />
          <button
            className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
            onClick={runRebalance}
            disabled={isRebalancing}
          >{isRebalancing ? 'Rebalancing...' : 'Run'}</button>
        </div>
      </div>

      {proposedAllocation && (
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <h3 className="font-semibold mb-2">Current</h3>
            <TickerCardsGrid allocation={ptf.allocation} tickers={ptf.tickers} />
          </div>

          <div class="inline-block min-h-[1em] w-0.5 self-stretch bg-neutral-100 dark:bg-black/50"></div>

          <div className="flex-1">
            <h3 className="font-semibold mb-2">Proposed</h3>
            <TickerCardsGrid allocation={proposedAllocation} tickers={ptf.tickers} />
            <div className="mt-4 flex space-x-5">
              <button
                className="bg-green-600 text-white px-4 py-2 rounded disabled:opacity-50"
                onClick={acceptRebalance}
                disabled={isAccepting}
              >{isAccepting ? 'Applying...' : 'Accept'}</button>
              <button className="px-4 py-2 rounded border" onClick={cancelRebalance}>Cancel</button>
            </div>
          </div>
        </div>
      )}

<div className="mt-8 pt-6 border-t"> {/* Add separator */}
        <h2 className="text-xl font-semibold mb-4">Portfolio Analysis (as of {new Date(ptf.end_date).toLocaleDateString()})</h2>

        {/* Chart Loading/Error State */}
        {chartLoading && <div className="text-center p-4">Loading charts...</div>}
        {chartError && <div className="text-red-500 p-4">Error loading charts: {chartError}</div>}

        {/* Render charts grid if data is available */}
        {chartData && !chartLoading && !chartError && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold mb-2">Equity Curve</h3>
              <EquityCurveChart dates={chartData.dates} equity={chartData.equity} />
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">Drawdown</h3>
              <DrawdownChart dates={chartData.dates} drawdowns={chartData.drawdown} />
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">Sector Distribution</h3>
              <SectorBarChart sectorLabels={chartData.sector_labels} sectorWeights={chartData.sector_weights} />
            </div>
            {/* <div>
              <h3 className="text-lg font-semibold mb-2">Correlation Heatmap</h3>
              <Heatmap labels={chartData.tickers} dataPoints={chartData.heatmap_data_points} />
            </div> */}
          </div>
        )}
         {!chartData && !chartLoading && !chartError && (
             <div className="text-center text-gray-500 p-4">Chart data could not be generated for this portfolio.</div>
         )}
      </div>

      <div>
        <h2 className="text-xl font-semibold mt-4">Reminders</h2>
        {loadingReminders && <div>Loading reminders...</div>}
        {errorReminders && <div className="text-red-500">{errorReminders}</div>}
        {!loadingReminders && (
          <div className="space-y-2">
            {['daily', 'weekly', 'quarterly'].map(type => (
              <label key={type} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={reminders[type]?.active || false}
                  onChange={() => toggleReminder(type)}
                  className="form-checkbox h-5 w-5"
                />
                <span className="capitalize">{type} reminder</span>
              </label>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}

export default function PortfolioDetailPage() {
  const { id } = useParams();
  return (
    <PortfolioDetailProvider portfolioId={id}>
      <DetailContent />
    </PortfolioDetailProvider>
  );
}