import React from 'react';
import { ToastContainer } from 'react-toastify';
import { PortfolioProvider, PortfolioContext } from './context/PortfolioContext';
import ModelPickerDropdown from './components/ModelPickerDropdown';
import RiskModelDropdown from './components/RiskModelDropdown';
import DatePicker from './components/DatePicker';
import CapitalInput from './components/CapitalInput';
import OptimizeButton from './components/OptimizeButton';
import StatsPanel from './components/StatsPanel';
import EquityCurveChart from './components/EquityCurveChart';
import SectorBarChart from './components/SectorBarChart';
import TickerCardsGrid from './components/TickerCardsGrid';
import SavePortfolio from './components/SavePortfolio';

export default function App() {
  const Dashboard = () => {
    const { result, error } = React.useContext(PortfolioContext);
    if (error) return <div className="text-red-500">Error: {error}</div>;
    if (!result) return null;
    return (
      <>
        <TickerCardsGrid />
        <SavePortfolio />
        <div className="space-y-6 mt-6">
          <div>
            <h2 className="text-lg font-semibold mb-2">Equity Curve</h2>
            <EquityCurveChart />
          </div>
          <div>
            <h2 className="text-lg font-semibold mb-2">Sector Distribution</h2>
            <SectorBarChart />
          </div>
          <div>
            <h2 className="text-lg font-semibold mb-2">Statistics</h2>
            <StatsPanel />
          </div>
        </div>
      </>
    );
  };

  return (
    <PortfolioProvider>
      <div className="p-4 space-y-4">
        <div className="flex flex-wrap gap-4 items-center">
          <ModelPickerDropdown />
          <RiskModelDropdown />
          <CapitalInput />
          <OptimizeButton />
          <DatePicker />
        </div>
        <Dashboard />
        <ToastContainer position="top-center" />
      </div>
    </PortfolioProvider>
  );
}
