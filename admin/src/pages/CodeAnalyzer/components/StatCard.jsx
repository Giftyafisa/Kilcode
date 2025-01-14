import React from 'react';
import { motion } from 'framer-motion';

const StatCard = ({ title, value, icon, color }) => {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    red: 'bg-red-100 text-red-600',
    yellow: 'bg-yellow-100 text-yellow-600'
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className={`p-6 rounded-lg shadow-sm ${colorClasses[color]} bg-opacity-50`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-70">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className="text-2xl opacity-80">{icon}</div>
      </div>
    </motion.div>
  );
};

export default StatCard; 