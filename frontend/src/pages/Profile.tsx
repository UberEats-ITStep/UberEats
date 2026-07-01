import type { FC } from 'react';
import { useAuth } from '../hooks/useAuth';

const Profile: FC = () => {
  const { profile } = useAuth();

  return (
    <div className="min-h-[70vh] flex items-center justify-center py-12">
      <section className="w-full max-w-md p-8 space-y-6 bg-white rounded-xl shadow-lg border border-gray-100">
        <div>
          <p className="text-sm font-medium text-green-600">Authenticated</p>
          <h1 className="mt-1 text-3xl font-extrabold text-gray-900">Your profile</h1>
          <p className="mt-2 text-sm text-gray-600">
            This data was loaded from the protected GET /profile endpoint.
          </p>
        </div>

        <dl className="divide-y divide-gray-100 rounded-lg border border-gray-200">
          <div className="p-4">
            <dt className="text-sm font-medium text-gray-500">Phone number</dt>
            <dd className="mt-1 text-gray-900">{profile?.phone_number || 'Not provided'}</dd>
          </div>
          <div className="p-4">
            <dt className="text-sm font-medium text-gray-500">Address</dt>
            <dd className="mt-1 text-gray-900">{profile?.address || 'Not provided'}</dd>
          </div>
        </dl>
      </section>
    </div>
  );
};

export default Profile;
