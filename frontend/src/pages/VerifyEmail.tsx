import type { FC } from 'react';
import { SectionContainer } from '../components/common';
import VerificationForm from '../features/auth/components/VerificationForm';

const VerifyEmail: FC = () => {
  return (
    <SectionContainer width="auth" padding="lg" className="flex min-h-[80vh] flex-col justify-center">
      <VerificationForm />
    </SectionContainer>
  );
};

export default VerifyEmail;
