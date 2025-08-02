// src/components/CropCard.tsx
import React from 'react';
import { FaLeaf, FaExclamationTriangle } from 'react-icons/fa';

type CropCardProps = {
  crop: {
    name: string;
    stage?: string;
    warning?: string;
  };
};

const CropCard: React.FC<CropCardProps> = ({ crop }) => {
  return (
    <div className="bg-white rounded-xl shadow p-4 flex flex-col items-center text-center cursor-pointer hover:shadow-lg transition">
      <div className="text-green-600 mb-2 text-4xl">
        <FaLeaf />
      </div>
      <h3 className="font-semibold text-lg">{crop.name}</h3>
      {crop.stage && <p className="text-gray-600 text-sm mt-1">Stage: {crop.stage}</p>}
      {crop.warning && (
        <p className="mt-2 text-red-600 flex items-center justify-center text-sm font-semibold">
          <FaExclamationTriangle className="mr-1" /> {crop.warning}
        </p>
      )}
    </div>
  );
};

export default CropCard;
