import React from 'react';
import { PortfolioProvider, PortfolioContext } from './context/PortfolioContext';
import ModelPickerDropdown from './components/ModelPickerDropdown';
import RiskModelDropdown from './components/RiskModelDropdown';
import OptimizeButton from './components/OptimizeButton';
import EquityCurveChart from './components/EquityCurveChart';
import SectorBarChart from './components/SectorBarChart';
import StatsPanel from './components/StatsPanel';

export default function App() {
  const Dashboard = () => {
    const { result, error } = React.useContext(PortfolioContext);
    if (error) return <div className="text-red-500">Error: {error}</div>;
    if (!result) return null;
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-lg font-semibold mb-2">Statistics</h2>
          <StatsPanel />
        </div>
        <div>
          <h2 className="text-lg font-semibold mb-2">Equity Curve</h2>
          <EquityCurveChart />
        </div>
        <div>
          <h2 className="text-lg font-semibold mb-2">Sector Distribution</h2>
          <SectorBarChart />
        </div>
      </div>
    );
  };

  return (
    <PortfolioProvider>
      <div className="p-4 space-y-4">
        <div className="flex flex-wrap gap-4 items-center">
          <ModelPickerDropdown />
          <RiskModelDropdown />
          <OptimizeButton />
        </div>
        <Dashboard />
      </div>
    </PortfolioProvider>
  );
}