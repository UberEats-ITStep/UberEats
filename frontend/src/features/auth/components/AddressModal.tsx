import { useState, type FC } from 'react';
import { Button, FormField, Input, Modal, Textarea } from '../../../components/common';
import type { DeliveryAddress, DeliveryAddressInput } from '../types/auth.types';
import LocationPicker, { type ResolvedLocation } from './LocationPicker';

interface Props { isOpen: boolean; address?: DeliveryAddress | null; onClose: () => void; onSave: (data: DeliveryAddressInput) => Promise<void>; }
const empty: DeliveryAddressInput = { label: '', formatted_address: '', street: '', building: '', apartment: '', entrance: '', floor: null, delivery_notes: '', contact_phone: '', latitude: null, longitude: null };

const AddressModal: FC<Props> = ({ isOpen, address, onClose, onSave }) => {
  const [form, setForm] = useState<DeliveryAddressInput>(address ? { label: address.label, formatted_address: address.formatted_address, street: address.street, building: address.building, apartment: address.apartment, entrance: address.entrance, floor: address.floor, delivery_notes: address.delivery_notes, contact_phone: address.contact_phone, latitude: address.latitude, longitude: address.longitude } : empty);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const set = (key: keyof DeliveryAddressInput, value: string | number | null) => setForm((current) => ({ ...current, [key]: value }));
  const resolve = (location: ResolvedLocation) => setForm((current) => ({ ...current, formatted_address: location.formattedAddress, street: location.street, building: location.building, latitude: location.latitude.toFixed(6), longitude: location.longitude.toFixed(6) }));
  const submit = async () => {
    if (!form.label.trim() || !form.formatted_address.trim() || !form.street.trim() || !form.building.trim()) { setError('Choose a precise address and add a label before saving.'); return; }
    setSaving(true); setError(null);
    try { await onSave({ ...form, label: form.label.trim(), formatted_address: form.formatted_address.trim(), street: form.street.trim(), building: form.building.trim() }); onClose(); }
    catch (err: unknown) { const data = (err as { response?: { data?: Record<string, string[]> } }).response?.data; setError(data ? Object.values(data).flat().join(' ') : 'Could not save this address.'); }
    finally { setSaving(false); }
  };
  return <Modal isOpen={isOpen} onClose={saving ? () => undefined : onClose} title={address ? 'Edit delivery address' : 'Add delivery address'} footer={<div className="flex justify-end gap-2"><Button variant="ghost" onClick={onClose} disabled={saving}>Cancel</Button><Button onClick={submit} isLoading={saving}>Save address</Button></div>}>
    <div className="max-h-[70vh] space-y-5 overflow-y-auto pr-1">
      {error && <p className="border border-border-default bg-secondary p-3 text-sm" role="alert">{error}</p>}
      <FormField label="Label" id="address-label" required helperText="For example: Home, Work or University"><Input id="address-label" value={form.label} onChange={(e) => set('label', e.target.value)} maxLength={100} /></FormField>
      <LocationPicker key={address?.id ?? 'new'} initialAddress={form.formatted_address} initialLatitude={Number(form.latitude) || undefined} initialLongitude={Number(form.longitude) || undefined} onResolve={resolve} />
      {form.formatted_address && <div className="border-l-2 border-primary pl-3"><p className="text-caption">Selected address</p><p className="mt-1 text-sm font-medium">{form.formatted_address}</p></div>}
      <div className="grid grid-cols-2 gap-3"><FormField label="Street" id="address-street" required><Input id="address-street" value={form.street} onChange={(e) => set('street', e.target.value)} /></FormField><FormField label="Building" id="address-building" required><Input id="address-building" value={form.building} onChange={(e) => set('building', e.target.value)} /></FormField></div>
      <div className="grid grid-cols-3 gap-3"><FormField label="Apartment" id="address-apartment" optionalLabel><Input id="address-apartment" value={form.apartment} onChange={(e) => set('apartment', e.target.value)} /></FormField><FormField label="Entrance" id="address-entrance" optionalLabel><Input id="address-entrance" value={form.entrance} onChange={(e) => set('entrance', e.target.value)} /></FormField><FormField label="Floor" id="address-floor" optionalLabel><Input id="address-floor" type="number" min="1" max="100" value={form.floor ?? ''} onChange={(e) => set('floor', e.target.value ? Number(e.target.value) : null)} /></FormField></div>
      <FormField label="Delivery notes" id="address-notes" optionalLabel><Textarea id="address-notes" value={form.delivery_notes} onChange={(e) => set('delivery_notes', e.target.value)} maxLength={500} rows={2} /></FormField>
    </div>
  </Modal>;
};
export default AddressModal;
