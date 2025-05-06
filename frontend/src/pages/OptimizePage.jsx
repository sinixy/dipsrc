import React from 'react';
import { PortfolioContext } from '../context/PortfolioContext';

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
import { DrawdownChart } from '../components/DrawdownChart';
import { Heatmap } from '../components/Heatmap';


export default function OptimizePage() {
  const { result, error, chartData, chartLoading, chartError } = React.useContext(PortfolioContext);

  const chartKey = React.useMemo(() => {
    if (!chartData) return 'no-data';
    // Create a simple unique identifier when data is present
    // Using dates[0] as a proxy for dataset change. Could use a timestamp or hash.
    return chartData.dates && chartData.dates.length > 0 ? chartData.dates[0] : Date.now();
  }, [chartData]);

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
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">

            {/* Chart Loading/Error State */}
            {chartLoading && <div className="lg:col-span-2 text-center p-4">Loading charts...</div>}
            {chartError && <div className="lg:col-span-2 text-red-500 p-4">Error loading charts: {chartError}</div>}

            {/* Render charts if data is available */}
            {chartData && !chartLoading && !chartError && (
              <React.Fragment key={chartKey}> {/* Add React.Fragment with key */}
                <div>
                  <h2 className="text-lg font-semibold mb-2">Equity Curve</h2>
                  <EquityCurveChart dates={chartData.dates} equity={chartData.equity} />
                </div>
                <div>
                  <h2 className="text-lg font-semibold mb-2">Drawdown</h2>
                  <DrawdownChart dates={chartData.dates} drawdowns={chartData.drawdown} />
                </div>
                <div>
                  <h2 className="text-lg font-semibold mb-2">Sector Distribution</h2>
                  <SectorBarChart sectorLabels={chartData.sector_labels} sectorWeights={chartData.sector_weights} />
                </div>
                {/* <div>
                  <h2 className="text-lg font-semibold mb-2">Correlation Heatmap</h2>
                  <Heatmap labels={chartData.tickers} dataPoints={chartData.heatmap_data_points} />
                </div> */}
              </React.Fragment>
            )}
          </div>

          {result.stats && (
              <div className="mt-6">
                  <h2 className="text-lg font-semibold mb-2">Statistics</h2>
                  <StatsPanel /> {/* Keep as is, it uses context internally for result.stats */}
              </div>
           )}
        </>
      )}
    </div>
  );
}