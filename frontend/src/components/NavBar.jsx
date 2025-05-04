import React from 'react';
import { NavLink } from 'react-router-dom';

export default function NavBar() {
  const baseClasses = 'px-4 py-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded';
  const activeClasses = 'font-bold underline';
  return (
    <nav className="bg-gray-800 text-gray-300 shadow-md">
      <div className="container mx-auto flex space-x-6 p-2">
        <NavLink to="/" className={({isActive}) => `${baseClasses} ${isActive?activeClasses:''}`}>📊 Optimize</NavLink>
        <NavLink to="/portfolios" className={({isActive}) => `${baseClasses} ${isActive?activeClasses:''}`}>💼 My Portfolios</NavLink>
        <NavLink to="/settings" className={({isActive}) => `${baseClasses} ${isActive?activeClasses:''}`}>⚙️ Settings</NavLink>
      </div>
    </nav>
  );
}