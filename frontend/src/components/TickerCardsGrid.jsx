import React, { useContext } from 'react';
import { PortfolioContext } from '../context/PortfolioContext';

export default function TickerCardsGrid() {
  const { result, capital } = useContext(PortfolioContext);
  if (!result) return null;
  const { weights, tickers } = result;
  const sortedWeights = Object.fromEntries(Object.entries(weights).sort((a, b) => b[1] - a[1]));
  return (
    <div className="grid grid-cols-1 md:grid-cols-5 lg:grid-cols-7 gap-4">
      {Object.entries(sortedWeights).map(([ticker, wt]) => {
        const meta = tickers[ticker];
        if (!meta) return null;
        const price = meta.price;
        const allocated = capital * wt;
        const shares = Math.floor(allocated / price);
        if (shares == 0) return null;
        return (
          <div key={ticker} className="relative border rounded p-4 bg-white dark:bg-gray-800">
            <a
              href={`https://finviz.com/quote.ashx?t=${ticker}`}
              target="_blank"
              rel="noopener noreferrer"
              className="absolute top-2 right-2 text-blue-500 text-xs"
            >
              FinViz ↗
            </a>
            <div className="flex items-center space-x-2 mb-2 mt-2">
              <img src={`icons/${ticker}.png`} alt={ticker} className="h-6 w-6" />
              <div className="font-semibold dark:text-gray-200">{ticker} <span className="font-normal text-sm">- {meta.company}</span></div>
            </div>
            <div className="text-sm text-gray-200">{meta.sector}</div>
            <div className="mt-2 text-sm text-gray-400">Weight: {(wt * 100).toFixed(2)}%</div>
            <div className="text-sm text-gray-400">Allocated: ${allocated.toFixed(2)}</div>
            <div className="text-sm text-gray-400">Shares: {shares}</div>
            <div className="text-sm text-gray-400">Price: ${price.toFixed(2)}</div>
          </div>
        );
      })}
    </div>
  );
}