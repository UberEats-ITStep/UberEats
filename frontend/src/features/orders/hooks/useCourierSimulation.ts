import { useState, useEffect, useRef, useMemo } from 'react';
import type { Order } from '../types/order.types';
import * as turf from '@turf/helpers';
import length from '@turf/length';
import along from '@turf/along';
import destination from '@turf/destination';

export type CourierStage = 'PREPARING' | 'TO_RESTAURANT' | 'AT_RESTAURANT' | 'TO_CUSTOMER' | 'ARRIVED' | 'CANCELLED';

interface SimulationOptions {
  order: Order;
  isActive: boolean;
}

export function useCourierSimulation({ order, isActive }: SimulationOptions) {
  const [courierPosition, setCourierPosition] = useState<[number, number] | null>(null);
  const [routeA, setRouteA] = useState<GeoJSON.Feature<GeoJSON.LineString> | null>(null);
  const [routeB, setRouteB] = useState<GeoJSON.Feature<GeoJSON.LineString> | null>(null);
  const [courierStage, setCourierStage] = useState<CourierStage>('PREPARING');
  const [isRouteLoading, setIsRouteLoading] = useState(false);

  // Memoize stable coordinates
  const startPoint = useMemo(() => {
    return order.restaurant_longitude && order.restaurant_latitude 
      ? [Number(order.restaurant_longitude), Number(order.restaurant_latitude)] as [number, number]
      : null;
  }, [order.restaurant_longitude, order.restaurant_latitude]);
    
  const endPoint = useMemo(() => {
    return order.delivery_longitude && order.delivery_latitude
      ? [Number(order.delivery_longitude), Number(order.delivery_latitude)] as [number, number]
      : null;
  }, [order.delivery_longitude, order.delivery_latitude]);

  // Deterministic courier starting position based on order ID
  const courierStart = useMemo(() => {
    if (!startPoint) return null;
    const bearing = (order.id * 37) % 360 - 180;
    // 1.5 km away
    return destination(startPoint, 1.5, bearing, { units: 'kilometers' }).geometry.coordinates as [number, number];
  }, [startPoint, order.id]);

  // Fetch routes
  useEffect(() => {
    if (!startPoint || !endPoint || !courierStart) return;
    
    let isMounted = true;

    const fetchRoutes = async () => {
      setIsRouteLoading(true);
      try {
        // Fetch Route A: Courier Start -> Restaurant
        const urlA = `https://router.project-osrm.org/route/v1/driving/${courierStart[0]},${courierStart[1]};${startPoint[0]},${startPoint[1]}?overview=full&geometries=geojson`;
        const resA = await fetch(urlA);
        let geomA = turf.lineString([courierStart, startPoint]);
        
        if (resA.ok) {
          const dataA = await resA.json();
          if (dataA.routes && dataA.routes.length > 0) {
            geomA = turf.feature(dataA.routes[0].geometry) as GeoJSON.Feature<GeoJSON.LineString>;
          }
        }

        // Fetch Route B: Restaurant -> Customer
        const urlB = `https://router.project-osrm.org/route/v1/driving/${startPoint[0]},${startPoint[1]};${endPoint[0]},${endPoint[1]}?overview=full&geometries=geojson`;
        const resB = await fetch(urlB);
        let geomB = turf.lineString([startPoint, endPoint]);

        if (resB.ok) {
          const dataB = await resB.json();
          if (dataB.routes && dataB.routes.length > 0) {
            geomB = turf.feature(dataB.routes[0].geometry) as GeoJSON.Feature<GeoJSON.LineString>;
          }
        }

        if (isMounted) {
          setRouteA(geomA);
          setRouteB(geomB);
        }
      } catch (err) {
        console.warn('Routing failed, using straight lines fallback', err);
        if (isMounted) {
          setRouteA(turf.lineString([courierStart, startPoint]));
          setRouteB(turf.lineString([startPoint, endPoint]));
        }
      } finally {
        if (isMounted) setIsRouteLoading(false);
      }
    };

    void fetchRoutes();
    return () => { isMounted = false; };
  }, [courierStart?.[0], courierStart?.[1], startPoint?.[0], startPoint?.[1], endPoint?.[0], endPoint?.[1]]);

  // Animation Refs
  const progressA = useRef(0);
  const progressB = useRef(0);
  const lastFrameTime = useRef(Date.now());
  const animationFrameRef = useRef<number | null>(null);

  // Jump progress based on backend status
  useEffect(() => {
    if (order.status === 'DELIVERING' && progressA.current < 1) {
      // Force completion of Stage A if backend says we are already delivering
      progressA.current = 1;
    }
  }, [order.status]);

  // Main Simulation Loop
  useEffect(() => {
    if (!isActive || !routeA || !routeB || !startPoint || !endPoint || !courierStart) {
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
      return;
    }

    if (order.status === 'CANCELLED') {
      setCourierStage('CANCELLED');
      return;
    }

    if (order.status === 'COMPLETED') {
      setCourierStage('ARRIVED');
      setCourierPosition(endPoint);
      return;
    }

    let isAnimating = true;
    lastFrameTime.current = Date.now();

    const animate = () => {
      if (!isAnimating) return;
      const now = Date.now();
      const delta = now - lastFrameTime.current;
      lastFrameTime.current = now;

      if (progressA.current < 1) {
        setCourierStage('TO_RESTAURANT');
        // Courier travels to restaurant (15s simulation duration)
        progressA.current += delta / 15000;
        if (progressA.current >= 1) progressA.current = 1;
        
        const len = length(routeA);
        const pos = along(routeA, progressA.current * len).geometry.coordinates;
        setCourierPosition(pos as [number, number]);
      } 
      else if (progressA.current >= 1 && order.status !== 'DELIVERING') {
        // Reached restaurant, waiting for backend to hit DELIVERING
        setCourierStage('AT_RESTAURANT');
        setCourierPosition(startPoint);
      }
      else if (progressA.current >= 1 && order.status === 'DELIVERING') {
        setCourierStage('TO_CUSTOMER');
        // Courier travels to customer (30s simulation duration)
        progressB.current += delta / 30000;
        if (progressB.current >= 1) progressB.current = 1;

        const len = length(routeB);
        // clamp to 0.999 to avoid exactly hitting the end before backend is COMPLETED
        const pos = along(routeB, Math.min(progressB.current, 0.999) * len).geometry.coordinates;
        setCourierPosition(pos as [number, number]);
      }

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animationFrameRef.current = requestAnimationFrame(animate);

    return () => {
      isAnimating = false;
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    };
  }, [isActive, order.status, routeA, routeB, startPoint, endPoint, courierStart]);

  return {
    courierPosition,
    routeA,
    routeB,
    startPoint,
    endPoint,
    courierStart,
    courierStage,
    isRouteLoading
  };
}
