import type { FC } from 'react';
import LoginForm from '../features/auth/components/LoginForm';

const Login: FC = () => {
  return (
    <div className="min-h-[80vh] flex flex-col justify-center items-center py-12 px-4 sm:px-6 lg:px-8">
      <LoginForm />
    </div>
  );
};

export default Login;
