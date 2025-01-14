import React from 'react';
import { FaChartPie, FaPercentage, FaTrophy } from 'react-icons/fa';

const StatisticalAnalysis = ({ codes }) => {
  const calculateWinLossRatio = () => {
    const total = codes.length;
    const won = codes.filter(code => code.status === 'won').length;
    const lost = codes.filter(code => code.status === 'lost').length;
    return {
      winRatio: ((won / total) * 100).toFixed(2),
      lossRatio: ((lost / total) * 100).toFixed(2)
    };
  };

  const calculateAverageOdds = () => {
    const totalOdds = codes.reduce((acc, code) => acc + code.odds, 0);
    return (totalOdds / codes.length).toFixed(2);
  };

  const { winRatio, lossRatio } = calculateWinLossRatio();
  const averageOdds = calculateAverageOdds();

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold mb-4">Statistical Analysis</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center space-x-2">
            <FaTrophy className="text-blue-500" />
            <h4 className="font-medium text-gray-700">Win Ratio</h4>
          </div>
          <p className="text-2xl font-bold text-blue-600 mt-2">{winRatio}%</p>
        </div>

        <div className="bg-red-50 p-4 rounded-lg">
          <div className="flex items-center space-x-2">
            <FaPercentage className="text-red-500" />
            <h4 className="font-medium text-gray-700">Loss Ratio</h4>
          </div>
          <p className="text-2xl font-bold text-red-600 mt-2">{lossRatio}%</p>
        </div>

        <div className="bg-green-50 p-4 rounded-lg">
          <div className="flex items-center space-x-2">
            <FaChartPie className="text-green-500" />
            <h4 className="font-medium text-gray-700">Average Odds</h4>
          </div>
          <p className="text-2xl font-bold text-green-600 mt-2">{averageOdds}</p>
        </div>
      </div>
    </div>
  );
};

export default StatisticalAnalysis; 