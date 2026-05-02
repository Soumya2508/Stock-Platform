/**
 * InsightsPanel Component
 * 
 * Displays stock insights including volatility, momentum, and trend.
 */

import { useStockSummary } from '../../hooks/useStockData';
import { formatNumber, formatCurrency, formatVolume } from '../../utils/formatters';
import StatsCard from './StatsCard';
import { LoadingCard } from '../common/Loading';
import './InsightsPanel.css';

function InsightsPanel({ symbol }) {
 const { summary, loading, error } = useStockSummary(symbol);

 if (loading) {
  return (
   <div className="insights-panel">
    <h3>Stock Insights</h3>
    <div className="insights-grid">
     <LoadingCard />
     <LoadingCard />
     <LoadingCard />
     <LoadingCard />
    </div>
   </div>
  );
 }

 if (error || !summary) {
  return (
   <div className="insights-panel">
    <h3>Stock Insights</h3>
    <p className="text-secondary">Unable to load insights</p>
   </div>
  );
 }

 const getVolatilityLabel = (v) => {
  if (v < 20) return 'Low';
  if (v < 50) return 'Moderate';
  return 'High';
 };

 const getTrendLabel = (t) => {
  if (t > 2) return 'Bullish';
  if (t < -2) return 'Bearish';
  return 'Neutral';
 };

 return (
  <div className="insights-panel">
   <h3>Stock Insights</h3>

   <div className="insights-grid">
    <StatsCard
     label="52W High"
     value={formatCurrency(summary.high_52w)}
    />
    <StatsCard
     label="52W Low"
     value={formatCurrency(summary.low_52w)}
    />
    <StatsCard
     label="Avg Volume"
     value={formatVolume(summary.avg_volume)}
    />
    <StatsCard
     label="Volatility"
     value={`${formatNumber(summary.volatility, 1)} (${getVolatilityLabel(summary.volatility)})`}
    />
    <StatsCard
     label="Momentum"
     value={formatNumber(summary.momentum, 2)}
     change={summary.momentum}
    />
    <StatsCard
     label="Trend"
     value={getTrendLabel(summary.trend_strength)}
     change={summary.trend_strength}
    />
   </div>
  </div>
 );
}

export default InsightsPanel;
