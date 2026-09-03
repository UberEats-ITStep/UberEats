import type { FC } from 'react';
import type { Order } from '../types/order.types';
import { Card } from '../../../components/common';
import { LIFECYCLE_STEPS, getActiveStepIndex } from '../utils/order.utils';
import OrderLiveMap from './OrderLiveMap';

interface OrderTrackerProps {
  order: Order;
}

const OrderTracker: FC<OrderTrackerProps> = ({ order }) => {
  const { status } = order;

  if (status === 'CANCELLED') {
    return (
      <Card padding="lg" className="rounded-none border-2 border-error bg-error/5 mb-8">
        <h2 className="text-3xl font-serif italic text-error mb-2">Order Cancelled</h2>
        <p className="text-base text-error/80">
          This order was cancelled and will not be delivered. If you have been charged, you will be refunded shortly.
        </p>
      </Card>
    );
  }

  const activeIndex = getActiveStepIndex(status);
  const activeStep = LIFECYCLE_STEPS[activeIndex];

  return (
    <Card padding="none" className="rounded-none mb-12 border border-border-default shadow-subtle bg-surface">
      {/* Hero Header for Tracker */}
      <div className="bg-text-primary text-surface p-8 sm:p-12">
        <p className="text-xs font-bold uppercase tracking-widest text-surface/60 mb-2">
          Current Status
        </p>
        <h2 className="text-4xl sm:text-6xl font-bold uppercase tracking-tight mb-4">
          {activeStep?.title || 'PROCESSING'}
        </h2>
        <p className="text-lg font-serif italic text-surface/80">
          {activeStep?.description}
        </p>
      </div>

      <div className="border-b border-border-default">
        <OrderLiveMap order={order} />
      </div>

      {/* Timeline */}
      <div className="p-8 sm:p-12 relative">
        <div className="relative pl-8 pb-4">
          {/* Background vertical line */}
          <div className="absolute left-[15px] top-4 bottom-8 w-[2px] bg-border-default" />
          
          {/* Active vertical line filler */}
          <div 
            className="absolute left-[15px] top-4 w-[2px] bg-text-primary transition-all duration-700 ease-in-out" 
            style={{ height: `${Math.max(0, activeIndex) * 100 / (LIFECYCLE_STEPS.length - 1)}%` }}
          />

          <div className="space-y-12">
            {LIFECYCLE_STEPS.map((step, index) => {
              const isCompleted = index < activeIndex;
              const isCurrent = index === activeIndex;
              const isUpcoming = index > activeIndex;

              return (
                <div key={step.id} className="relative flex gap-6 items-start">
                  {/* Node */}
                  <div className="absolute -left-8 top-1 flex h-8 w-8 items-center justify-center bg-surface">
                    <div 
                      className={`flex rounded-full transition-all duration-500
                        ${isCompleted ? 'h-3 w-3 bg-text-primary' : 
                          isCurrent ? 'h-4 w-4 bg-text-primary ring-4 ring-text-primary/20 animate-pulse-slow' : 
                          'h-3 w-3 border-2 border-border-default bg-surface'}
                      `}
                    />
                  </div>
                  
                  {/* Content */}
                  <div className={`transition-opacity duration-500 ${isUpcoming ? 'opacity-30' : 'opacity-100'} -mt-1`}>
                    <h3 className={`text-lg sm:text-xl font-medium tracking-tight ${isCurrent ? 'text-text-primary font-bold' : 'text-text-secondary'}`}>
                      {step.title}
                    </h3>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default OrderTracker;
