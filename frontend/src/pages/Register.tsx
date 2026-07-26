import type { FC } from 'react';
import { SectionContainer } from '../components/common';
import RegisterForm from '../features/auth/components/RegisterForm';

const Register: FC = () => {
  return (
    <SectionContainer width="auth" padding="lg" className="flex min-h-[80vh] flex-col justify-center">
      <RegisterForm />
    </SectionContainer>
  );
};

export default Register;
