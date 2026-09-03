import { useCallback, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { useGSAP } from '@gsap/react';

gsap.registerPlugin(ScrollTrigger);

const DESKTOP_INITIAL_CLIP = 'inset(16% 7% 14% 36%)';
const MOBILE_INITIAL_CLIP = 'inset(14% 7% 27% 7%)';

export const useHeroAnimation = () => {
  const containerRef = useRef<HTMLElement>(null);

  useGSAP(
    () => {
      const q = gsap.utils.selector(containerRef);
      const photo = q<HTMLElement>('[data-hero="photo"]');
      const image = q<HTMLElement>('[data-hero="image"]');
      const shade = q<HTMLElement>('[data-hero="shade"]');
      const opening = q<HTMLElement>('[data-hero="opening"]');
      const openingDetail = q<HTMLElement>('[data-hero="opening-detail"]');
      const eyebrow = q<HTMLElement>('[data-hero="eyebrow"]');
      const finalCopy = q<HTMLElement>('[data-hero="final-copy"]');
      const cta = q<HTMLElement>('[data-hero="cta"]');
      const nav = q<HTMLElement>('[data-hero="nav"]');
      
      const openingChars = q<HTMLElement>('.opening-char');
      const detailChars = q<HTMLElement>('.detail-char');

      const mm = gsap.matchMedia();

      const prepareScene = (clipPath: string, imageScale: number) => {
        gsap.set(photo, { clipPath });
        gsap.set(image, { scale: imageScale, transformOrigin: '50% 50%' });
        gsap.set(shade, { autoAlpha: 0 });
        gsap.set(opening, { autoAlpha: 1 });
        gsap.set(openingDetail, { autoAlpha: 1 });
        gsap.set(eyebrow, { autoAlpha: 1 });
        gsap.set(finalCopy, { autoAlpha: 0, y: 28 });
        gsap.set(cta, { autoAlpha: 0, y: 12 });
        gsap.set(nav, { color: '#191918' });
      };

      // Intro animation for typing + blur effect
      const playIntroAnimation = () => {
        // Initial state for the characters
        gsap.set(openingChars, { autoAlpha: 0, filter: 'blur(8px)' });
        gsap.set(detailChars, { autoAlpha: 0, filter: 'blur(8px)' });

        const introTl = gsap.timeline();
        introTl.to(openingChars, {
          autoAlpha: 1,
          filter: 'blur(0px)',
          stagger: 0.04,
          duration: 0.8,
          ease: 'power2.out',
        })
        .to(detailChars, {
          autoAlpha: 1,
          filter: 'blur(0px)',
          stagger: 0.02,
          duration: 0.6,
          ease: 'power2.out',
        }, '>');
        
        return introTl;
      };

      mm.add('(min-width: 768px) and (prefers-reduced-motion: no-preference)', () => {
        prepareScene(DESKTOP_INITIAL_CLIP, 1.12);
        
        const introTl = playIntroAnimation();

        const tl = gsap.timeline({
          defaults: { ease: 'none' },
          scrollTrigger: {
            trigger: containerRef.current,
            start: 'top top',
            end: 'bottom bottom',
            scrub: 0.5,
            invalidateOnRefresh: true,
          },
        });

        tl.to(photo, { clipPath: 'inset(0% 0% 0% 0%)', duration: 2.15, ease: 'power2.inOut' }, 0)
          .to(image, { scale: 1, duration: 2.7 }, 0)
          .to(opening, { autoAlpha: 0, xPercent: -8, duration: 0.8 }, 0.25)
          .to(openingDetail, { autoAlpha: 0, xPercent: 12, duration: 0.65 }, 0.32)
          .to(eyebrow, { autoAlpha: 0, y: -10, duration: 0.5 }, 0.36)
          .to(shade, { autoAlpha: 0.5, duration: 1.1, ease: 'power1.inOut' }, 1.45)
          .to(nav, { color: '#ffffff', duration: 0.6 }, 1.65)
          .to(finalCopy, { autoAlpha: 1, y: 0, duration: 0.8, ease: 'power2.out' }, 2)
          .to(cta, { autoAlpha: 1, y: 0, duration: 0.55, ease: 'power2.out' }, 2.4);

        return () => {
          introTl.kill();
          tl.kill();
        };
      });

      mm.add('(max-width: 767px) and (prefers-reduced-motion: no-preference)', () => {
        prepareScene(MOBILE_INITIAL_CLIP, 1.08);
        
        const introTl = playIntroAnimation();

        const tl = gsap.timeline({
          defaults: { ease: 'none' },
          scrollTrigger: {
            trigger: containerRef.current,
            start: 'top top',
            end: 'bottom bottom',
            scrub: 0.35,
            invalidateOnRefresh: true,
          },
        });

        tl.to(photo, { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.4, ease: 'power2.inOut' }, 0)
          .to(image, { scale: 1, duration: 1.7 }, 0)
          .to(opening, { autoAlpha: 0, y: -10, duration: 0.5 }, 0.12)
          .to(eyebrow, { autoAlpha: 0, y: -8, duration: 0.4 }, 0.15)
          .to(shade, { autoAlpha: 0.5, duration: 0.7, ease: 'power1.inOut' }, 0.95)
          .to(nav, { color: '#ffffff', duration: 0.4 }, 1.15)
          .to(finalCopy, { autoAlpha: 1, y: 0, duration: 0.55, ease: 'power2.out' }, 1.45)
          .to(cta, { autoAlpha: 1, y: 0, duration: 0.4, ease: 'power2.out' }, 1.75);

        return () => {
          introTl.kill();
          tl.kill();
        };
      });

      mm.add('(prefers-reduced-motion: reduce)', () => {
        gsap.set(photo, { clipPath: 'inset(0% 0% 0% 0%)' });
        gsap.set(image, { scale: 1 });
        gsap.set(shade, { autoAlpha: 0.5 });
        gsap.set([opening, openingDetail, eyebrow], { autoAlpha: 0 });
        gsap.set(finalCopy, { autoAlpha: 1, y: 0 });
        gsap.set(cta, { autoAlpha: 1, y: 0 });
        gsap.set(nav, { color: '#ffffff' });
        gsap.set([openingChars, detailChars], { autoAlpha: 1, filter: 'blur(0px)' });
      });

      return () => mm.revert();
    },
    { scope: containerRef },
  );

  const scrollToRestaurants = useCallback(() => {
    document.getElementById('restaurants')?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  return { containerRef, scrollToRestaurants };
};
