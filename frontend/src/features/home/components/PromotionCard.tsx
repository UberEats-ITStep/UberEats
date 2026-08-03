import type { FC } from 'react';
import { Link } from 'react-router-dom';
import type { Promotion } from '../types/promotion.types';

export interface PromotionCardProps {
  promotion: Promotion;
}

export const PromotionCard: FC<PromotionCardProps> = ({ promotion }) => {
  return (
    <div 
      className={`relative w-full h-48 sm:h-64 rounded-xl overflow-hidden shadow-subtle border border-border-default flex items-center justify-between p-8 sm:p-12 ${promotion.backgroundColor}`}
    >
      <div className={`z-10 flex flex-col items-start justify-center max-w-lg ${promotion.textColor}`}>
        <h2 className="text-2xl sm:text-4xl font-bold tracking-tight mb-3">
          {promotion.title}
        </h2>
        <p className="text-sm sm:text-lg mb-8 opacity-90 max-w-md leading-relaxed">
          {promotion.description}
        </p>
        <Link 
          to={promotion.ctaLink}
          className={`inline-flex items-center justify-center rounded-sm bg-white px-6 py-2.5 text-sm font-bold transition-base hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-slate-900 shadow-sm ${promotion.accentColor || 'text-gray-900'}`}
        >
          {promotion.ctaText}
        </Link>
      </div>

      {promotion.illustrationEmoji && (
        <div className="absolute right-4 bottom-4 sm:right-8 sm:bottom-4 opacity-40 pointer-events-none text-6xl sm:text-8xl select-none">
          {promotion.illustrationEmoji}
        </div>
      )}
      
      {promotion.imageUrl && (
        <div className="absolute inset-y-0 right-0 w-1/3 overflow-hidden pointer-events-none opacity-50">
          <div className="absolute inset-0 bg-gradient-to-r from-slate-900 to-transparent z-10" />
          <img 
            src={promotion.imageUrl} 
            alt="" 
            className="w-full h-full object-cover object-center mask-image-to-l" 
          />
        </div>
      )}
    </div>
  );
};

export default PromotionCard;
