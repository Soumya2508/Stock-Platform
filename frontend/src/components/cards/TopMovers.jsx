/**
 * TopMovers Component
 * 
 * Displays top gainers and losers of the day.
 */

import { useState, useEffect } from 'react';
import { topMoversApi } from '../../services/api';
import { formatPercent, cleanSymbol } from '../../utils/formatters';
import './TopMovers.css';

function TopMovers() {
 const [data, setData] = useState(null);
 const [loading, setLoading] = useState(true);

 useEffect(() => {
  const fetchData = async () => {
   try {
    const response = await topMoversApi.get();
    setData(response.data);
   } catch (err) {
    console.error('Failed to load top movers:', err);
   } finally {
    setLoading(false);
   }
  };
  fetchData();
 }, []);

 if (loading) {
  return (
   <div className="top-movers">
    <h3>Top Movers</h3>
    <div className="movers-loading">Loading...</div>
   </div>
  );
 }

 if (!data) return null;

 return (
  <div className="top-movers">
   <h3>Top Movers</h3>

   <div className="movers-section">
    <h4 className="gainers-title">Top Gainers</h4>
    <div className="movers-list">
     {(data.gainers || []).map(stock => (
      <div key={stock.symbol} className="mover-item gainer">
       <span className="mover-symbol">{cleanSymbol(stock.symbol)}</span>
       <span className="mover-change text-success">
        {formatPercent(stock.daily_change)}
       </span>
      </div>
     ))}
    </div>
   </div>

   <div className="movers-section">
    <h4 className="losers-title">Top Losers</h4>
    <div className="movers-list">
     {(data.losers || []).map(stock => (
      <div key={stock.symbol} className="mover-item loser">
       <span className="mover-symbol">{cleanSymbol(stock.symbol)}</span>
       <span className="mover-change text-danger">
        {formatPercent(stock.daily_change)}
       </span>
      </div>
     ))}
    </div>
   </div>
  </div>
 );
}

export default TopMovers;
