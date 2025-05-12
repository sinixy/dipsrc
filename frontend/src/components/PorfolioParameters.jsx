import React from 'react';


export default function PortfolioParameters({ ptf }) {
  if (!ptf) {
    return <div className="text-gray-500 text-gray-400">No portfolio parameters available.</div>;
  }

  // Prepare the parameters in a structured format for easy mapping
  // We include formatting directly here
  const parameters = [
    {
      label: 'Created At',
      value: ptf.created_at ? new Date(ptf.created_at).toLocaleString() : 'N/A',
    },
    {
      label: 'Snapshot Date',
      value: ptf.end_date ? new Date(ptf.end_date).toLocaleDateString() : 'N/A',
    },
    {
      label: 'Initial Capital', // Changed label slightly for clarity
      value: ptf.capital ? `$${ptf.capital.toLocaleString()}` : 'N/A',
    },
    {
      label: 'Model',
      value: ptf.model || 'N/A', // Use || 'N/A' for potential missing strings
    },
    {
      label: 'Optimizer',
      value: ptf.optimizer || 'N/A',
    }
  ];

  return (
    <div className="container mx-auto px-4 py-4"> {/* Consistent container styling */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {parameters.map((param) => (
          <div key={param.label} className="border rounded-lg shadow-sm p-4 bg-white bg-gray-700">
            <div className="text-sm font-medium text-gray-600 text-gray-300">{param.label}</div>
            <div className="text-lg font-semibold text-gray-800 text-gray-200 mt-1">
              {param.value}
            </div>
          </div>
        ))}
        <div key="Notes" className="border rounded-lg shadow-sm p-4 bg-white bg-gray-700">
            <div className="text-sm font-medium text-gray-600 text-gray-300">Notes</div>
            <div className="text-sm text-gray-700 text-gray-200 mt-1">
                {ptf.notes || "None"}
            </div>
        </div>
      </div>
    </div>
  );
}