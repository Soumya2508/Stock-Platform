/**
 * PriceChart Component
 * 
 * Interactive line chart for stock prices using Recharts.
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
 Area,
 AreaChart
} from 'recharts';
import { useStockData } from '../../hooks/useStockData';
import { useStock } from '../../context/StockContext';
import { useTheme } from '../../context/ThemeContext';
import { formatDate, formatCurrency } from '../../utils/formatters';
import TimeFilter from '../controls/TimeFilter';
import { LoadingChart } from '../common/Loading';
import './PriceChart.css';

function PriceChart({ symbol }) {
 const { timeRange } = useStock();
 const { theme } = useTheme();
 const { data, loading, error } = useStockData(symbol, timeRange);

 const chartData = useMemo(() => {
  if (!data?.data) return [];
  return data.data.map(d => ({
   date: d.date,
   close: d.close,
   ma7: d.ma_7,
   ma20: d.ma_20
  }));
 }, [data]);

 const colors = {
  primary: theme === 'dark' ? '#6366f1' : '#4f46e5',
  ma7: theme === 'dark' ? '#22c55e' : '#16a34a',
  ma20: theme === 'dark' ? '#f59e0b' : '#d97706',
  grid: theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
  text: theme === 'dark' ? '#a0a0b0' : '#475569',
  gradient: theme === 'dark' ? 'rgba(99,102,241,0.2)' : 'rgba(79,70,229,0.1)'
 };

 if (loading) {
  return (
   <div className="price-chart">
    <div className="chart-header">
     <h3>Price Chart</h3>
     <TimeFilter />
    </div>
    <LoadingChart />
   </div>
  );
 }

 if (error || !chartData.length) {
  return (
   <div className="price-chart">
    <div className="chart-header">
     <h3>Price Chart</h3>
     <TimeFilter />
    </div>
    <div className="chart-empty">
     <p>No data available</p>
    </div>
   </div>
  );
 }

 const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
   return (
    <div className="chart-tooltip">
     <p className="tooltip-date">{formatDate(label)}</p>
     <p className="tooltip-value">
      <span style={{ color: colors.primary }}>Price:</span> {formatCurrency(payload[0]?.value)}
     </p>
     {payload[1] && (
      <p className="tooltip-value">
       <span style={{ color: colors.ma7 }}>MA7:</span> {formatCurrency(payload[1]?.value)}
      </p>
     )}
     {payload[2] && (
      <p className="tooltip-value">
       <span style={{ color: colors.ma20 }}>MA20:</span> {formatCurrency(payload[2]?.value)}
      </p>
     )}
    </div>
   );
  }
  return null;
 };

 return (
  <div className="price-chart">
   <div className="chart-header">
    <div className="chart-title">
     <h3>{data.name}</h3>
     <span className="chart-symbol">{data.symbol}</span>
    </div>
    <TimeFilter />
   </div>

   <div className="chart-container">
    <ResponsiveContainer width="100%" height={350}>
     <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
      <defs>
       <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
        <stop offset="5%" stopColor={colors.primary} stopOpacity={0.3} />
        <stop offset="95%" stopColor={colors.primary} stopOpacity={0} />
       </linearGradient>
      </defs>
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
       domain={['auto', 'auto']}
       tick={{ fill: colors.text, fontSize: 11 }}
       tickFormatter={(val) => `${(val / 1000).toFixed(1)}K`}
       width={50}
      />
      <Tooltip content={<CustomTooltip />} />
      <Area
       type="monotone"
       dataKey="close"
       stroke={colors.primary}
       strokeWidth={2}
       fill="url(#colorClose)"
      />
      <Line
       type="monotone"
       dataKey="ma7"
       stroke={colors.ma7}
       strokeWidth={1.5}
       dot={false}
       strokeDasharray="5 5"
      />
      <Line
       type="monotone"
       dataKey="ma20"
       stroke={colors.ma20}
       strokeWidth={1.5}
       dot={false}
       strokeDasharray="5 5"
      />
     </AreaChart>
    </ResponsiveContainer>
   </div>

   <div className="chart-legend">
    <div className="legend-item">
     <span className="legend-color" style={{ background: colors.primary }}></span>
     <span>Close Price</span>
    </div>
    <div className="legend-item">
     <span className="legend-color dashed" style={{ background: colors.ma7 }}></span>
     <span>7-Day MA</span>
    </div>
    <div className="legend-item">
     <span className="legend-color dashed" style={{ background: colors.ma20 }}></span>
     <span>20-Day MA</span>
    </div>
   </div>
  </div>
 );
}

export default PriceChart;
