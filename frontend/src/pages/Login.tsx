import type { FC } from 'react';
import { SectionContainer } from '../components/common';
import LoginForm from '../features/auth/components/LoginForm';

const Login: FC = () => {
  return (
    <SectionContainer width="auth" padding="lg" className="flex min-h-[80vh] flex-col justify-center">
      <LoginForm />
    </SectionContainer>
  );
};

export default Login;
