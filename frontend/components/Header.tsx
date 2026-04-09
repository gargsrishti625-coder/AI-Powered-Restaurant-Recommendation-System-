'use client';

export default function Header() {
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-100 shadow-sm">
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-1">
          <span className="text-[#e23744] font-extrabold text-xl tracking-tight">Zomato</span>
          <span className="text-gray-800 font-extrabold text-xl tracking-tight"> AI</span>
        </div>

        {/* Nav */}
        <nav className="hidden sm:flex items-center gap-8 text-sm font-medium text-gray-600">
          <a href="#" className="text-[#e23744] border-b-2 border-[#e23744] pb-0.5">Explore</a>
          <a href="#" className="hover:text-gray-900 transition-colors">Dining</a>
          <a href="#" className="hover:text-gray-900 transition-colors">Nightlife</a>
        </nav>

        {/* Icons */}
        <div className="flex items-center gap-3 text-gray-500">
          <button className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors" aria-label="Location">
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
          </button>
          <button className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors" aria-label="Profile">
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
}
