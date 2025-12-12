/**
 * CompareChart Component
 * 
 * Overlay chart for comparing two stocks' performance.
 */

import { useMemo } from 'react';
import {
 LineChart,
 Line,
 XAxis,
 YAxis,
 CartesianGrid,
 Tooltip,
 ResponsiveContainer,
 Legend
} from 'recharts';
import { useTheme } from '../../context/ThemeContext';
import { formatDate } from '../../utils/formatters';
import './CompareChart.css';

function CompareChart({ comparison }) {
 const { theme } = useTheme();

 const chartData = useMemo(() => {
  if (!comparison?.chart_data) return [];

  const { dates } = comparison.chart_data;
  const [symbol1, symbol2] = comparison.symbols;

  return dates.map((date, i) => ({
   date,
   [symbol1]: comparison.chart_data[symbol1][i],
   [symbol2]: comparison.chart_data[symbol2][i]
  }));
 }, [comparison]);

 const colors = {
  stock1: theme === 'dark' ? '#6366f1' : '#4f46e5',
  stock2: theme === 'dark' ? '#22c55e' : '#16a34a',
  grid: theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
  text: theme === 'dark' ? '#a0a0b0' : '#475569'
 };

 if (!comparison || !chartData.length) {
  return (
   <div className="compare-chart">
    <p className="chart-empty">Select two stocks to compare</p>
   </div>
  );
 }

 const [symbol1, symbol2] = comparison.symbols;

 const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
   return (
    <div className="chart-tooltip">
     <p className="tooltip-date">{formatDate(label)}</p>
     {payload.map((p, i) => (
      <p key={i} className="tooltip-value" style={{ color: p.stroke }}>
       {p.name.replace('.NS', '')}: {p.value?.toFixed(2)}%
      </p>
     ))}
    </div>
   );
  }
  return null;
 };

 return (
  <div className="compare-chart">
   <div className="chart-header">
    <h3>Performance Comparison</h3>
    <div className="compare-stats">
     <span className="correlation-badge">
      Correlation: {comparison.correlation.returns}
     </span>
    </div>
   </div>

   <div className="chart-container">
    <ResponsiveContainer width="100%" height={350}>
     <LineChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
      <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
      <XAxis
       dataKey="date"
       tick={{ fill: colors.text, fontSize: 11 }}
       tickFormatter={(val) => {
        const d = new Date(val);
        return `${d.getDate()}/${d.getMonth() + 1}`;
       }}
       interval="preserveStartEnd"
      />
      <YAxis
       tick={{ fill: colors.text, fontSize: 11 }}
       tickFormatter={(val) => `${val.toFixed(0)}%`}
       width={50}
      />
      <Tooltip content={<CustomTooltip />} />
      <Line
       type="monotone"
       dataKey={symbol1}
       stroke={colors.stock1}
       strokeWidth={2}
       dot={false}
       name={symbol1}
      />
      <Line
       type="monotone"
       dataKey={symbol2}
       stroke={colors.stock2}
       strokeWidth={2}
       dot={false}
       name={symbol2}
      />
     </LineChart>
    </ResponsiveContainer>
   </div>

   <div className="comparison-summary">
    <div className="summary-card" style={{ borderColor: colors.stock1 }}>
     <span className="summary-symbol">{symbol1.replace('.NS', '')}</span>
     <span className="summary-return" style={{ color: comparison.performance[symbol1].total_return >= 0 ? 'var(--success)' : 'var(--danger)' }}>
      {comparison.performance[symbol1].total_return >= 0 ? '+' : ''}{comparison.performance[symbol1].total_return}%
     </span>
    </div>
    <div className="summary-card" style={{ borderColor: colors.stock2 }}>
     <span className="summary-symbol">{symbol2.replace('.NS', '')}</span>
     <span className="summary-return" style={{ color: comparison.performance[symbol2].total_return >= 0 ? 'var(--success)' : 'var(--danger)' }}>
      {comparison.performance[symbol2].total_return >= 0 ? '+' : ''}{comparison.performance[symbol2].total_return}%
     </span>
    </div>
   </div>
  </div>
 );
}

export default CompareChart;
