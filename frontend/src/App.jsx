import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import { PortfolioProvider } from './context/PortfolioContext';
import NavBar from './components/NavBar';
import OptimizePage from './pages/OptimizePage';
import PortfolioListPage from './pages/PortfolioListPage';
import PortfolioDetailPage from './pages/PortfolioDetailPage';
import SettingsPage from './pages/SettingsPage';

export default function App() {
  return (
    <PortfolioProvider>
      <BrowserRouter>
        <NavBar />
        <div className="p-4">
          <Routes>
            <Route path="/" element={<OptimizePage />} />
            <Route path="/portfolios" element={<PortfolioListPage />} />
            <Route path="/portfolio/:id" element={<PortfolioDetailPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </div>
        <ToastContainer position="top-center" />
      </BrowserRouter>
    </PortfolioProvider>
  );
}