/**
 * MainContent Component
 * 
 * Wrapper for the main content area.
 */

import './MainContent.css';

function MainContent({ children }) {
 return (
  <main className="main-content">
   {children}
  </main>
 );
}

export default MainContent;
