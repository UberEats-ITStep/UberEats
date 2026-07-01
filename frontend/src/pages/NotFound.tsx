import React from 'react';
import { Link } from 'react-router-dom';

const NotFound: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
      <p className="text-xl text-gray-600 mb-8">Page not found</p>
      <Link to="/" className="text-green-600 hover:text-green-500 font-medium">
        Go back home
      </Link>
    </div>
  );
};

export default NotFound;
