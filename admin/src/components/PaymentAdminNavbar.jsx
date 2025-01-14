import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function PaymentAdminNavbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-blue-600">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-white text-2xl font-bold">
              Payment Admin
            </Link>
            {user && (
              <span className="ml-4 text-white bg-blue-700 px-3 py-1 rounded-full text-sm">
                {user.country?.toUpperCase()}
              </span>
            )}
          </div>
          
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <span className="text-white">
                  {user.full_name || user.email}
                </span>
                <button
                  onClick={logout}
                  className="text-white hover:text-gray-200 bg-blue-700 px-4 py-2 rounded-md"
                >
                  Logout
                </button>
              </>
            ) : (
              <Link
                to="/login"
                className="text-white hover:text-gray-200"
              >
                Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default PaymentAdminNavbar; 