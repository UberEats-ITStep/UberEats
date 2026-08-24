import type { FC } from 'react';
import { SectionContainer } from '../components/common';
import ForgotPasswordForm from '../features/auth/components/ForgotPasswordForm';

const ForgotPassword: FC = () => (
  <SectionContainer width="auth" padding="lg" className="flex min-h-[80vh] flex-col justify-center">
    <ForgotPasswordForm />
  </SectionContainer>
);

export default ForgotPassword;
