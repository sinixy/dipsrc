import React from 'react';
import ModelPickerDropdown from '../components/ModelPickerDropdown';
import RiskModelDropdown from '../components/RiskModelDropdown';
import DatePicker from '../components/DatePicker';
import CapitalInput from '../components/CapitalInput';
import OptimizeButton from '../components/OptimizeButton';
import TickerCardsGrid from '../components/TickerCardsGrid';
import SavePortfolio from '../components/SavePortfolio';
import StatsPanel from '../components/StatsPanel';
import EquityCurveChart from '../components/EquityCurveChart';
import SectorBarChart from '../components/SectorBarChart';
import { PortfolioContext } from '../context/PortfolioContext';

export default function OptimizePage() {
  const { result, error } = React.useContext(PortfolioContext);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-4 items-center w-full">
        <ModelPickerDropdown />
        <RiskModelDropdown />
        <CapitalInput />
        <OptimizeButton />
        <DatePicker />
      </div>

      {error && <div className="text-red-500">Error: {error}</div>}

      {result && (
        <>
          <TickerCardsGrid allocation={result.allocation} tickers={result.tickers} />
          <SavePortfolio />
          <div className="space-y-6 mt-6">
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
        </>
      )}
    </div>
  );
}