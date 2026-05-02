/**
 * Theme Context
 * 
 * Provides theme state (light/dark) across the application.
 * Persists theme preference in localStorage.
 */

import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
 const [theme, setTheme] = useState(() => {
  // Check localStorage first
  const saved = localStorage.getItem('theme');
  if (saved) return saved;

  // Check system preference
  if (window.matchMedia('(prefers-color-scheme: light)').matches) {
   return 'light';
  }
  return 'dark';
 });

 useEffect(() => {
  // Apply theme to document
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
 }, [theme]);

 const toggleTheme = () => {
  setTheme(prev => prev === 'dark' ? 'light' : 'dark');
 };

 return (
  <ThemeContext.Provider value={{ theme, toggleTheme }}>
   {children}
  </ThemeContext.Provider>
 );
}

export function useTheme() {
 const context = useContext(ThemeContext);
 if (!context) {
  throw new Error('useTheme must be used within a ThemeProvider');
 }
 return context;
}
