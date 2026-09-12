import { initializeApp } from 'firebase/app';
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signOut,
} from 'firebase/auth';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

export const isFirebaseAuthEnabled =
  import.meta.env.VITE_FIREBASE_AUTH_ENABLED === 'true' &&
  Object.values(firebaseConfig).every(Boolean);

const app = isFirebaseAuthEnabled ? initializeApp(firebaseConfig) : null;
const firebaseAuth = app ? getAuth(app) : null;

export const signInWithGoogle = async (): Promise<string> => {
  if (!firebaseAuth) {
    throw new Error('Google sign-in is not configured.');
  }

  const provider = new GoogleAuthProvider();
  provider.setCustomParameters({ prompt: 'select_account' });
  const credential = await signInWithPopup(firebaseAuth, provider);
  return credential.user.getIdToken(true);
};

export const signOutFromFirebase = async (): Promise<void> => {
  if (firebaseAuth) {
    await signOut(firebaseAuth);
  }
};

export const firebaseAuthErrorMessage = (error: unknown): string => {
  const code =
    typeof error === 'object' && error !== null && 'code' in error
      ? String(error.code)
      : '';

  if (code === 'auth/popup-closed-by-user' || code === 'auth/cancelled-popup-request') {
    return 'Google sign-in was cancelled.';
  }
  if (code === 'auth/popup-blocked') {
    return 'Your browser blocked the Google sign-in popup.';
  }
  if (code === 'auth/network-request-failed') {
    return 'Google sign-in could not reach Firebase. Check your connection.';
  }
  return 'Unable to sign in with Google. Please try again.';
};
