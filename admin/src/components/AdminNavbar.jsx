import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FaUserShield, FaUsers, FaSignOutAlt, FaTicketAlt } from 'react-icons/fa';

function AdminNavbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => {
    return location.pathname === path ? 'bg-blue-700' : '';
  };

  if (!user) return null;

  return (
    <nav className="bg-blue-800 text-white">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between h-16">
          <div className="flex">
            {/* Logo/Brand */}
            <div className="flex-shrink-0 flex items-center">
              <Link to="/" className="text-xl font-bold">
                Admin Portal
              </Link>
            </div>

            {/* Navigation Links */}
            <div className="hidden md:ml-6 md:flex md:items-center md:space-x-4">
              <Link
                to="/"
                className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/')}`}
              >
                <div className="flex items-center space-x-2">
                  <FaUserShield />
                  <span>Dashboard</span>
                </div>
              </Link>

              <Link
                to="/betting-codes"
                className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/betting-codes')}`}
              >
                <div className="flex items-center space-x-2">
                  <FaTicketAlt />
                  <span>Betting Codes</span>
                </div>
              </Link>

              <Link
                to="/users"
                className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/users')}`}
              >
                <div className="flex items-center space-x-2">
                  <FaUsers />
                  <span>Users</span>
                </div>
              </Link>
            </div>
          </div>

          {/* Right side - User Menu */}
          <div className="flex items-center">
            <div className="flex items-center">
              <span className="text-sm mr-4">
                {user.name} {user.country && `(${user.country.toUpperCase()})`}
              </span>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
              >
                <FaSignOutAlt />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default AdminNavbar; 