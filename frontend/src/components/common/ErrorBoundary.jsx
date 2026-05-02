import React from 'react';

class ErrorBoundary extends React.Component {
 constructor(props) {
  super(props);
  this.state = { hasError: false, error: null };
 }

 static getDerivedStateFromError(error) {
  return { hasError: true, error };
 }

 componentDidCatch(error, errorInfo) {
  console.error('React Error Boundary caught an error:', error, errorInfo);
 }

 render() {
  if (this.state.hasError) {
   return (
    <div style={{
     padding: '2rem',
     textAlign: 'center',
     color: 'var(--text-primary)',
     background: 'var(--bg-primary)',
     height: '100vh',
     display: 'flex',
     flexDirection: 'column',
     alignItems: 'center',
     justifyContent: 'center'
    }}>
     <h2>Something went wrong</h2>
     <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
      {this.state.error?.message || 'An unexpected error occurred'}
     </p>
     <button
      onClick={() => window.location.reload()}
      style={{
       padding: '0.5rem 1rem',
       background: 'var(--accent-primary)',
       color: 'white',
       border: 'none',
       borderRadius: '4px',
       cursor: 'pointer'
      }}
     >
      Reload Page
     </button>
    </div>
   );
  }

  return this.props.children;
 }
}

export default ErrorBoundary;
