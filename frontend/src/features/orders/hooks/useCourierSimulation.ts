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
  const storageKey = `courier_sim_order_${order.id}`;

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

  const getInitialProgressA = (): number => {
    if (['ACCEPTED', 'PREPARING', 'READY', 'DELIVERING', 'COMPLETED'].includes(order.status)) {
      return 1;
    }
    try {
      const saved = sessionStorage.getItem(storageKey);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.hasReachedRestaurant || parsed.progressA >= 1) return 1;
        if (typeof parsed.progressA === 'number') return parsed.progressA;
      }
    } catch {
      // Ignore sessionStorage errors
    }
    if (order.created_at) {
      const elapsed = (Date.now() - new Date(order.created_at).getTime()) / 1000;
      if (elapsed >= 15) return 1;
      if (elapsed > 0) return Math.min(1, elapsed / 15);
    }
    return 0;
  };

  const getInitialProgressB = (): number => {
    if (order.status === 'COMPLETED') return 1;
    try {
      const saved = sessionStorage.getItem(storageKey);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (typeof parsed.progressB === 'number') return parsed.progressB;
      }
    } catch {
      // Ignore sessionStorage errors
    }
    return 0;
  };

  const progressA = useRef<number>(getInitialProgressA());
  const progressB = useRef<number>(getInitialProgressB());
  const hasReachedRestaurant = useRef<boolean>(progressA.current >= 1);
  const lastFrameTime = useRef(Date.now());
  const animationFrameRef = useRef<number | null>(null);

  const getInitialStage = (): CourierStage => {
    if (order.status === 'CANCELLED') return 'CANCELLED';
    if (order.status === 'COMPLETED') return 'ARRIVED';
    if (order.status === 'DELIVERING') return 'TO_CUSTOMER';
    if (hasReachedRestaurant.current || ['ACCEPTED', 'PREPARING', 'READY'].includes(order.status)) {
      return 'AT_RESTAURANT';
    }
    return 'TO_RESTAURANT';
  };

  const getInitialPosition = (): [number, number] | null => {
    if (order.status === 'COMPLETED' && endPoint) return endPoint;
    if ((hasReachedRestaurant.current || ['ACCEPTED', 'PREPARING', 'READY'].includes(order.status)) && startPoint) {
      return startPoint;
    }
    return courierStart;
  };

  const [courierPosition, setCourierPosition] = useState<[number, number] | null>(getInitialPosition);
  const [routeA, setRouteA] = useState<GeoJSON.Feature<GeoJSON.LineString> | null>(null);
  const [routeB, setRouteB] = useState<GeoJSON.Feature<GeoJSON.LineString> | null>(null);
  const [courierStage, setCourierStage] = useState<CourierStage>(getInitialStage);
  const [isRouteLoading, setIsRouteLoading] = useState(false);

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

  // Sync state if order status changes externally
  useEffect(() => {
    if (['ACCEPTED', 'PREPARING', 'READY', 'DELIVERING', 'COMPLETED'].includes(order.status)) {
      progressA.current = 1;
      hasReachedRestaurant.current = true;
    }
    if (order.status === 'COMPLETED') {
      progressB.current = 1;
      setCourierStage('ARRIVED');
      if (endPoint) setCourierPosition(endPoint);
    } else if (order.status === 'CANCELLED') {
      setCourierStage('CANCELLED');
    } else if (order.status === 'DELIVERING') {
      setCourierStage('TO_CUSTOMER');
    } else if (['ACCEPTED', 'PREPARING', 'READY'].includes(order.status)) {
      setCourierStage('AT_RESTAURANT');
      if (startPoint) setCourierPosition(startPoint);
    }
  }, [order.status, startPoint, endPoint]);

  // Main Simulation Loop
  useEffect(() => {
    if (!isActive || !startPoint || !endPoint || !courierStart) {
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
      progressA.current = 1;
      progressB.current = 1;
      return;
    }

    let isAnimating = true;
    lastFrameTime.current = Date.now();

    const animate = () => {
      if (!isAnimating) return;
      const now = Date.now();
      const delta = now - lastFrameTime.current;
      lastFrameTime.current = now;

      // Stage 1: Heading to restaurant (only while in PENDING and courier hasn't arrived)
      if (progressA.current < 1 && !hasReachedRestaurant.current && order.status === 'PENDING') {
        setCourierStage('TO_RESTAURANT');
        // Courier travels to restaurant (15s simulation duration)
        progressA.current += delta / 15000;
        if (progressA.current >= 1) {
          progressA.current = 1;
          hasReachedRestaurant.current = true;
        }

        if (routeA) {
          const len = length(routeA);
          const pos = along(routeA, progressA.current * len).geometry.coordinates;
          setCourierPosition(pos as [number, number]);
        } else {
          setCourierPosition(courierStart);
        }

        try {
          sessionStorage.setItem(storageKey, JSON.stringify({
            progressA: progressA.current,
            progressB: progressB.current,
            hasReachedRestaurant: hasReachedRestaurant.current
          }));
        } catch {
          // ignore
        }
      } 
      // Stage 2: Arrived and stationary at the restaurant (waiting for food / order preparation)
      else if (order.status !== 'DELIVERING') {
        progressA.current = 1;
        hasReachedRestaurant.current = true;
        setCourierStage('AT_RESTAURANT');
        setCourierPosition(startPoint);

        try {
          sessionStorage.setItem(storageKey, JSON.stringify({
            progressA: 1,
            progressB: progressB.current,
            hasReachedRestaurant: true
          }));
        } catch {
          // ignore
        }
      }
      // Stage 3: Out for delivery to customer
      else if (order.status === 'DELIVERING') {
        progressA.current = 1;
        hasReachedRestaurant.current = true;
        setCourierStage('TO_CUSTOMER');

        // Courier travels to customer (30s simulation duration)
        progressB.current += delta / 30000;
        if (progressB.current >= 1) progressB.current = 1;

        if (routeB) {
          const len = length(routeB);
          // Clamp to 0.999 to avoid exactly hitting the end before backend is COMPLETED
          const pos = along(routeB, Math.min(progressB.current, 0.999) * len).geometry.coordinates;
          setCourierPosition(pos as [number, number]);
        } else {
          setCourierPosition(startPoint);
        }

        try {
          sessionStorage.setItem(storageKey, JSON.stringify({
            progressA: 1,
            progressB: progressB.current,
            hasReachedRestaurant: true
          }));
        } catch {
          // ignore
        }
      }

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animationFrameRef.current = requestAnimationFrame(animate);

    return () => {
      isAnimating = false;
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    };
  }, [isActive, order.status, routeA, routeB, startPoint, endPoint, courierStart, storageKey]);

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
