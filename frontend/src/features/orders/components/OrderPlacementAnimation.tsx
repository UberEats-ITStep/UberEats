import type { FC } from 'react';

interface OrderPlacementAnimationProps {
  isSuccess: boolean;
}

const OrderPlacementAnimation: FC<OrderPlacementAnimationProps> = ({ isSuccess }) => {
  return (
    <div className="flex flex-col items-center justify-center space-y-10 animate-fade-in w-full max-w-md mx-auto py-16 px-4">
      
      {/* Animated Icon Container */}
      <div className="relative flex items-center justify-center w-36 h-36">
        
        {/* Expanding Background Ring */}
        <div 
          className={`absolute inset-0 rounded-full opacity-20 animate-ping transition-colors duration-500
            ${isSuccess ? 'bg-status-success' : 'bg-accent'}`} 
        />
        
        {/* Core Circle */}
        <div 
          className={`relative z-10 flex items-center justify-center w-28 h-28 rounded-full shadow-lg transition-all duration-700
            ${isSuccess ? 'bg-status-success scale-110' : 'bg-surface border-4 border-accent'}`}
        >
          {isSuccess ? (
            <svg 
              className="w-14 h-14 text-white animate-pop drop-shadow-md" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor" 
              strokeWidth={3}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          ) : (
            <div className="relative flex items-center justify-center">
              <svg 
                className="w-12 h-12 text-accent animate-spin" 
                fill="none" 
                viewBox="0 0 24 24"
              >
                <circle 
                  className="opacity-20" 
                  cx="12" cy="12" r="10" 
                  stroke="currentColor" 
                  strokeWidth="4"
                ></circle>
                <path 
                  className="opacity-90" 
                  fill="currentColor" 
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              {/* Subtle inner pulsing dot */}
              <div className="absolute inset-0 m-auto w-2 h-2 bg-accent rounded-full animate-pulse" />
            </div>
          )}
        </div>
      </div>
      
      {/* Dynamic Text Content */}
      <div className="text-center space-y-3">
        <h2 className="text-3xl font-extrabold text-text-primary tracking-tight transition-all duration-300">
          {isSuccess ? 'Order Confirmed!' : 'Processing Order...'}
        </h2>
        <p className="text-text-secondary text-lg">
          {isSuccess 
            ? 'Your meal is being sent to the kitchen. Redirecting to your tracking page...' 
            : 'Securely finalizing your delivery with the restaurant.'}
        </p>
      </div>
    </div>
  );
};

export default OrderPlacementAnimation;
