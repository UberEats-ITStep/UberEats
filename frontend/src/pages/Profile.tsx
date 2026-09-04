import { useEffect, useState, type FC } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Alert, Avatar, Badge, Button, Card, FormField, Input, LoadingState, SectionContainer } from '../components/common';
import ChangePasswordForm from '../features/auth/components/ChangePasswordForm';
import AddressModal from '../features/auth/components/AddressModal';
import { authApi } from '../features/auth/api/authApi';
import type { AvatarOption, DeliveryAddress, DeliveryAddressInput } from '../features/auth/types/auth.types';

const Profile: FC = () => {
  const { profile, refreshProfile } = useAuth();
  const [phone, setPhone] = useState(profile?.phone_number || '');
  const [avatar, setAvatar] = useState(profile?.avatar || 'avatar_01');
  const [avatars, setAvatars] = useState<AvatarOption[]>([]);
  const [addresses, setAddresses] = useState<DeliveryAddress[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingProfile, setSavingProfile] = useState(false);
  const [workingId, setWorkingId] = useState<number | null>(null);
  const [editing, setEditing] = useState<DeliveryAddress | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [notice, setNotice] = useState<{ kind: 'success' | 'error'; message: string } | null>(null);
  const loadAddresses = async () => setAddresses(await authApi.getAddresses());

  useEffect(() => { Promise.all([authApi.getAvatarOptions(), authApi.getAddresses()]).then(([options, saved]) => { setAvatars(options); setAddresses(saved); }).catch(() => setNotice({ kind: 'error', message: 'Some profile details could not be loaded.' })).finally(() => setLoading(false)); }, []);
  const saveProfile = async (event: React.FormEvent) => { event.preventDefault(); setSavingProfile(true); setNotice(null); try { await authApi.updateProfile({ phone_number: phone.trim() || null, avatar }); await refreshProfile(); setNotice({ kind: 'success', message: 'Profile updated.' }); } catch (err: unknown) { const response = (err as { response?: { data?: { phone_number?: string[] } } }).response; setNotice({ kind: 'error', message: response?.data?.phone_number?.[0] || 'Profile could not be updated.' }); } finally { setSavingProfile(false); } };
  const saveAddress = async (data: DeliveryAddressInput) => { if (editing) await authApi.updateAddress(editing.id, data); else await authApi.createAddress(data); await loadAddresses(); await refreshProfile(); setNotice({ kind: 'success', message: editing ? 'Delivery address updated.' : 'Delivery address added.' }); };
  const setDefault = async (id: number) => { setWorkingId(id); setNotice(null); try { await authApi.setDefaultAddress(id); await loadAddresses(); await refreshProfile(); setNotice({ kind: 'success', message: 'Default delivery address updated.' }); } catch { setNotice({ kind: 'error', message: 'Default address could not be changed.' }); } finally { setWorkingId(null); } };
  const remove = async (address: DeliveryAddress) => { if (!window.confirm(`Delete ${address.label}?`)) return; setWorkingId(address.id); try { await authApi.deleteAddress(address.id); await loadAddresses(); await refreshProfile(); setNotice({ kind: 'success', message: 'Delivery address deleted.' }); } catch { setNotice({ kind: 'error', message: 'Delivery address could not be deleted.' }); } finally { setWorkingId(null); } };

  if (loading) return <SectionContainer width="content" padding="lg"><LoadingState message="Loading your profile…" /></SectionContainer>;
  return <SectionContainer width="content" padding="lg" className="pb-16">
    <div className="mb-8"><p className="text-caption">Account management</p><h1 className="mt-2 text-page-title">Your profile</h1><p className="mt-2 text-body">Keep your contact details and favorite delivery places up to date.</p></div>
    {notice && <Alert className="mb-6" variant={notice.kind} message={notice.message} />}
    <div className="space-y-8">
      <Card elevation="subtle" padding="lg"><form onSubmit={saveProfile} className="space-y-7">
        <div><h2 className="text-section-title">Profile information</h2><p className="mt-1 text-body">Choose how you appear and where we can reach you.</p></div>
        <FormField label="Phone number" id="profile-phone" optionalLabel><Input id="profile-phone" type="tel" inputMode="tel" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+380501234567" /></FormField>
        <fieldset><legend className="text-label">Choose an avatar</legend><div className="mt-3 grid grid-cols-3 gap-3 sm:grid-cols-6">{avatars.map((option) => { const selected = avatar === option.id; return <button key={option.id} type="button" onClick={() => setAvatar(option.id)} aria-pressed={selected} className={`group flex flex-col items-center gap-2 border p-3 transition duration-200 ${selected ? 'scale-[1.03] border-primary bg-secondary shadow-subtle' : 'border-border-default hover:border-text-muted'}`}><Avatar avatarId={option.id} size="lg" className={selected ? 'ring-2 ring-primary ring-offset-2' : 'transition-transform group-hover:scale-105'} /><span className="text-xs font-medium">{option.label}</span>{selected && <span className="text-[10px] uppercase tracking-widest">Selected</span>}</button>; })}</div></fieldset>
        <div className="flex justify-end"><Button type="submit" isLoading={savingProfile} disabled={phone === (profile?.phone_number || '') && avatar === profile?.avatar}>Save profile</Button></div>
      </form></Card>
      <section><div className="mb-4 flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-end"><div><p className="text-caption">Saved places</p><h2 className="mt-1 text-section-title">Delivery addresses</h2></div><Button onClick={() => { setEditing(null); setModalOpen(true); }}>+ Add another address</Button></div>
        {addresses.length === 0 ? <Card padding="lg" className="border-dashed text-center"><p className="font-medium">No saved delivery addresses yet.</p><p className="mt-1 text-body">Add a place to make checkout faster.</p></Card> : <div className="grid gap-4 md:grid-cols-2">{addresses.map((address) => <Card key={address.id} padding="md" className={address.is_default ? 'border-2 border-primary' : ''}><div className="flex items-start justify-between gap-4"><div><div className="flex items-center gap-2"><h3 className="font-bold uppercase tracking-wide">{address.label}</h3>{address.is_default && <Badge variant="success" size="sm">Default</Badge>}</div><p className="mt-3 text-sm font-medium">{address.formatted_address}</p>{address.apartment && <p className="mt-1 text-xs text-text-secondary">Apartment {address.apartment}{address.entrance ? ` · Entrance ${address.entrance}` : ''}</p>}</div><span aria-hidden="true" className="text-xl">{address.is_default ? '✓' : '○'}</span></div><div className="mt-6 flex flex-wrap gap-2 border-t border-border-default pt-4">{!address.is_default && <Button size="sm" variant="outline" isLoading={workingId === address.id} onClick={() => setDefault(address.id)}>Set as default</Button>}<Button size="sm" variant="ghost" disabled={workingId === address.id} onClick={() => { setEditing(address); setModalOpen(true); }}>Edit</Button><Button size="sm" variant="ghost" disabled={workingId === address.id} onClick={() => remove(address)}>Delete</Button></div></Card>)}</div>}
      </section>
      <ChangePasswordForm />
    </div>
    <AddressModal key={`${editing?.id ?? 'new'}-${modalOpen}`} isOpen={modalOpen} address={editing} onClose={() => setModalOpen(false)} onSave={saveAddress} />
  </SectionContainer>;
};
export default Profile;
