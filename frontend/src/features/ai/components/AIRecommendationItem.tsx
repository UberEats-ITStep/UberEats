import type { FC } from 'react';
import { Link } from 'react-router-dom';
import { formatPrice } from '../../../utils/currency';
import type { AIRecommendationItem as AIRecommendationItemType } from '../types/ai.types';

interface AIRecommendationItemProps {
  item: AIRecommendationItemType;
  index: number;
  isFeatured?: boolean;
  onClose: () => void;
}

export const AIRecommendationItem: FC<AIRecommendationItemProps> = ({
  item,
  index,
  isFeatured = false,
  onClose,
}) => {
  const numberStr = String(index + 1).padStart(2, '0');

  return (
    <Link
      to={`/restaurants/${item.menu_item.restaurant.id}#item-${item.menu_item.id}`}
      className={`group/item block focus:outline-none focus:bg-surface-muted transition-colors ${
        isFeatured 
          ? 'pb-6 mb-6 border-b border-border-default' 
          : 'py-4 border-t border-border-default first:border-t-0'
      }`}
      onClick={onClose}
    >
      <div className={`flex items-start gap-4 ${isFeatured ? 'flex-col md:flex-row md:items-start' : 'flex-row'}`}>
        {/* Number */}
        <span className="font-serif italic text-text-muted text-lg mt-0.5 shrink-0 w-8">
          {numberStr}
        </span>
        
        {/* Content */}
        <div className="flex-1">
          <div className="flex justify-between items-start gap-4">
            <div>
              {isFeatured && (
                <span className="text-[10px] font-bold uppercase tracking-widest text-text-primary mb-3 block">
                  Top Match
                </span>
              )}
              <h4
                className={`font-medium text-text-primary group-hover/item:underline decoration-1 underline-offset-4 ${
                  isFeatured ? 'text-2xl font-serif' : 'text-lg'
                }`}
              >
                {item.menu_item.name}
              </h4>
              <p className="text-xs font-bold uppercase tracking-wider text-text-muted mt-1.5">
                {item.menu_item.restaurant.name}
              </p>
            </div>
            
            <span className={`font-serif italic text-text-primary shrink-0 ${isFeatured ? 'text-xl' : 'text-base'}`}>
              {formatPrice(Number(item.menu_item.price))}
            </span>
          </div>
          
          <p className={`text-text-secondary mt-3 ${isFeatured ? 'text-base max-w-2xl' : 'text-sm'}`}>
            {item.reason}
          </p>
        </div>
      </div>
    </Link>
  );
};
