/**
 * Application constants
 */

export const TIME_RANGES = [
 { label: '7D', value: 7 },
 { label: '30D', value: 30 },
 { label: '90D', value: 90 },
 { label: '1Y', value: 365 }
];

export const CHART_COLORS = {
 primary: '#6366f1',
 secondary: '#8b5cf6',
 success: '#22c55e',
 danger: '#ef4444',
 warning: '#f59e0b',
 info: '#3b82f6'
};

export const NAVIGATION = [
 { path: '/', label: 'Dashboard', icon: 'chart' },
 { path: '/compare', label: 'Compare', icon: 'compare' },
 { path: '/predictions', label: 'Predictions', icon: 'predict' },
 { path: '/correlation', label: 'Correlation', icon: 'matrix' }
];
