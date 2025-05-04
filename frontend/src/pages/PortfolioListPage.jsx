import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getPortfolios } from '../api';

export default function PortfolioListPage() {
  const [list, setList] = useState([]);

  useEffect(() => {
    getPortfolios()
      .then(setList)
      .catch(console.error);
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">My Portfolios</h1>
      <div className="space-y-3">
        {list.map(p => (
          <div
            key={p._id}
            className="flex items-center justify-between bg-gray-800 dark:bg-gray-700 p-4 rounded"
          >
            <div>
              <Link
                to={`/portfolio/${p._id}`}
                className="text-white text-xl font-semibold hover:underline"
              >
                {p.name || p._id}
              </Link>
              <div className="text-gray-400 text-sm">
                {p.allocation.stocks.length || 0} stocks • Created: {new Date(p.created_at).toLocaleDateString()}
              </div>
            </div>
            <div className="text-gray-400 font-semibold text-lg">
              As of: {new Date(p.end_date).toLocaleDateString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}