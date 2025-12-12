/**
 * Predictions Page
 * 
 * ML predictions for stock prices.
 */

import { useState, useEffect } from 'react';
import { useCompanies } from '../../hooks/useCompanies';
import { predictionsApi } from '../../services/api';
import { cleanSymbol, formatCurrency, formatPercent, getChangeColor } from '../../utils/formatters';
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
import { useTheme } from '../../context/ThemeContext';
import { LoadingChart } from '../../components/common/Loading';
import './Predictions.css';

function Predictions() {
 const { companies } = useCompanies();
 const { theme } = useTheme();
 const [selectedStock, setSelectedStock] = useState('');
 const [prediction, setPrediction] = useState(null);
 const [loading, setLoading] = useState(false);
 const [error, setError] = useState(null);

 useEffect(() => {
  if (!selectedStock) {
   setPrediction(null);
   return;
  }

  const fetchPrediction = async () => {
   try {
    setLoading(true);
    setError(null);
    const response = await predictionsApi.predict(selectedStock);
    setPrediction(response.data);
   } catch (err) {
    setError('Failed to generate prediction. Model may need training.');
    setPrediction(null);
   } finally {
    setLoading(false);
   }
  };

  fetchPrediction();
 }, [selectedStock]);

 const chartData = prediction ? prediction.dates.map((date, i) => ({
  date,
  predicted: prediction.predictions[i],
  lower: prediction.confidence.lower[i],
  upper: prediction.confidence.upper[i]
 })) : [];

 const colors = {
  primary: theme === 'dark' ? '#6366f1' : '#4f46e5',
  confidence: theme === 'dark' ? 'rgba(99,102,241,0.2)' : 'rgba(79,70,229,0.15)',
  grid: theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
  text: theme === 'dark' ? '#a0a0b0' : '#475569'
 };

 return (
  <div className="predictions-page">
   <div className="page-header">
    <h1>ML Prediction</h1>
   </div>

   <div className="stock-selector-single">
    <label>Select Stock</label>
    <select value={selectedStock} onChange={(e) => setSelectedStock(e.target.value)}>
     <option value="">Choose a stock</option>
     {companies.map(c => (
      <option key={c.symbol} value={c.symbol}>
       {cleanSymbol(c.symbol)} - {c.name}
      </option>
     ))}
    </select>
   </div>

   {loading && <LoadingChart />}

   {error && (
    <div className="prediction-error">
     <p>{error}</p>
    </div>
   )}

   {prediction && !loading && (
    <div className="prediction-results animate-fadeIn">
     <div className="prediction-summary">
      <div className="summary-item">
       <span className="label">Current Price</span>
       <span className="value">{formatCurrency(prediction.current_price)}</span>
      </div>
      <div className="summary-item">
       <span className="label">Predicted (7 days)</span>
       <span className="value">{formatCurrency(prediction.summary.expected_price)}</span>
      </div>
      <div className="summary-item">
       <span className="label">Expected Return</span>
       <span className={`value ${getChangeColor(prediction.summary.expected_return)}`}>
        {formatPercent(prediction.summary.expected_return)}
       </span>
      </div>
      <div className="summary-item">
       <span className="label">Trend</span>
       <span className={`value trend-${prediction.summary.trend}`}>
        {prediction.summary.trend.charAt(0).toUpperCase() + prediction.summary.trend.slice(1)}
       </span>
      </div>
     </div>

     <div className="prediction-chart">
      <h3>7-Day Price Forecast</h3>
      <ResponsiveContainer width="100%" height={300}>
       <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
        <defs>
         <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
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
        />
        <YAxis
         domain={['auto', 'auto']}
         tick={{ fill: colors.text, fontSize: 11 }}
         width={60}
        />
        <Tooltip
         contentStyle={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-color)',
          borderRadius: '8px'
         }}
        />
        <Area
         type="monotone"
         dataKey="upper"
         stroke="transparent"
         fill={colors.confidence}
        />
        <Area
         type="monotone"
         dataKey="lower"
         stroke="transparent"
         fill="var(--bg-primary)"
        />
        <Line
         type="monotone"
         dataKey="predicted"
         stroke={colors.primary}
         strokeWidth={2}
         dot={{ fill: colors.primary, r: 4 }}
        />
       </AreaChart>
      </ResponsiveContainer>
      <p className="chart-note">Shaded area represents 95% confidence interval</p>
     </div>
    </div>
   )}


  </div>
 );
}

export default Predictions;
