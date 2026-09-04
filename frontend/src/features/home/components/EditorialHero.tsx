import type { FC } from "react";
import { Link } from "react-router-dom";
import { useHeroAnimation } from "../hooks/useHeroAnimation";
import "./EditorialHero.css";

const HERO_IMAGE =
  "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?q=80&w=2000&auto=format&fit=crop";

const splitText = (text: string, className: string) => {
  return text.split(" ").map((word, wordIndex, wordsArr) => (
    <span key={wordIndex} className="inline-block whitespace-nowrap">
      {word.split("").map((char, charIndex) => (
        <span key={charIndex} className={`inline-block ${className}`}>
          {char}
        </span>
      ))}
      {wordIndex !== wordsArr.length - 1 && (
        <span className={`inline-block ${className}`}>&nbsp;</span>
      )}
    </span>
  ));
};

const EditorialHero: FC = () => {
  const { containerRef, scrollToRestaurants } = useHeroAnimation();

  return (
    <section
      ref={containerRef}
      className="editorial-hero relative w-full bg-background"
    >
      <div
        data-hero="stage"
        className="editorial-hero__stage sticky top-0 w-full overflow-hidden"
      >
        <div
          data-hero="photo"
          className="editorial-hero__photo absolute inset-0 overflow-hidden"
        >
          <img
            data-hero="image"
            src={HERO_IMAGE}
            alt="A carefully prepared restaurant dish"
            className="absolute inset-0 h-full w-full object-cover"
            loading="eager"
            fetchPriority="high"
            draggable={false}
          />
          <div
            data-hero="shade"
            aria-hidden="true"
            className="absolute inset-0 bg-black"
          />
        </div>

        <div className="pointer-events-none absolute inset-0 z-10">
          <p
            data-hero="eyebrow"
            className="absolute left-5 top-24 text-[10px] font-semibold uppercase tracking-[0.26em] text-text-primary sm:left-8 sm:top-32 lg:left-12"
          >
            BiteUp / 01
          </p>

          <h1
            data-hero="opening"
            className="editorial-hero__opening absolute font-serif text-text-primary"
          >
            <span className="block whitespace-nowrap mb-2 md:mb-4">
              {splitText("Food worth", "opening-char")}
            </span>
            <span className="block whitespace-nowrap italic">
              {splitText("remembering.", "opening-char")}
            </span>
          </h1>

          <p
            data-hero="opening-detail"
            className="editorial-hero__opening-detail absolute hidden text-right text-[10px] font-semibold uppercase leading-relaxed tracking-[0.18em] text-text-secondary md:block"
          >
            <span className="block whitespace-nowrap">
              {splitText("Restaurants selected for", "detail-char")}
            </span>
            <span className="block whitespace-nowrap">
              {splitText("every kind of evening", "detail-char")}
            </span>
          </p>

          <div
            data-hero="final-copy"
            className="absolute inset-x-5 top-1/2 -translate-y-1/2 text-center text-white sm:inset-x-8"
          >
            <p className="mb-5 text-[10px] font-semibold uppercase tracking-[0.28em] text-white/70">
              The table is yours
            </p>
            <h2 className="font-serif text-[clamp(4rem,10vw,10.5rem)] leading-[0.8] tracking-[-0.04em]">
              Taste it
              <br />
              <span className="italic">tonight.</span>
            </h2>
          </div>
        </div>

        <button
          data-hero="cta"
          type="button"
          onClick={scrollToRestaurants}
          className="absolute bottom-7 left-1/2 z-20 flex -translate-x-1/2 flex-col items-center gap-3 whitespace-nowrap text-[10px] font-semibold uppercase tracking-[0.22em] text-white focus:outline-none focus:ring-1 focus:ring-white focus:ring-offset-2 focus:ring-offset-black sm:bottom-10"
        >
          Explore restaurants
          <span aria-hidden="true" className="h-8 w-px bg-white/60" />
        </button>

        <nav
          data-hero="nav"
          className="absolute left-0 top-0 z-30 flex w-full items-center justify-between px-5 py-6 sm:px-8 sm:py-7 lg:px-12"
        >
          <Link
            to="/"
            className="font-serif text-3xl italic leading-none tracking-tight focus:outline-none focus:ring-1 focus:ring-current"
          >
            BiteUp.
          </Link>
          <Link
            to="/login"
            className="border border-current px-4 py-2 text-[10px] font-semibold uppercase tracking-[0.16em] transition-opacity hover:opacity-70 focus:outline-none focus:ring-1 focus:ring-current focus:ring-offset-2"
          >
            Sign in
          </Link>
        </nav>
      </div>
    </section>
  );
};

export default EditorialHero;
