import { useState, useRef } from 'react';
import type { FC } from 'react';
import gsap from 'gsap';
import { useGSAP } from '@gsap/react';

interface TypewriterEffectProps {
  strings: string[];
  pauseDuration?: number;
}

export const TypewriterEffect: FC<TypewriterEffectProps> = ({
  strings,
  pauseDuration = 2500, // Slightly longer pause to read the slower text
}) => {
  const containerRef = useRef<HTMLSpanElement>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  
  const currentString = strings[currentIndex];

  useGSAP(() => {
    if (!containerRef.current) return;
    
    // Select all character spans
    const chars = containerRef.current.querySelectorAll('.char');
    
    const tl = gsap.timeline({
      onComplete: () => {
        setCurrentIndex((prev) => (prev + 1) % strings.length);
      }
    });

    // Typewriter IN (fade + blur stagger) - smoother and slower
    tl.fromTo(chars, 
      { opacity: 0, filter: 'blur(8px)' },
      { 
        opacity: 1, 
        filter: 'blur(0px)', 
        duration: 0.25, 
        stagger: 0.05, 
        ease: 'power2.out' 
      }
    );

    // Wait
    tl.to({}, { duration: pauseDuration / 1000 });

    // Typewriter OUT (backspace effect right-to-left)
    tl.to(chars, { 
      opacity: 0, 
      filter: 'blur(2px)', 
      duration: 0.15, 
      stagger: {
        each: 0.03,
        from: 'end'
      },
      ease: 'power2.in' 
    });

  }, [currentIndex, strings, pauseDuration]);

  return (
    <span ref={containerRef} className="inline-block relative">
      {currentString.split('').map((char, i) => (
        <span key={`${currentIndex}-${i}`} className="char inline-block opacity-0" style={{ willChange: 'opacity, filter' }}>
          {char === ' ' ? '\u00A0' : char}
        </span>
      ))}
    </span>
  );
};
