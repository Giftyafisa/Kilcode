import React from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useCodeAnalyzerAuth } from '../../context/CodeAnalyzerAuthContext';
import { FaChartBar, FaUpload, FaSignOutAlt } from 'react-icons/fa';

const CodeAnalyzerLayout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useCodeAnalyzerAuth();

  const navigation = [
    { name: 'Dashboard', path: '/', icon: FaChartBar },
    { name: 'Upload Code', path: '/upload', icon: FaUpload },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header with Navigation */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-8">
              <h1 className="text-2xl font-semibold text-gray-900">
                Code Analyzer Portal
              </h1>
              <nav className="flex space-x-4">
                {navigation.map((item) => {
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.name}
                      to={item.path}
                      className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${
                        location.pathname === item.path
                          ? 'bg-blue-500 text-white'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      <Icon className="w-4 h-4 mr-2" />
                      {item.name}
                    </Link>
                  );
                })}
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-600">
                {user?.email}
              </span>
              <button
                onClick={handleLogout}
                className="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
              >
                <FaSignOutAlt className="w-4 h-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white shadow mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-gray-600">
            © {new Date().getFullYear()} Kilcode Code Analyzer Portal
          </p>
        </div>
      </footer>
    </div>
  );
};

export default CodeAnalyzerLayout; 