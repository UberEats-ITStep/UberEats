export const formatOrderDate = (dateValue: string): string => {
  const date = new Date(dateValue);
  if (Number.isNaN(date.getTime())) return dateValue;

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
};

export interface StatusStep {
  id: import('../types/order.types').OrderStatus;
  title: string;
  description: string;
}

export const LIFECYCLE_STEPS: StatusStep[] = [
  { id: 'PENDING', title: 'Order placed', description: 'Waiting for restaurant confirmation' },
  { id: 'ACCEPTED', title: 'Restaurant accepted', description: 'Getting ready to prepare' },
  { id: 'PREPARING', title: 'Preparing your food', description: 'The kitchen is working on your order' },
  { id: 'READY', title: 'Ready for pickup', description: 'Waiting for a courier' },
  { id: 'DELIVERING', title: 'Out for delivery', description: 'Heading your way' },
  { id: 'COMPLETED', title: 'Delivered', description: 'Enjoy your meal!' },
];

export const getActiveStepIndex = (status: import('../types/order.types').OrderStatus): number => {
  const index = LIFECYCLE_STEPS.findIndex((s) => s.id === status);
  return index >= 0 ? index : 0;
};
