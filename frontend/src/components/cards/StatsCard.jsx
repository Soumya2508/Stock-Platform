/**
 * StatsCard Component
 * 
 * Displays a single statistic with label and value.
 */

import { getChangeColor } from '../../utils/formatters';
import './StatsCard.css';

function StatsCard({ label, value, change, icon, variant = 'default' }) {
 return (
  <div className={`stats-card ${variant}`}>
   {icon && <div className="stats-icon">{icon}</div>}
   <div className="stats-content">
    <span className="stats-label">{label}</span>
    <span className="stats-value">{value}</span>
    {change !== undefined && (
     <span className={`stats-change ${getChangeColor(change)}`}>
      {change > 0 ? '+' : ''}{change}%
     </span>
    )}
   </div>
  </div>
 );
}

export default StatsCard;
