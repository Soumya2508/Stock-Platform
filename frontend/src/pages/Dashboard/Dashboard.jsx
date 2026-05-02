/**
 * Dashboard Page
 * 
 * Main dashboard showing stock overview and selected stock details.
 */

import { useStock } from '../../context/StockContext';
import PriceChart from '../../components/charts/PriceChart';
import InsightsPanel from '../../components/cards/InsightsPanel';
import TopMovers from '../../components/cards/TopMovers';
import './Dashboard.css';

function Dashboard() {
 const { selectedStock } = useStock();

 return (
  <div className="dashboard">
   <div className="dashboard-header">
    <h1>Stock Intelligence Dashboard</h1>
    <p>Real-time analytics and insights for NSE stocks</p>
   </div>

   <div className="dashboard-layout">
    <div className="dashboard-main">
     {selectedStock ? (
      <div className="stock-detail animate-fadeIn">
       <PriceChart symbol={selectedStock.symbol} />
       <InsightsPanel symbol={selectedStock.symbol} />
      </div>
     ) : (
      <div className="welcome-section">
       <div className="welcome-card">
        <h2>Welcome</h2>
       </div>
      </div>
     )}
    </div>

    <div className="dashboard-sidebar">
     <TopMovers />
    </div>
   </div>
  </div>
 );
}

export default Dashboard;

