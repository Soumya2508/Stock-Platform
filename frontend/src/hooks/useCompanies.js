/**
 * Custom hook for fetching company list
 */

import { useState, useEffect } from 'react';
import { companiesApi } from '../services/api';

export function useCompanies() {
 const [companies, setCompanies] = useState([]);
 const [loading, setLoading] = useState(true);
 const [error, setError] = useState(null);

 const fetchCompanies = async () => {
  try {
   setLoading(true);
   const response = await companiesApi.getAll();
   setCompanies(response.data.companies || []);
   setError(null);
  } catch (err) {
   setError(err.message || 'Failed to fetch companies');
  } finally {
   setLoading(false);
  }
 };

 useEffect(() => {
  fetchCompanies();
 }, []);

 return { companies, loading, error, refetch: fetchCompanies };
}
