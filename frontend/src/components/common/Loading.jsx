/**
 * Loading Component
 * 
 * Skeleton loading placeholders.
 */

import './Loading.css';

function Loading({ count = 5 }) {
 return (
  <div className="loading-container">
   {Array.from({ length: count }).map((_, i) => (
    <div key={i} className="skeleton-item">
     <div className="skeleton skeleton-text"></div>
     <div className="skeleton skeleton-text short"></div>
    </div>
   ))}
  </div>
 );
}

export function LoadingCard() {
 return (
  <div className="card loading-card">
   <div className="skeleton skeleton-title"></div>
   <div className="skeleton skeleton-text"></div>
   <div className="skeleton skeleton-text short"></div>
  </div>
 );
}

export function LoadingChart() {
 return (
  <div className="loading-chart">
   <div className="skeleton skeleton-chart"></div>
  </div>
 );
}

export default Loading;
