import { Outlet } from 'react-router-dom';

export default function MainLayout() {
  return (
    <div className="min-h-screen bg-white text-[#37352f] selection:bg-[#cce2ff] font-sans">
      <header className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-[#e9e9e7]">
        <div className="max-w-5xl mx-auto px-6 h-12 flex items-center gap-2 text-sm font-medium">
          <span className="bg-[#f1f1ef] px-2 py-0.5 rounded text-[#73726e]">UberEats Clone</span>
          <span className="text-[#e9e9e7]">/</span>
          <span>System Status</span>
        </div>
      </header>

      <main>
        <Outlet />
      </main>
    </div>
  );
}
