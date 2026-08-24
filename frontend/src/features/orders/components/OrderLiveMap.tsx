import { useMemo, useRef, useEffect } from 'react';
import type { FC } from 'react';
import type { Order } from '../types/order.types';
import Map, { Source, Layer, Marker, NavigationControl } from 'react-map-gl/maplibre';
import type { MapRef } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import { useCourierSimulation } from '../hooks/useCourierSimulation';
import { LIFECYCLE_STEPS, getActiveStepIndex } from '../utils/order.utils';

interface OrderLiveMapProps {
  order: Order;
}

const OrderLiveMap: FC<OrderLiveMapProps> = ({ order }) => {
  const maptilerKey = import.meta.env.VITE_MAPTILER_API_KEY;
  const isDelivering = order.status === 'DELIVERING';
  const mapRef = useRef<MapRef>(null);

  const {
    courierPosition,
    routeGeoJSON,
    startPoint,
    endPoint,
  } = useCourierSimulation({
    order,
    isActive: isDelivering,
    maptilerKey
  });

  useEffect(() => {
    if (mapRef.current && startPoint && endPoint) {
      const minLng = Math.min(startPoint[0], endPoint[0]);
      const maxLng = Math.max(startPoint[0], endPoint[0]);
      const minLat = Math.min(startPoint[1], endPoint[1]);
      const maxLat = Math.max(startPoint[1], endPoint[1]);
      
      const lngDiff = maxLng - minLng;
      const latDiff = maxLat - minLat;
      
      // If points are identical, just center without fitBounds
      if (lngDiff === 0 && latDiff === 0) {
        mapRef.current.flyTo({ center: startPoint, zoom: 15 });
        return;
      }
      
      mapRef.current.fitBounds(
        [[minLng, minLat], [maxLng, maxLat]],
        { padding: 80, duration: 1500, maxZoom: 15 }
      );
    }
  }, [startPoint, endPoint]);

  if (!startPoint || !endPoint) {
    return null; // Silent fallback if no coordinates
  }

  // Use basic-v2 as it's the most reliable standard MapTiler style, 
  // or fallback to OSM with corrected contrast so it doesn't look like a gray blob.
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

  const viewState = useMemo(() => {
    return {
      longitude: (startPoint[0] + endPoint[0]) / 2,
      latitude: (startPoint[1] + endPoint[1]) / 2,
      zoom: 13,
      pitch: 45
    };
  }, [startPoint, endPoint]);

  const activeIndex = getActiveStepIndex(order.status);
  const activeStep = LIFECYCLE_STEPS[activeIndex];

  return (
    <div className="relative w-full h-[500px] sm:h-[600px] bg-background overflow-hidden border-y border-border-default">
      {/* Editorial Map Overlay elements */}
      <div className="absolute top-0 left-0 w-full h-32 bg-gradient-to-b from-surface/80 to-transparent z-10 pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-full h-32 bg-gradient-to-t from-surface/80 to-transparent z-10 pointer-events-none" />
      
      {/* Floating Status Card */}
      <div className="absolute top-6 left-6 z-20 bg-surface border border-border-default shadow-elevated p-4 max-w-[250px]">
        <p className="text-[10px] uppercase font-bold tracking-widest text-text-muted mb-1">
          Live Tracking
        </p>
        <p className="text-sm font-medium text-text-primary">
          {activeStep?.title || order.status}
        </p>
      </div>

      <Map
        ref={mapRef}
        initialViewState={viewState}
        mapStyle={mapStyle}
        attributionControl={false}
      >
        <NavigationControl position="bottom-right" />
        
        {/* Route Line */}
        {routeGeoJSON && (
          <>
            <Source id="route-bg" type="geojson" data={routeGeoJSON}>
              <Layer 
                id="route-line-bg" 
                type="line" 
                paint={{
                  'line-color': '#FFFFFF',
                  'line-width': 8,
                  'line-opacity': 0.8
                }} 
              />
            </Source>
            <Source id="route" type="geojson" data={routeGeoJSON}>
              <Layer 
                id="route-line" 
                type="line" 
                paint={{
                  'line-color': '#191918',
                  'line-width': 3,
                  'line-dasharray': [2, 2],
                  'line-opacity': 0.8
                }} 
              />
            </Source>
          </>
        )}

        {/* Restaurant Marker */}
        <Marker longitude={startPoint[0]} latitude={startPoint[1]} anchor="bottom">
          <div className="flex flex-col items-center">
            <div className="bg-surface border border-border-default text-text-primary px-3 py-1 text-[10px] uppercase font-bold tracking-widest shadow-subtle mb-1 whitespace-nowrap">
              Restaurant
            </div>
            <div className="h-4 w-4 bg-surface border-4 border-text-primary rounded-full shadow-subtle" />
          </div>
        </Marker>

        {/* Destination Marker */}
        <Marker longitude={endPoint[0]} latitude={endPoint[1]} anchor="bottom">
          <div className="flex flex-col items-center">
            <div className="bg-text-primary text-surface px-3 py-1 text-[10px] uppercase font-bold tracking-widest shadow-subtle mb-1 whitespace-nowrap">
              Destination
            </div>
            <div className="h-3 w-3 bg-text-primary rounded-full shadow-subtle" />
          </div>
        </Marker>

        {/* Courier Marker */}
        {courierPosition && (
          <Marker longitude={courierPosition[0]} latitude={courierPosition[1]} anchor="center">
            <div className="relative flex items-center justify-center">
              {isDelivering && (
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
