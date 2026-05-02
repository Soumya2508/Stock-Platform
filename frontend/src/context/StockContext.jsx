/**
 * Stock Context
 * 
 * Manages global state for selected stock and comparison mode.
 */

import { createContext, useContext, useState } from 'react';

const StockContext = createContext();

export function StockProvider({ children }) {
 const [selectedStock, setSelectedStock] = useState(null);
 const [compareMode, setCompareMode] = useState(false);
 const [compareStocks, setCompareStocks] = useState([]);
 const [timeRange, setTimeRange] = useState(30); // days

 const selectStock = (stock) => {
  if (compareMode) {
   // In compare mode, add to comparison list
   if (compareStocks.length < 2 && !compareStocks.find(s => s.symbol === stock.symbol)) {
    setCompareStocks(prev => [...prev, stock]);
   }
  } else {
   setSelectedStock(stock);
  }
 };

 const clearSelection = () => {
  setSelectedStock(null);
  setCompareStocks([]);
 };

 const toggleCompareMode = () => {
  setCompareMode(prev => !prev);
  if (compareMode) {
   // Exiting compare mode
   setCompareStocks([]);
  }
 };

 const removeFromCompare = (symbol) => {
  setCompareStocks(prev => prev.filter(s => s.symbol !== symbol));
 };

 return (
  <StockContext.Provider value={{
   selectedStock,
   selectStock,
   clearSelection,
   compareMode,
   toggleCompareMode,
   compareStocks,
   removeFromCompare,
   timeRange,
   setTimeRange
  }}>
   {children}
  </StockContext.Provider>
 );
}

export function useStock() {
 const context = useContext(StockContext);
 if (!context) {
  throw new Error('useStock must be used within a StockProvider');
 }
 return context;
}
