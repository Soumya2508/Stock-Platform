/**
 * App Component
 * 
 * Main application wrapper with routing.
 */

import { Routes, Route } from 'react-router-dom';
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import MainContent from './components/layout/MainContent';
import Dashboard from './pages/Dashboard/Dashboard';
import Compare from './pages/Compare/Compare';
import Predictions from './pages/Predictions/Predictions';
import Correlation from './pages/Correlation/Correlation';
import './App.css';

function App() {
 return (
  <div className="app">
   <Header />
   <div className="app-body">
    <Sidebar />
    <MainContent>
     <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/compare" element={<Compare />} />
      <Route path="/predictions" element={<Predictions />} />
      <Route path="/correlation" element={<Correlation />} />
     </Routes>
    </MainContent>
   </div>
  </div>
 );
}

export default App;
