import type { FC } from 'react';
import { SectionContainer } from '../components/common';
import ResetPasswordForm from '../features/auth/components/ResetPasswordForm';

const ResetPassword: FC = () => (
  <SectionContainer width="auth" padding="lg" className="flex min-h-[80vh] flex-col justify-center">
    <ResetPasswordForm />
  </SectionContainer>
);

export default ResetPassword;
