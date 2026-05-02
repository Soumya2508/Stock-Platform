/**
 * Custom hook for stock comparison
 */

import { useState, useEffect } from 'react';
import { compareApi } from '../services/api';

export function useCompare(symbol1, symbol2) {
 const [comparison, setComparison] = useState(null);
 const [loading, setLoading] = useState(false);
 const [error, setError] = useState(null);

 useEffect(() => {
  if (!symbol1 || !symbol2) {
   setComparison(null);
   return;
  }

  const fetchComparison = async () => {
   try {
    setLoading(true);
    const response = await compareApi.compare(symbol1, symbol2);
    setComparison(response.data);
    setError(null);
   } catch (err) {
    setError(err.message || 'Failed to compare stocks');
    setComparison(null);
   } finally {
    setLoading(false);
   }
  };

  fetchComparison();
 }, [symbol1, symbol2]);

 return { comparison, loading, error };
}

export function useCorrelationMatrix() {
 const [matrix, setMatrix] = useState(null);
 const [loading, setLoading] = useState(true);
 const [error, setError] = useState(null);

 useEffect(() => {
  const fetchMatrix = async () => {
   try {
    setLoading(true);
    const response = await compareApi.correlationMatrix();
    setMatrix(response.data);
    setError(null);
   } catch (err) {
    setError(err.message || 'Failed to fetch correlation matrix');
   } finally {
    setLoading(false);
   }
  };

  fetchMatrix();
 }, []);

 return { matrix, loading, error };
}
