import { useState, useEffect, useRef } from 'react';
import type { Order } from '../types/order.types';
import * as turf from '@turf/helpers';
import length from '@turf/length';
import along from '@turf/along';

interface SimulationOptions {
  order: Order;
  isActive: boolean;
  maptilerKey?: string;
}

export function useCourierSimulation({ order, isActive, maptilerKey }: SimulationOptions) {
  const [courierPosition, setCourierPosition] = useState<[number, number] | null>(null);
  const [routeGeoJSON, setRouteGeoJSON] = useState<GeoJSON.Feature<GeoJSON.LineString> | null>(null);
  const [isRouteLoading, setIsRouteLoading] = useState(false);
  const [routeError, setRouteError] = useState<string | null>(null);

  const startPoint = order.restaurant_longitude && order.restaurant_latitude 
    ? [Number(order.restaurant_longitude), Number(order.restaurant_latitude)] as [number, number]
    : null;
    
  const endPoint = order.delivery_longitude && order.delivery_latitude
    ? [Number(order.delivery_longitude), Number(order.delivery_latitude)] as [number, number]
    : null;

  const animationRef = useRef<number | null>(null);

  // Fetch route
  useEffect(() => {
    if (!startPoint || !endPoint) return;

    let isMounted = true;
    const fetchRoute = async () => {
      setIsRouteLoading(true);
      setRouteError(null);

      // Create straight line fallback first
      const straightLine = turf.lineString([startPoint, endPoint]);
      
      try {
        if (!maptilerKey) throw new Error('No MapTiler API key');
        
        // Try fetching a route
        const url = `https://api.maptiler.com/routing/directions/driving/${startPoint[0]},${startPoint[1]};${endPoint[0]},${endPoint[1]}?key=${maptilerKey}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Routing API failed');
        
        const data = await response.json();
        if (data.routes && data.routes.length > 0 && isMounted) {
          // The geometry might be a LineString directly or an encoded polyline depending on MapTiler response format
          // By default MapTiler returns a GeoJSON LineString geometry for the route
          setRouteGeoJSON({
            type: 'Feature',
            properties: {},
            geometry: data.routes[0].geometry
          });
          return;
        }
      } catch (err) {
        console.warn('Routing failed, using straight line fallback', err);
      } finally {
        if (isMounted) setIsRouteLoading(false);
      }

      // Fallback to straight line
      if (isMounted) {
        setRouteGeoJSON(straightLine);
      }
    };

    void fetchRoute();
    return () => { isMounted = false; };
  }, [startPoint?.[0], startPoint?.[1], endPoint?.[0], endPoint?.[1], maptilerKey]);

  // Handle animation
  useEffect(() => {
    if (!isActive || !routeGeoJSON || !startPoint || !endPoint) {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
      // If not active, put courier at destination if completed, or start if pending
      if (order.status === 'COMPLETED') {
        setCourierPosition(endPoint);
      } else {
        setCourierPosition(startPoint);
      }
      return;
    }

    const routeLength = length(routeGeoJSON, { units: 'kilometers' });
    const durationMs = 30000; // Simulate 30s journey for MVP

    // Deterministic offset based on order creation time
    // Assume delivery starts ~30s after order creation for this simulated MVP
    const assumedDeliveryStartTime = new Date(order.created_at).getTime() + 30000;
    
    const animate = () => {
      const now = Date.now();
      let elapsed = now - assumedDeliveryStartTime;
      
      // If the order somehow started delivering earlier than 30s, or we're running fast
      if (elapsed < 0) elapsed = 0;
      
      let progress = elapsed / durationMs;
      if (progress >= 1) progress = 1;

      const currentDistance = routeLength * progress;
      const currentPoint = along(routeGeoJSON, currentDistance, { units: 'kilometers' });
      
      setCourierPosition(currentPoint.geometry.coordinates as [number, number]);

      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animate);
      } else {
        // If progress is >= 1, we don't need to keep animating until the backend catches up
        if (order.status !== 'COMPLETED') {
           // We might just poll a bit or stay at 99% until status updates
           const nearEnd = along(routeGeoJSON, routeLength * 0.99, { units: 'kilometers' });
           setCourierPosition(nearEnd.geometry.coordinates as [number, number]);
        } else {
           setCourierPosition(endPoint);
        }
      }
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isActive, routeGeoJSON, startPoint, endPoint, order.status]);

  return {
    courierPosition,
    routeGeoJSON,
    startPoint,
    endPoint,
    isRouteLoading,
    routeError
  };
}
