import { useEffect, useState } from 'react';
import api from '../services/api';

export default function HomePage() {
  const [status, setStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');

  useEffect(() => {
    // Attempt to ping the backend root or health endpoint
    api.get('/')
      .then(() => setStatus('connected'))
      .catch(() => setStatus('disconnected'));
  }, []);

  return (
    <div className="max-w-2xl mx-auto mt-20 px-6">
      <div className="mb-8">
        <h1 className="text-[40px] font-bold text-[#37352f] tracking-tight leading-tight mb-2">
          System Status
        </h1>
        <p className="text-[#73726e] text-lg">
          Monitoring the connection to the Django backend.
        </p>
      </div>

      <div className="border border-[#e9e9e7] rounded-lg bg-white shadow-sm overflow-hidden">
        <div className="border-b border-[#e9e9e7] px-6 py-4 flex items-center justify-between bg-[#fbfbfa]">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-[#73726e]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
            </svg>
            <span className="font-medium text-[#37352f]">API Server</span>
          </div>
          <div className="flex items-center gap-2">
            {status === 'checking' && (
              <span className="flex items-center gap-2 text-sm text-[#73726e]">
                <span className="w-2 h-2 rounded-full bg-[#e3e2e0] animate-pulse"></span>
                Checking...
              </span>
            )}
            {status === 'connected' && (
              <span className="flex items-center gap-2 text-sm text-[#73726e]">
                <span className="w-2 h-2 rounded-full bg-[#0f7b6c]"></span>
                Connected
              </span>
            )}
            {status === 'disconnected' && (
              <span className="flex items-center gap-2 text-sm text-[#73726e]">
                <span className="w-2 h-2 rounded-full bg-[#eb5757]"></span>
                Disconnected
              </span>
            )}
          </div>
        </div>
        <div className="px-6 py-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-[#73726e]">Endpoint URL</span>
              <span className="text-[#eb5757] font-mono bg-[#f1f1ef] px-1.5 py-0.5 rounded">http://localhost:8000/api</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-[#73726e]">Environment</span>
              <span className="text-[#37352f]">Development</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-[#73726e]">Last Checked</span>
              <span className="text-[#37352f]">{new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </div>
      </div>
      
      {status === 'disconnected' && (
        <div className="mt-6 flex items-start gap-3 p-4 rounded-md bg-[#fdfaf6] border border-[#f0e1cf]">
          <span className="text-xl leading-none">💡</span>
          <div className="text-sm text-[#37352f] leading-relaxed">
            <span className="font-medium">Backend is not running.</span> To fix this, start the Django development server using <code className="bg-[#f1f1ef] text-[#eb5757] px-1.5 py-0.5 rounded text-xs font-mono">python manage.py runserver</code> in your backend directory.
          </div>
        </div>
      )}
    </div>
  );
}
