/**
 * SearchBar Component
 * 
 * Search input for filtering companies.
 */

import './SearchBar.css';

function SearchBar({ value, onChange, placeholder = 'Search...' }) {
 return (
  <div className="search-bar">
   <svg className="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="11" cy="11" r="8" />
    <path d="m21 21-4.35-4.35" />
   </svg>
   <input
    type="text"
    value={value}
    onChange={(e) => onChange(e.target.value)}
    placeholder={placeholder}
    className="search-input"
   />
   {value && (
    <button className="search-clear" onClick={() => onChange('')}>
     <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
     </svg>
    </button>
   )}
  </div>
 );
}

export default SearchBar;
