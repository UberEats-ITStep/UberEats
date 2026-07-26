import type { FC } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Home from '../pages/Home';

const IndexRoute: FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-64 items-center justify-center" role="status">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return isAuthenticated ? <Home /> : <Navigate to="/login" replace />;
};

export default IndexRoute;
