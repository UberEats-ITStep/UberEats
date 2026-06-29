import type { FC } from 'react';
import RegisterForm from '../features/auth/components/RegisterForm';

const Register: FC = () => {
  return (
    <div className="min-h-[80vh] flex flex-col justify-center items-center py-12 px-4 sm:px-6 lg:px-8">
      <RegisterForm />
    </div>
  );
};

export default Register;
