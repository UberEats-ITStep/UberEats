import { useMemo, useState, type FC } from 'react';
import Map, { NavigationControl } from 'react-map-gl/maplibre';
import type { StyleSpecification } from 'maplibre-gl';
import { Button, Input } from '../../../components/common';
import 'maplibre-gl/dist/maplibre-gl.css';

export interface ResolvedLocation { formattedAddress: string; street: string; building: string; latitude: number; longitude: number; }
interface Props { initialLatitude?: number; initialLongitude?: number; initialAddress?: string; onResolve: (location: ResolvedLocation) => void; }

const LocationPicker: FC<Props> = ({ initialLatitude = 50.62, initialLongitude = 26.25, initialAddress = '', onResolve }) => {
  const key = import.meta.env.VITE_MAPTILER_API_KEY;
  const [query, setQuery] = useState(initialAddress);
  const [viewState, setViewState] = useState({ latitude: initialLatitude, longitude: initialLongitude, zoom: 15 });
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const mapStyle = useMemo(() => key ? `https://api.maptiler.com/maps/basic-v2/style.json?key=${key}` : ({ version: 8, sources: { osm: { type: 'raster', tiles: ['https://a.tile.openstreetmap.org/{z}/{x}/{y}.png'], tileSize: 256 } }, layers: [{ id: 'osm', type: 'raster', source: 'osm' }] } as StyleSpecification), [key]);

  type GeoFeature = { center?: [number, number]; address?: string; text?: string; place_name?: string; place_type?: string[] };
  const accept = (feature: GeoFeature) => {
    const latitude = feature.center?.[1] ?? viewState.latitude;
    const longitude = feature.center?.[0] ?? viewState.longitude;
    const building = feature.address || '';
    const street = feature.text || feature.place_name?.split(',')[0] || '';
    const formattedAddress = feature.place_name || [street, building].filter(Boolean).join(' ');
    setQuery(formattedAddress);
    setViewState((current) => ({ ...current, latitude, longitude, zoom: 16 }));
    onResolve({ formattedAddress, street, building, latitude, longitude });
    setMessage('Location confirmed.');
  };

  const request = async (url: string) => {
    setBusy(true); setMessage(null);
    try {
      const response = await fetch(url);
      const data = await response.json();
      if (!data.features?.length) throw new Error('No matching address found.');
      return data.features;
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Address lookup failed.'); return null; }
    finally { setBusy(false); }
  };

  const search = async () => {
    if (!query.trim()) return;
    if (!key) { setMessage('Address search needs a MapTiler API key. Move the map and confirm the pin instead.'); return; }
    const features = await request(`https://api.maptiler.com/geocoding/${encodeURIComponent(query.trim())}.json?key=${key}&limit=1`);
    if (features) accept(features[0]);
  };

  const confirmPin = async () => {
    if (!key) { onResolve({ formattedAddress: query.trim(), street: query.trim(), building: '', latitude: viewState.latitude, longitude: viewState.longitude }); setMessage('Map location confirmed.'); return; }
    const features = await request(`https://api.maptiler.com/geocoding/${viewState.longitude},${viewState.latitude}.json?key=${key}`);
    if (features) accept(features.find((item: GeoFeature) => item.place_type?.includes('address')) || features[0]);
  };

  return <div className="space-y-3">
    <div className="flex flex-col gap-2 sm:flex-row"><Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search street and city" aria-label="Search delivery address" /><Button type="button" variant="outline" isLoading={busy} onClick={search}>Search</Button></div>
    <div className="relative h-64 overflow-hidden border border-border-default bg-muted sm:h-72">
      <Map {...viewState} onMove={(e) => setViewState(e.viewState)} mapStyle={mapStyle} attributionControl={false}><NavigationControl position="top-right" /><div className="pointer-events-none absolute left-1/2 top-1/2 z-10 -translate-x-1/2 -translate-y-full"><div className="h-8 w-8 rounded-full border-4 border-surface bg-primary shadow-elevated"><div className="m-auto mt-2 h-2 w-2 rounded-full bg-surface" /></div><div className="mx-auto h-5 w-1 bg-primary" /></div></Map>
      <Button type="button" size="sm" className="absolute bottom-4 left-1/2 z-20 -translate-x-1/2 whitespace-nowrap" onClick={confirmPin} isLoading={busy}>Confirm pin</Button>
    </div>
    {message && <p className="text-xs text-text-secondary" role="status">{message}</p>}
  </div>;
};
export default LocationPicker;
