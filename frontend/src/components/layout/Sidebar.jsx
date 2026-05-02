/**
 * Sidebar Component
 * 
 * Displays list of companies with search functionality.
 */

import { useState, useMemo } from 'react';
import { useCompanies } from '../../hooks/useCompanies';
import { useStock } from '../../context/StockContext';
import { formatPercent, getChangeColor, cleanSymbol } from '../../utils/formatters';
import SearchBar from '../controls/SearchBar';
import Loading from '../common/Loading';
import './Sidebar.css';

function Sidebar() {
 const { companies, loading, error } = useCompanies();
 const { selectedStock, selectStock, compareMode } = useStock();
 const [search, setSearch] = useState('');

 const filteredCompanies = useMemo(() => {
  if (!search) return companies;
  const term = search.toLowerCase();
  return companies.filter(c =>
   c.symbol.toLowerCase().includes(term) ||
   c.name.toLowerCase().includes(term)
  );
 }, [companies, search]);

 if (loading) {
  return (
   <aside className="sidebar">
    <div className="sidebar-header">
     <h2>Companies</h2>
    </div>
    <Loading count={10} />
   </aside>
  );
 }

 if (error) {
  return (
   <aside className="sidebar">
    <div className="sidebar-header">
     <h2>Companies</h2>
    </div>
    <div className="sidebar-error">
     <p>Failed to load companies</p>
     <button className="btn btn-secondary" onClick={() => window.location.reload()}>
      Retry
     </button>
    </div>
   </aside>
  );
 }

 return (
  <aside className="sidebar">
   <div className="sidebar-header">
    <h2>Companies</h2>
    {compareMode && <span className="compare-badge">Compare Mode</span>}
   </div>

   <div className="sidebar-search">
    <SearchBar
     value={search}
     onChange={setSearch}
     placeholder="Search stocks..."
    />
   </div>

   <div className="company-list">
    {filteredCompanies.map(company => (
     <button
      key={company.symbol}
      className={`company-item ${selectedStock?.symbol === company.symbol ? 'active' : ''}`}
      onClick={() => selectStock(company)}
     >
      <div className="company-info">
       <span className="company-symbol">{cleanSymbol(company.symbol)}</span>
       <span className="company-name">{company.name}</span>
      </div>
      <div className="company-price">
       {company.current_price && (
        <>
         <span className="price">{company.current_price.toFixed(2)}</span>
         <span className={`change ${getChangeColor(company.daily_change)}`}>
          {formatPercent(company.daily_change)}
         </span>
        </>
       )}
      </div>
     </button>
    ))}
   </div>
  </aside>
 );
}

export default Sidebar;
