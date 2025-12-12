/**
 * Utility functions for formatting data
 */

/**
 * Format number with thousand separators
 */
export function formatNumber(value, decimals = 2) {
 if (value === null || value === undefined) return '-';
 return new Intl.NumberFormat('en-IN', {
  minimumFractionDigits: decimals,
  maximumFractionDigits: decimals
 }).format(value);
}

/**
 * Format number as currency (INR)
 */
export function formatCurrency(value) {
 if (value === null || value === undefined) return '-';
 return new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  minimumFractionDigits: 2
 }).format(value);
}

/**
 * Format percentage with sign
 */
export function formatPercent(value, decimals = 2) {
 if (value === null || value === undefined) return '-';
 const sign = value > 0 ? '+' : '';
 return `${sign}${value.toFixed(decimals)}%`;
}

/**
 * Format volume with K/M/B suffixes
 */
export function formatVolume(volume) {
 if (!volume) return '-';
 if (volume >= 1e9) return `${(volume / 1e9).toFixed(1)}B`;
 if (volume >= 1e6) return `${(volume / 1e6).toFixed(1)}M`;
 if (volume >= 1e3) return `${(volume / 1e3).toFixed(1)}K`;
 return volume.toString();
}

/**
 * Format date to readable string
 */
export function formatDate(dateStr) {
 if (!dateStr) return '-';
 const date = new Date(dateStr);
 return date.toLocaleDateString('en-IN', {
  day: 'numeric',
  month: 'short',
  year: 'numeric'
 });
}

/**
 * Get color class based on value
 */
export function getChangeColor(value) {
 if (value > 0) return 'text-success';
 if (value < 0) return 'text-danger';
 return 'text-secondary';
}

/**
 * Clean stock symbol for display
 */
export function cleanSymbol(symbol) {
 return symbol.replace('.NS', '');
}
