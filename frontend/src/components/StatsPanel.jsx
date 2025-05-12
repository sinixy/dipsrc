import React, { useState } from 'react';

export default function StatsPanel({ stats }) {
  const [showSecondary, setShowSecondary] = useState(false);

  // Define the list of primary metrics based on our previous discussion
  const primaryMetrics = [
    'Annualized Mean',
    'Annualized Standard Deviation',
    'Annualized Sharpe Ratio', // Assuming Annualized Sharpe Ratio is the preferred primary over non-annualized
    'Assets Number',
    'Value at Risk at 95%',
    'CVaR at 95%',
  ];

  // Filter stats into primary and secondary
  const primaryStats = {};
  const secondaryStats = {};

  if (stats) {
    Object.entries(stats).forEach(([label, value]) => {
      if (primaryMetrics.includes(label)) {
        primaryStats[label] = value;
      } else {
        secondaryStats[label] = value;
      }
    });
  }

  // Helper function to format values (optional but recommended for readability)
  const formatValue = (label, value) => {
    if (typeof value !== 'number') {
      return value; // Return non-numeric values as is
    }
    // Simple formatting based on potential metric types
    if (label.includes('Ratio') || label.includes('Skew') || label.includes('Kurtosis') || label.includes('Number')) {
         return value.toFixed(2); // Ratios, Shape metrics, Counts
    }
     if (label.includes('Drawdown') || label.includes('Risk') || label.includes('Variance') || label.includes('Deviation') || label.includes('Realization')) {
         return value.toFixed(4); // Risk/Volatility measures might need more precision
    }
    // Default formatting for percentages/decimals like Mean
     return value.toFixed(4); // Default to 4 decimal places
  };


  if (!stats) {
    return <div className="text-gray-500 text-gray-400">No stats available.</div>;
  }

  return (
    <div className="container mx-auto px-4 py-4"> {/* Add some padding around the panel */}

      {/* Primary Metrics Section */}
      <h2 className="text-xl font-bold mb-4 text-gray-800 text-gray-200">Key Performance & Risk</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8"> {/* Responsive grid for primary */}
        {Object.entries(primaryStats).map(([label, value]) => (
          <div key={label} className="border rounded-lg shadow-sm p-4 bg-white bg-gray-700"> {/* Enhanced card style */}
            <div className="text-sm font-medium text-gray-600 text-gray-300">{label}</div> {/* Slightly different text style */}
            <div className="text-2xl font-bold text-indigo-600 text-indigo-400 mt-1">{formatValue(label, value)}</div> {/* Larger, bolder text */}
          </div>
        ))}
      </div>

      {/* Secondary Metrics Section */}
      <div className="border-t pt-4 mt-4 border-gray-200 border-gray-600"> {/* Separator line */}
        <button
          className="flex justify-between items-center w-full text-left text-lg font-bold text-gray-800 text-gray-200 mb-4 focus:outline-none"
          onClick={() => setShowSecondary(!showSecondary)}
          aria-expanded={showSecondary}
        >
          Other Metrics
          <svg
            className={`w-5 h-5 transform transition-transform duration-200 ${showSecondary ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </button>

        {/* Collapsible Table for Secondary Metrics */}
        {showSecondary && (
          <div className="overflow-x-auto"> {/* Make table scrollable horizontally if needed */}
            <table className="min-w-full divide-y divide-gray-200 divide-gray-600">
              <thead className="bg-gray-50 bg-gray-600">
                <tr>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-300 text-gray-300 uppercase tracking-wider"
                  >
                    Metric
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-300 text-gray-300 uppercase tracking-wider"
                  >
                    Value
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white bg-gray-700 divide-y divide-gray-200 divide-gray-600">
                {Object.entries(secondaryStats).map(([label, value]) => (
                  <tr key={label}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 text-gray-100">{label}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                       <div className="text-sm text-gray-800 text-gray-200">{formatValue(label, value)}</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}