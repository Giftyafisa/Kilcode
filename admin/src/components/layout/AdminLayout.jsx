import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  FaChartLine,
  FaCode,
  FaUsers,
  FaCog,
  FaSignOutAlt
} from 'react-icons/fa';

const AdminLayout = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', path: '/', icon: FaChartLine },
    { name: 'Code Analyzer', path: '/code-analyzer', icon: FaCode },
    { name: 'Users', path: '/users', icon: FaUsers },
    { name: 'Settings', path: '/settings', icon: FaCog }
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-gray-900 text-white">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="px-6 py-8">
            <h1 className="text-2xl font-bold">Admin Panel</h1>
            <p className="text-sm text-gray-400 mt-1">Code Analyzer</p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  className={`flex items-center px-4 py-3 rounded-lg transition-colors ${
                    location.pathname === item.path
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-800'
                  }`}
                >
                  <Icon className="w-5 h-5 mr-3" />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* User Info */}
          <div className="p-4 border-t border-gray-800">
            <div className="flex items-center">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {user?.name || 'Admin User'}
                </p>
                <p className="text-xs text-gray-400 truncate">
                  {user?.email || 'admin@example.com'}
                </p>
              </div>
              <button
                onClick={logout}
                className="ml-2 p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800"
              >
                <FaSignOutAlt className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="pl-64">
        {/* Header */}
        <header className="bg-white shadow">
          <div className="px-8 py-6">
            <h2 className="text-2xl font-bold text-gray-900">
              {navigation.find((item) => item.path === location.pathname)?.name || 'Dashboard'}
            </h2>
          </div>
        </header>

        {/* Content */}
        <main className="p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AdminLayout; 