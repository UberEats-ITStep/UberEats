import type { FC } from 'react';
import { Link } from 'react-router-dom';
import { SectionContainer, EmptyState, Button } from '../components/common';

const NotFound: FC = () => {
  return (
    <SectionContainer width="content" padding="lg" className="flex min-h-[70vh] items-center justify-center">
      <EmptyState
        title="404 — Page Not Found"
        description="The page you are looking for might have been removed, had its name changed, or is temporarily unavailable."
        action={
          <Link to="/">
            <Button variant="primary" size="md">
              Go back home
            </Button>
          </Link>
        }
      />
    </SectionContainer>
  );
};

export default NotFound;
