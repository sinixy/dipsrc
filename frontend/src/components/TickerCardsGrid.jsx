import React, { useContext } from 'react';
import { PortfolioContext } from '../context/PortfolioContext';

export default function TickerCardsGrid() {
  const { result, capital } = useContext(PortfolioContext);
  if (!result) return null;
  const { allocation, tickers } = result;
  const { stocks, total_capital, leftover_capital } = allocation;
  return (
    <div className="grid grid-cols-1 md:grid-cols-5 lg:grid-cols-7 gap-4">
      { stocks.map(stock => {
        const meta = tickers[stock.ticker];
        const ticker = stock.ticker;
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
            <div className="mt-2 text-sm text-gray-400">Weight: {(stock.weight * 100).toFixed(2)}%</div>
            <div className="text-sm text-gray-400">Allocated: ${stock.allocated.toFixed(2)}</div>
            <div className="text-sm text-gray-400">Shares: {stock.shares}</div>
            <div className="text-sm text-gray-400">Price: ${stock.price.toFixed(2)}</div>
          </div>
        );
      })}
    </div>
  );
}