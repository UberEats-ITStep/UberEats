import type { FC } from 'react';
import { useAuth } from '../hooks/useAuth';
import { SectionContainer, Card, Badge } from '../components/common';
import ChangePasswordForm from '../features/auth/components/ChangePasswordForm';

const Profile: FC = () => {
  const { profile } = useAuth();

  return (
    <SectionContainer width="content" padding="lg" className="flex min-h-[70vh] items-center justify-center">
      <Card elevation="elevated" padding="lg" className="w-full max-w-3xl space-y-8">
        <div>
          <div className="mb-2">
            <Badge variant="success" size="sm">
              Authenticated
            </Badge>
          </div>
          <h1 className="text-page-title">Your profile</h1>
          <p className="mt-2 text-body">
            This data was loaded from the protected GET /profile endpoint.
          </p>
        </div>

        <dl className="divide-y divide-border-default rounded-lg border border-border-default bg-background">
          <div className="p-4">
            <dt className="text-caption">Phone number</dt>
            <dd className="mt-1 font-semibold text-text-primary">{profile?.phone_number || 'Not provided'}</dd>
          </div>
          <div className="p-4">
            <dt className="text-caption">Address</dt>
            <dd className="mt-1 font-semibold text-text-primary">{profile?.address || 'Not provided'}</dd>
          </div>
        </dl>

        <ChangePasswordForm />
      </Card>
    </SectionContainer>
  );
};

export default Profile;
