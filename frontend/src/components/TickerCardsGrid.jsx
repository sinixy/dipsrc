// src/components/TickerCardsGrid.jsx
import React from 'react';

export default function TickerCardsGrid({ allocation, tickers = {} }) {
  if (!allocation?.stocks?.length) return null;
  const { stocks } = allocation;

  return (
    <div className="grid grid-cols-1 md:grid-cols-5 lg:grid-cols-7 gap-4">
      {stocks.map(stock => {
        const { ticker, weight, allocated, shares, price } = stock;
        const meta = tickers[ticker] || {};
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
              <img src={`${window.location.origin}/icons/${ticker}.png`} alt={ticker} className="h-6 w-6" />
              <div className="font-semibold dark:text-gray-200">
                {ticker}
                {meta.company && <span className="font-normal text-sm"> – {meta.company}</span>}
              </div>
            </div>
            {meta.sector && <div className="text-sm text-gray-400">{meta.sector}</div>}
            <div className="mt-2 text-sm text-gray-400">Weight: {(weight * 100).toFixed(2)}%</div>
            <div className="text-sm text-gray-400">Allocated: ${allocated.toFixed(2)}</div>
            <div className="text-sm text-gray-400">Shares: {shares}</div>
            <div className="text-sm text-gray-400">Price: ${price.toFixed(2)}</div>
          </div>
        );
      })}
    </div>
  );
}
