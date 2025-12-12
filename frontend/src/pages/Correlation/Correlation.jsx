/**
 * Correlation Page
 * 
 * Displays correlation matrix heatmap for all stocks.
 */

import CorrelationHeatmap from '../../components/charts/CorrelationHeatmap';
import './Correlation.css';

function Correlation() {
 return (
  <div className="correlation-page">
   <div className="page-header">
    <h1>Correlation Analysis</h1>
    <p>Understand how different stocks move together</p>
   </div>

   <CorrelationHeatmap />

   <div className="correlation-info">
    <h3>How to Read This Matrix</h3>
    <div className="info-grid">
     <div className="info-item">
      <span className="info-value positive">+1.0</span>
      <span className="info-desc">Perfect positive correlation - stocks move together</span>
     </div>
     <div className="info-item">
      <span className="info-value neutral">0.0</span>
      <span className="info-desc">No correlation - stocks move independently</span>
     </div>
     <div className="info-item">
      <span className="info-value negative">-1.0</span>
      <span className="info-desc">Perfect negative correlation - stocks move opposite</span>
     </div>
    </div>
   </div>
  </div>
 );
}

export default Correlation;
