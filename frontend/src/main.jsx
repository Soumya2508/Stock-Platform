import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { ThemeProvider } from './context/ThemeContext'
import { StockProvider } from './context/StockContext'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
 <React.StrictMode>
  <BrowserRouter>
   <ThemeProvider>
    <StockProvider>
     <App />
    </StockProvider>
   </ThemeProvider>
  </BrowserRouter>
 </React.StrictMode>
)
