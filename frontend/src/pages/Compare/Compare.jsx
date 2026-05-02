/**
 * Compare Page
 * 
 * Stock comparison page with selector and comparison chart.
 */

import { useState } from 'react';
import { useCompanies } from '../../hooks/useCompanies';
import { useCompare } from '../../hooks/useCompare';
import CompareChart from '../../components/charts/CompareChart';
import { cleanSymbol } from '../../utils/formatters';
import { LoadingChart } from '../../components/common/Loading';
import './Compare.css';

function Compare() {
 const { companies } = useCompanies();
 const [stock1, setStock1] = useState('');
 const [stock2, setStock2] = useState('');

 const { comparison, loading, error } = useCompare(stock1, stock2);

 return (
  <div className="compare-page">
   <div className="page-header">
    <h1>Compare Stocks</h1>
   </div>

   <div className="stock-selectors">
    <div className="selector-group">
     <label>Stock 1</label>
     <select value={stock1} onChange={(e) => setStock1(e.target.value)}>
      <option value="">Select a stock</option>
      {companies.map(c => (
       <option key={c.symbol} value={c.symbol} disabled={c.symbol === stock2}>
        {cleanSymbol(c.symbol)} - {c.name}
       </option>
      ))}
     </select>
    </div>

    <div className="vs-badge">VS</div>

    <div className="selector-group">
     <label>Stock 2</label>
     <select value={stock2} onChange={(e) => setStock2(e.target.value)}>
      <option value="">Select a stock</option>
      {companies.map(c => (
       <option key={c.symbol} value={c.symbol} disabled={c.symbol === stock1}>
        {cleanSymbol(c.symbol)} - {c.name}
       </option>
      ))}
     </select>
    </div>
   </div>

   {loading && <LoadingChart />}
   {error && <p className="error-message">Failed to load comparison data</p>}
   {!loading && comparison && <CompareChart comparison={comparison} />}

   {(!stock1 || !stock2) && !loading && !comparison && (
    <div className="compare-hint">
     <p>Select two stocks above to see their performance comparison</p>
    </div>
   )}
  </div>
 );
}

export default Compare;
