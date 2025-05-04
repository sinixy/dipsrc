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
      <ul className="list-disc pl-5">
        {list.map(p => (
          <li key={p._id}>
            <Link to={`/portfolio/${p._id}`} className="text-blue-600 hover:underline">
              {p.name || p._id} — {new Date(p.end_date).toLocaleDateString()}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}