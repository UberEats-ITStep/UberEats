import { useRef } from 'react';
import type { FC } from 'react';
import { SectionContainer } from '../components/common';
import LoginForm from '../features/auth/components/LoginForm';
import gsap from 'gsap';
import { useGSAP } from '@gsap/react';

const Login: FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    gsap.fromTo('.login-reveal',
      { y: 40, opacity: 0 },
      { y: 0, opacity: 1, duration: 1, stagger: 0.1, ease: 'power3.out' }
    );
  }, { scope: containerRef });

  return (
    <div ref={containerRef} className="flex-1">
      <SectionContainer width="auth" padding="lg" className="flex min-h-[80vh] flex-col justify-center">
        <div className="login-reveal">
          <LoginForm />
        </div>
      </SectionContainer>
    </div>
  );
};

export default Login;
