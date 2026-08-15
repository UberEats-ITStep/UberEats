import { useRef, type FC } from 'react';
import { Link } from 'react-router-dom';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { useGSAP } from '@gsap/react';

// Register ScrollTrigger once
if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

export const EditorialHero: FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    // Only execute if ref is populated
    if (!containerRef.current) return;

    // Use matchMedia to handle prefers-reduced-motion
    const mm = gsap.matchMedia(containerRef);

    mm.add("(prefers-reduced-motion: no-preference)", () => {
      // 1. Initial Load Timeline
      const tl = gsap.timeline({ defaults: { ease: 'cubic-bezier(.2, .75, .2, 1)', duration: 0.7 } });
      
      tl.fromTo('.hero-headline-line', 
        { y: 40, opacity: 0 },
        { y: 0, opacity: 1, stagger: 0.15 }
      )
      .fromTo('.hero-copy',
        { y: 20, opacity: 0 },
        { y: 0, opacity: 1 },
        "-=0.4"
      )
      .fromTo('.hero-ctas',
        { y: 20, opacity: 0 },
        { y: 0, opacity: 1 },
        "-=0.5"
      )
      .fromTo('.hero-art',
        { opacity: 0, scale: 0.95, rotation: -2 },
        { opacity: 1, scale: 1, rotation: 0, stagger: 0.1, duration: 1 },
        "-=0.6"
      );

      // 2. Subtle Scroll Parallax for Artwork
      gsap.to('.hero-art-parallax', {
        y: -40,
        ease: 'none',
        scrollTrigger: {
          trigger: '.hero-section',
          start: 'top top',
          end: 'bottom top',
          scrub: true,
        }
      });

      // 3. Reveal "How it works" steps on scroll
      gsap.fromTo('.how-step',
        { y: 30, opacity: 0 },
        {
          y: 0, 
          opacity: 1, 
          stagger: 0.15,
          duration: 0.6,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: '.how-it-works-section',
            start: 'top 85%',
          }
        }
      );
    });

    // Fallback for reduced motion
    mm.add("(prefers-reduced-motion: reduce)", () => {
      gsap.set(['.hero-headline-line', '.hero-copy', '.hero-ctas', '.hero-art', '.how-step'], { 
        opacity: 1, y: 0, scale: 1, rotation: 0 
      });
    });

    return () => {
      // Clean up matchMedia on unmount
      mm.revert();
    };
  }, { scope: containerRef });

  return (
    <div ref={containerRef} className="w-full bg-background pt-6 pb-20 border-b border-border-default overflow-hidden">
      
      {/* Top Navigation Strip */}
      <div className="container-page flex justify-between items-center mb-16 relative z-20">
        <div className="font-serif italic font-bold text-2xl tracking-tight text-text-primary">
          BiteUp
        </div>
        <Link 
          to="/login" 
          className="text-sm font-medium tracking-widest uppercase text-text-secondary hover:text-text-primary transition-colors underline-offset-4 hover:underline"
        >
          Sign in
        </Link>
      </div>

      {/* Main Hero Section */}
      <section className="hero-section container-page relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-16 min-h-[60vh]">
        
        {/* Left Column: Copy & CTA */}
        <div className="max-w-2xl lg:w-1/2">
          
          <h1 className="text-5xl lg:text-7xl xl:text-8xl font-bold tracking-tight text-text-primary mb-8 overflow-hidden">
            <div className="hero-headline-line">Your next</div>
            <div className="hero-headline-line font-serif italic font-normal text-text-secondary">meal,</div>
            <div className="hero-headline-line">made easy.</div>
          </h1>

          <div className="hero-copy mb-10">
            <p className="text-lg text-text-secondary max-w-lg leading-relaxed mb-6">
              Discover local restaurants, browse exquisite menus, build your perfect order, and make dinner effortless.
            </p>
            
            <div className="flex flex-wrap gap-x-6 gap-y-2 text-xs font-medium tracking-widest uppercase text-text-muted">
              <span>✓ Local kitchens</span>
              <span>✓ Menus in one place</span>
              <span>✓ Simple ordering</span>
            </div>
          </div>

          <div className="hero-ctas flex flex-wrap items-center gap-4">
            <a 
              href="#restaurants" 
              className="px-8 py-4 bg-primary text-surface font-medium text-sm tracking-wide transition-all duration-300 hover:bg-primary-hover hover:-translate-y-0.5"
            >
              Explore restaurants
            </a>
            <Link 
              to="/login" 
              className="px-8 py-4 bg-surface border border-border-default text-text-primary font-medium text-sm tracking-wide transition-all duration-300 hover:border-text-primary hover:-translate-y-0.5"
            >
              Sign in
            </Link>
          </div>
        </div>

        {/* Right Column: Editorial Artwork */}
        <div className="lg:w-1/2 h-80 lg:h-[500px] relative mt-12 lg:mt-0 opacity-100 flex items-center justify-center">
          <div className="hero-art-parallax relative w-full h-full">
            {/* Abstract background grid */}
            <div className="hero-art absolute inset-0 editorial-grid opacity-10"></div>
            
            {/* Minimalist Shapes / Plates */}
            <div className="hero-art absolute top-10 right-10 w-64 h-64 rounded-full border border-border-default flex items-center justify-center">
               <div className="w-48 h-48 rounded-full border border-border-subtle bg-surface shadow-subtle flex items-center justify-center">
                 <div className="w-32 h-32 rounded-full bg-background border border-border-default/50"></div>
               </div>
            </div>
            
            {/* Minimal Menu Card */}
            <div className="hero-art absolute bottom-12 left-10 w-56 p-6 bg-surface border border-border-default shadow-elevated transform -rotate-3 transition-transform duration-500 hover:rotate-0 hover:-translate-y-2 hover:shadow-floating">
               <div className="w-12 h-1 bg-text-primary mb-4"></div>
               <div className="w-3/4 h-2 bg-muted mb-2"></div>
               <div className="w-1/2 h-2 bg-muted mb-6"></div>
               
               <div className="w-full h-1 bg-border-default mb-2"></div>
               <div className="flex justify-between w-full mb-1">
                 <div className="w-2/3 h-1.5 bg-muted"></div>
                 <div className="w-1/4 h-1.5 bg-text-primary"></div>
               </div>
               <div className="flex justify-between w-full">
                 <div className="w-1/2 h-1.5 bg-muted"></div>
                 <div className="w-1/4 h-1.5 bg-text-primary"></div>
               </div>
            </div>

            {/* Stamp / Badge */}
            <div className="hero-art absolute top-1/2 left-1/4 w-20 h-20 bg-primary rounded-full text-surface flex flex-col items-center justify-center transform -translate-y-1/2 translate-x-1/4 rotate-12">
               <span className="text-[10px] uppercase tracking-widest font-medium">Est.</span>
               <span className="font-serif italic text-lg">2026</span>
            </div>
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section className="how-it-works-section container-page mt-32 relative z-10">
        <h2 className="text-xs font-medium tracking-widest uppercase text-text-muted mb-12 border-b border-border-default pb-4">
          How it works
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 lg:gap-24">
          <div className="how-step">
            <div className="text-4xl font-serif italic text-text-muted mb-4">01.</div>
            <h3 className="text-xl font-medium text-text-primary mb-3">Pick a kitchen</h3>
            <p className="text-text-secondary leading-relaxed text-sm">
              Explore curated restaurants in your area, ranging from hidden gems to renowned local favorites.
            </p>
          </div>
          
          <div className="how-step">
            <div className="text-4xl font-serif italic text-text-muted mb-4">02.</div>
            <h3 className="text-xl font-medium text-text-primary mb-3">Choose your dish</h3>
            <p className="text-text-secondary leading-relaxed text-sm">
              Browse elegant menus, customize your perfect meal, and securely place your order in seconds.
            </p>
          </div>
          
          <div className="how-step">
            <div className="text-4xl font-serif italic text-text-muted mb-4">03.</div>
            <h3 className="text-xl font-medium text-text-primary mb-3">Enjoy your evening</h3>
            <p className="text-text-secondary leading-relaxed text-sm">
              Sit back and relax. We coordinate the preparation and delivery so you can savor every bite.
            </p>
          </div>
        </div>
      </section>
      
    </div>
  );
};

export default EditorialHero;
