import { useRef, useEffect } from 'react';
import type { FC } from 'react';
import type { Order } from '../types/order.types';
import Map, { Source, Layer, Marker, NavigationControl } from 'react-map-gl/maplibre';
import type { MapRef } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import { useCourierSimulation } from '../hooks/useCourierSimulation';

interface OrderLiveMapProps {
  order: Order;
}

const OrderLiveMap: FC<OrderLiveMapProps> = ({ order }) => {
  const maptilerKey = import.meta.env.VITE_MAPTILER_API_KEY;
  const mapRef = useRef<MapRef>(null);

  const {
    courierPosition,
    routeA,
    routeB,
    startPoint,
    endPoint,
    courierStage
  } = useCourierSimulation({
    order,
    isActive: true
  });

  // Center the map so it frames the active stage
  useEffect(() => {
    if (!mapRef.current || !startPoint || !endPoint) return;
    
    // Fit bounds based on which stage we are in
    const activeRoute = (courierStage === 'TO_CUSTOMER' || courierStage === 'ARRIVED') ? routeB : routeA;
    if (!activeRoute) return;

    const coords = activeRoute.geometry.coordinates;
    if (!coords || coords.length === 0) return;

    let minLng = coords[0][0];
    let maxLng = coords[0][0];
    let minLat = coords[0][1];
    let maxLat = coords[0][1];

    for (const [lng, lat] of coords) {
      if (lng < minLng) minLng = lng;
      if (lng > maxLng) maxLng = lng;
      if (lat < minLat) minLat = lat;
      if (lat > maxLat) maxLat = lat;
    }

    try {
      mapRef.current.fitBounds(
        [[minLng, minLat], [maxLng, maxLat]],
        { padding: 80, duration: 1500, maxZoom: 15 }
      );
    } catch (e) {
      console.warn('Map fitBounds failed:', e);
    }
  }, [courierStage, routeA, routeB, startPoint, endPoint]);

  if (!startPoint || !endPoint) {
    return null; // Silent fallback if no coordinates
  }

  const mapStyle = maptilerKey 
    ? `https://api.maptiler.com/maps/basic-v2/style.json?key=${maptilerKey}`
    : {
        version: 8,
        sources: {
          osm: {
            type: 'raster',
            tiles: ['https://a.tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
            attribution: '&copy; OpenStreetMap Contributors',
          }
        },
        layers: [
          {
            id: 'osm',
            type: 'raster',
            source: 'osm',
            paint: {
              'raster-saturation': -1,
              'raster-opacity': 0.8
            }
          }
        ]
      } as any;

  // Determine Overlay content
  let overlayTitle = "PREPARING";
  let overlayDescription = "Order is being packed";

  if (courierStage === 'PREPARING') {
    if (order.status === 'PENDING') {
      overlayTitle = "ORDER PLACED";
      overlayDescription = "Waiting for restaurant confirmation";
    } else if (order.status === 'ACCEPTED') {
      overlayTitle = "ACCEPTED";
      overlayDescription = "Getting ready to prepare";
    } else {
      overlayTitle = "PREPARING";
      overlayDescription = "The kitchen is working on your order";
    }
  } else if (courierStage === 'TO_RESTAURANT') {
    overlayTitle = "PICKUP IN PROGRESS";
    overlayDescription = "Courier is heading to the restaurant";
  } else if (courierStage === 'AT_RESTAURANT') {
    overlayTitle = "AT RESTAURANT";
    overlayDescription = "Courier is picking up your order";
  } else if (courierStage === 'TO_CUSTOMER') {
    overlayTitle = "OUT FOR DELIVERY";
    overlayDescription = "Your courier is on the way";
  } else if (courierStage === 'ARRIVED') {
    overlayTitle = "DELIVERED";
    overlayDescription = "Enjoy your meal!";
  } else if (courierStage === 'CANCELLED') {
    overlayTitle = "CANCELLED";
    overlayDescription = "Order was cancelled";
  }

  const isStageA = courierStage === 'TO_RESTAURANT' || courierStage === 'AT_RESTAURANT' || courierStage === 'PREPARING';

  return (
    <div className="relative w-full h-[500px] sm:h-[600px] bg-background overflow-hidden border-y border-border-default">
      
      {/* Map Status Overlay */}
      <div className="absolute top-6 left-6 z-20 max-w-[280px]">
        <div className="bg-surface shadow-elevated border border-border-default p-5 transition-all">
          <h3 className="font-bold text-text-primary text-sm uppercase tracking-widest mb-1">
            {overlayTitle}
          </h3>
          <p className="text-sm text-text-secondary">
            {overlayDescription}
          </p>
        </div>
      </div>

      <Map
        ref={mapRef}
        initialViewState={{
          longitude: startPoint[0],
          latitude: startPoint[1],
          zoom: 13
        }}
        mapStyle={mapStyle}
        attributionControl={false}
      >
        <NavigationControl position="bottom-right" />

        {/* Route A (Courier -> Restaurant) */}
        {routeA && (
          <Source id="route-a" type="geojson" data={routeA}>
            <Layer 
              id="line-a" 
              type="line" 
              paint={{
                'line-color': isStageA ? '#191918' : '#9ca3af',
                'line-width': isStageA ? 3 : 2,
                'line-dasharray': [2, 2],
                'line-opacity': isStageA ? 1 : 0.4
              }} 
            />
          </Source>
        )}

        {/* Route B (Restaurant -> Customer) */}
        {routeB && (
          <Source id="route-b" type="geojson" data={routeB}>
            <Layer 
              id="line-b" 
              type="line" 
              paint={{
                'line-color': !isStageA ? '#191918' : '#9ca3af',
                'line-width': !isStageA ? 3 : 2,
                'line-dasharray': [2, 2],
                'line-opacity': !isStageA ? 1 : 0.4
              }} 
            />
          </Source>
        )}

        {/* Restaurant Marker */}
        <Marker longitude={startPoint[0]} latitude={startPoint[1]} anchor="center">
          <div className="relative flex justify-center items-center">
            <div className="absolute bottom-full mb-1 bg-surface border border-border-default text-text-primary px-3 py-1 text-[10px] uppercase font-bold tracking-widest shadow-subtle whitespace-nowrap">
              ● RESTAURANT
            </div>
            <div className="h-4 w-4 bg-surface border-4 border-text-primary rounded-full shadow-subtle" />
          </div>
        </Marker>

        {/* Destination Marker */}
        <Marker longitude={endPoint[0]} latitude={endPoint[1]} anchor="center">
          <div className="relative flex justify-center items-center">
            <div className="absolute bottom-full mb-1 bg-text-primary text-surface px-3 py-1 text-[10px] uppercase font-bold tracking-widest shadow-subtle whitespace-nowrap">
              ● YOU
            </div>
            <div className="h-3 w-3 bg-text-primary rounded-full shadow-subtle" />
          </div>
        </Marker>

        {/* Courier Marker */}
        {courierPosition && courierStage !== 'CANCELLED' && (
          <Marker longitude={courierPosition[0]} latitude={courierPosition[1]} anchor="center">
            <div className="relative flex items-center justify-center">
              {courierStage === 'TO_CUSTOMER' && (
                <div className="absolute w-16 h-16 border-2 border-text-primary rounded-full animate-ping opacity-20" />
              )}
              <div className="relative z-10 w-10 h-10 bg-text-primary text-surface rounded-full flex items-center justify-center shadow-floating transition-transform duration-300">
                <span className="text-xl">🚴</span>
              </div>
            </div>
          </Marker>
        )}
      </Map>
    </div>
  );
};

export default OrderLiveMap;
