export interface Promotion {
  id: string | number;
  title: string;
  description: string;
  ctaText: string;
  ctaLink: string;
  backgroundColor: string; // Tailwind color class or hex
  textColor: string;       // Tailwind color class or hex
  accentColor?: string;    // Tailwind text color class for CTA/accents
  illustrationEmoji?: string;
  imageUrl?: string;
}
