import apiClient from '../api/client';

export type EventType = 
  | 'RESTAURANT_VIEW'
  | 'MENU_ITEM_VIEW'
  | 'SEARCH'
  | 'AI_SEARCH'
  | 'ADD_TO_CART'
  | 'REMOVE_FROM_CART';

export const trackEvent = (eventType: EventType, metadata: Record<string, any> = {}) => {
  // Fire and forget
  if (!localStorage.getItem('access_token')) {
    // Cannot track unauthenticated users
    return;
  }
  
  apiClient.post('/users/events/', {
    event_type: eventType,
    metadata,
  }).catch(() => {
    // Silently fail to not interrupt UX
  });
};
