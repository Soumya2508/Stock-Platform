/**
 * Header Component
 * 
 * Top navigation bar with logo, navigation links, and theme toggle.
 */

import { Link, useLocation } from 'react-router-dom';
import { useTheme } from '../../context/ThemeContext';
import ThemeToggle from '../controls/ThemeToggle';
import './Header.css';

function Header() {
 const { theme } = useTheme();
 const location = useLocation();

 const navLinks = [
  { path: '/', label: 'Dashboard' },
  { path: '/compare', label: 'Compare' },
  { path: '/predictions', label: 'ML Prediction' },
  { path: '/correlation', label: 'Correlation' }
 ];

 return (
  <header className="header">
   <div className="header-content">
    <div className="header-left">
     <Link to="/" className="logo">
      <span className="logo-icon">S</span>
      <span className="logo-text">Stock Intelligence</span>
     </Link>

     <nav className="nav-links">
      {navLinks.map(link => (
       <Link
        key={link.path}
        to={link.path}
        className={`nav-link ${location.pathname === link.path ? 'active' : ''}`}
       >
        {link.label}
       </Link>
      ))}
     </nav>
    </div>

    <div className="header-right">
     <ThemeToggle />
    </div>
   </div>
  </header>
 );
}

export default Header;
