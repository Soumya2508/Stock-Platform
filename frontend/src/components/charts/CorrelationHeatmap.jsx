/**
 * CorrelationHeatmap Component
 * 
 * Heatmap visualization of stock correlations.
 */

import { useMemo } from 'react';
import { useCorrelationMatrix } from '../../hooks/useCompare';
import { cleanSymbol } from '../../utils/formatters';
import { LoadingChart } from '../common/Loading';
import './CorrelationHeatmap.css';

function CorrelationHeatmap() {
 const { matrix, loading, error } = useCorrelationMatrix();

 const getColor = (value) => {
  // Color scale from red (-1) through white (0) to green (+1)
  if (value >= 0.7) return 'hsl(142, 70%, 35%)';
  if (value >= 0.4) return 'hsl(142, 50%, 45%)';
  if (value >= 0.1) return 'hsl(142, 30%, 55%)';
  if (value >= -0.1) return 'hsl(0, 0%, 50%)';
  if (value >= -0.4) return 'hsl(0, 30%, 55%)';
  if (value >= -0.7) return 'hsl(0, 50%, 45%)';
  return 'hsl(0, 70%, 35%)';
 };

 if (loading) {
  return (
   <div className="correlation-heatmap">
    <h3>Correlation Matrix</h3>
    <LoadingChart />
   </div>
  );
 }

 if (error || !matrix) {
  return (
   <div className="correlation-heatmap">
    <h3>Correlation Matrix</h3>
    <p className="heatmap-error">Failed to load correlation data</p>
   </div>
  );
 }

 return (
  <div className="correlation-heatmap">
   <h3>Correlation Matrix (Daily Returns)</h3>

   <div className="heatmap-container">
    <table className="heatmap-table">
     <thead>
      <tr>
       <th></th>
       {matrix.symbols.map(sym => (
        <th key={sym}>{cleanSymbol(sym)}</th>
       ))}
      </tr>
     </thead>
     <tbody>
      {matrix.symbols.map((rowSym, i) => (
       <tr key={rowSym}>
        <td className="row-label">{cleanSymbol(rowSym)}</td>
        {matrix.matrix[i].map((value, j) => (
         <td
          key={j}
          className="heatmap-cell"
          style={{ backgroundColor: getColor(value) }}
          title={`${cleanSymbol(rowSym)} vs ${cleanSymbol(matrix.symbols[j])}: ${value.toFixed(2)}`}
         >
          {value.toFixed(2)}
         </td>
        ))}
       </tr>
      ))}
     </tbody>
    </table>
   </div>

   <div className="heatmap-legend">
    <span className="legend-label">-1 (Negative)</span>
    <div className="legend-gradient"></div>
    <span className="legend-label">+1 (Positive)</span>
   </div>
  </div>
 );
}

export default CorrelationHeatmap;
