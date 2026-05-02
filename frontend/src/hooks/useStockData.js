/**
 * Custom hook for fetching stock data
 */

import { useState, useEffect } from 'react';
import { stockDataApi } from '../services/api';

export function useStockData(symbol, days = 30) {
 const [data, setData] = useState(null);
 const [loading, setLoading] = useState(false);
 const [error, setError] = useState(null);

 useEffect(() => {
  if (!symbol) {
   setData(null);
   return;
  }

  const fetchData = async () => {
   try {
    setLoading(true);
    const response = await stockDataApi.getData(symbol, days);
    setData(response.data);
    setError(null);
   } catch (err) {
    setError(err.message || 'Failed to fetch stock data');
    setData(null);
   } finally {
    setLoading(false);
   }
  };

  fetchData();
 }, [symbol, days]);

 return { data, loading, error };
}

export function useStockSummary(symbol) {
 const [summary, setSummary] = useState(null);
 const [loading, setLoading] = useState(false);
 const [error, setError] = useState(null);

 useEffect(() => {
  if (!symbol) {
   setSummary(null);
   return;
  }

  const fetchSummary = async () => {
   try {
    setLoading(true);
    const response = await stockDataApi.getSummary(symbol);
    setSummary(response.data);
    setError(null);
   } catch (err) {
    setError(err.message || 'Failed to fetch summary');
    setSummary(null);
   } finally {
    setLoading(false);
   }
  };

  fetchSummary();
 }, [symbol]);

 return { summary, loading, error };
}
