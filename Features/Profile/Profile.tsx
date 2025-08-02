import React, { useContext } from 'react';
import { AppContext } from '../../src/hooks/AppContext';

const Profile: React.FC = () => {
  const { user, logout } = useContext(AppContext);

  return (
    <div className="max-w-md mx-auto p-4 pb-20">
      <div className="bg-white rounded-xl shadow p-6 flex flex-col items-center">
        <img
          src="/assets/profile-placeholder.png"
          alt="User avatar"
          className="w-24 h-24 rounded-full mb-4"
        />
        <div className="text-xl font-semibold">{user?.name}</div>
        <div className="text-gray-700">{user?.phone}</div>
        <div className="text-gray-700">{user?.location}</div>
        <div className="text-gray-700">{user?.language && `Preferred: ${user.language}`}</div>
        <button
          className="mt-6 bg-danger text-white px-6 py-2 rounded"
          onClick={logout}
        >Sign Out</button>
      </div>
    </div>
  );
};
export default Profile;
