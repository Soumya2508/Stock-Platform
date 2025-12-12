/**
 * TimeFilter Component
 * 
 * Button group for selecting time range.
 */

import { useStock } from '../../context/StockContext';
import { TIME_RANGES } from '../../utils/constants';
import './TimeFilter.css';

function TimeFilter() {
 const { timeRange, setTimeRange } = useStock();

 return (
  <div className="time-filter">
   {TIME_RANGES.map(range => (
    <button
     key={range.value}
     className={`time-btn ${timeRange === range.value ? 'active' : ''}`}
     onClick={() => setTimeRange(range.value)}
    >
     {range.label}
    </button>
   ))}
  </div>
 );
}

export default TimeFilter;
