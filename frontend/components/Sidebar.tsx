'use client';

import { useState, useEffect, useRef } from 'react';
import type { RecommendRequest } from '@/lib/types';
import { fetchLocations, fetchCuisines } from '@/lib/api';

interface SidebarProps {
  onSearch: (req: RecommendRequest) => void;
  loading: boolean;
  activeFilters: RecommendRequest | null;
  onClearFilter: (key: keyof RecommendRequest) => void;
}

const BUDGET_OPTIONS = [
  { value: 'low', label: 'Low', sub: 'Under ₹700', icon: '₹' },
  { value: 'medium', label: 'Mid Range', sub: '₹700–2000', icon: '₹₹' },
  { value: 'high', label: 'Premium', sub: '₹2000+', icon: '₹₹₹' },
] as const;

export default function Sidebar({ onSearch, loading, activeFilters, onClearFilter }: SidebarProps) {
  const [locations, setLocations] = useState<string[]>([]);
  const [allCuisines, setAllCuisines] = useState<string[]>([]);
  const [location, setLocation] = useState('');
  const [budget, setBudget] = useState<'low' | 'medium' | 'high'>('medium');
  const [selectedCuisines, setSelectedCuisines] = useState<Set<string>>(new Set());
  const [minRating, setMinRating] = useState(3.5);
  const [additional, setAdditional] = useState('');
  const [cuisineOpen, setCuisineOpen] = useState(false);
  const [cuisineSearch, setCuisineSearch] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchLocations().then(setLocations).catch(() => {});
    fetchCuisines().then(setAllCuisines).catch(() => {});
  }, []);

  // Close cuisine dropdown on outside click
  useEffect(() => {
    function handler(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setCuisineOpen(false);
      }
    }
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const filteredCuisines = allCuisines.filter(c =>
    c.toLowerCase().includes(cuisineSearch.toLowerCase())
  );

  function toggleCuisine(c: string) {
    setSelectedCuisines(prev => {
      const next = new Set(prev);
      next.has(c) ? next.delete(c) : next.add(c);
      return next;
    });
  }

  function removeCuisine(c: string) {
    setSelectedCuisines(prev => { const n = new Set(prev); n.delete(c); return n; });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!location) return;
    onSearch({
      location,
      budget,
      cuisine: selectedCuisines.size > 0 ? [...selectedCuisines].join(', ') : null,
      min_rating: minRating,
      additional_preferences: additional.trim() || null,
    });
  }

  const budgetLabel = BUDGET_OPTIONS.find(b => b.value === budget);

  return (
    <aside className="w-full lg:w-[320px] shrink-0">
      {/* Connoisseur card */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        {/* Header */}
        <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-purple-100 flex items-center justify-center text-purple-700 shrink-0">
            🍽️
          </div>
          <div>
            <div className="text-sm font-bold text-gray-900">The Connoisseur</div>
            <div className="text-xs text-gray-400">Your Digital Sommelier</div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-5">
          {/* Smart Filters label */}
          <div className="flex items-center gap-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2a1 1 0 01-.293.707L13 13.414V19a1 1 0 01-.553.894l-4 2A1 1 0 017 21v-7.586L3.293 6.707A1 1 0 013 6V4z"/>
            </svg>
            Smart Filters
          </div>

          {/* Active criteria chips */}
          {activeFilters && (
            <div className="space-y-2">
              <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Active Criteria</div>
              <div className="flex flex-col gap-1.5">
                <ActiveChip icon="📍" label={activeFilters.location} onRemove={() => onClearFilter('location')} />
                <ActiveChip icon="💰" label={`Budget: ${BUDGET_OPTIONS.find(b=>b.value===activeFilters.budget)?.icon ?? ''}`} onRemove={() => onClearFilter('budget')} />
                {activeFilters.cuisine && (
                  <ActiveChip icon="🍴" label={`Cuisine: ${activeFilters.cuisine}`} onRemove={() => onClearFilter('cuisine')} />
                )}
              </div>
            </div>
          )}

          {/* Location */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Location *</label>
            <select
              value={location}
              onChange={e => setLocation(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl border border-gray-200 bg-white text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-purple-300 focus:border-purple-400 appearance-none cursor-pointer"
              required
            >
              <option value="" disabled>Select a location…</option>
              {locations.map(l => <option key={l} value={l}>{l}</option>)}
            </select>
          </div>

          {/* Budget */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Budget</label>
            <div className="grid grid-cols-3 gap-2">
              {BUDGET_OPTIONS.map(opt => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setBudget(opt.value)}
                  className={`py-2 px-1 rounded-xl border text-center transition-all ${
                    budget === opt.value
                      ? 'border-[#e23744] bg-red-50 text-[#e23744]'
                      : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                  }`}
                >
                  <div className="text-sm font-bold">{opt.icon}</div>
                  <div className="text-[10px] mt-0.5 font-medium">{opt.label}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Cuisine multi-select */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Cuisine <span className="font-normal normal-case text-gray-400">(optional)</span>
            </label>
            <div className="relative" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => setCuisineOpen(o => !o)}
                className="w-full px-3 py-2.5 rounded-xl border border-gray-200 bg-white text-sm text-left flex items-center justify-between focus:outline-none focus:ring-2 focus:ring-purple-300 focus:border-purple-400"
              >
                <span className={selectedCuisines.size > 0 ? 'text-gray-800 font-medium' : 'text-gray-400'}>
                  {selectedCuisines.size > 0 ? `${selectedCuisines.size} selected` : 'Any cuisine'}
                </span>
                <span className="text-gray-400 text-xs ml-1">{cuisineOpen ? '▲' : '▾'}</span>
              </button>
              {cuisineOpen && (
                <div className="absolute z-50 top-full mt-1 left-0 right-0 bg-white border border-purple-200 rounded-xl shadow-xl overflow-hidden">
                  <div className="p-2 border-b border-gray-100">
                    <input
                      type="text"
                      placeholder="Search cuisines…"
                      value={cuisineSearch}
                      onChange={e => setCuisineSearch(e.target.value)}
                      className="w-full px-3 py-1.5 text-sm rounded-lg border border-gray-200 focus:outline-none focus:ring-1 focus:ring-purple-300"
                      autoFocus
                    />
                  </div>
                  <div className="max-h-48 overflow-y-auto py-1">
                    {filteredCuisines.length === 0 ? (
                      <p className="text-xs text-gray-400 text-center py-3">No cuisines match</p>
                    ) : filteredCuisines.map(c => (
                      <label key={c} className={`flex items-center gap-2.5 px-4 py-2 cursor-pointer hover:bg-purple-50 text-sm ${selectedCuisines.has(c) ? 'text-purple-700 font-medium bg-purple-50' : 'text-gray-700'}`}>
                        <input
                          type="checkbox"
                          checked={selectedCuisines.has(c)}
                          onChange={() => toggleCuisine(c)}
                          className="accent-purple-600 w-3.5 h-3.5"
                        />
                        {c}
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </div>
            {/* Chips */}
            {selectedCuisines.size > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-1.5">
                {[...selectedCuisines].map(c => (
                  <span key={c} className="inline-flex items-center gap-1 text-xs bg-purple-100 text-purple-700 px-2.5 py-1 rounded-full font-medium">
                    {c}
                    <button type="button" onClick={() => removeCuisine(c)} className="text-purple-400 hover:text-purple-700 font-bold leading-none">×</button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Rating */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center justify-between">
              Min Rating
              <span className="bg-amber-100 text-amber-700 text-xs font-bold px-2 py-0.5 rounded-full normal-case">{minRating.toFixed(1)} ★</span>
            </label>
            <input
              type="range" min="0" max="5" step="0.1"
              value={minRating}
              onChange={e => setMinRating(parseFloat(e.target.value))}
              className="w-full accent-[#e23744] cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-gray-400">
              <span>0</span><span>2.5</span><span>5 ★</span>
            </div>
          </div>

          {/* Additional */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Preferences <span className="font-normal normal-case text-gray-400">(optional)</span>
            </label>
            <textarea
              value={additional}
              onChange={e => setAdditional(e.target.value)}
              rows={2}
              placeholder="e.g. family-friendly, rooftop, quick service"
              className="w-full px-3 py-2.5 rounded-xl border border-gray-200 bg-white text-sm text-gray-800 placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-purple-300 focus:border-purple-400"
            />
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading || !location}
            className="w-full py-3 rounded-xl bg-[#e23744] hover:bg-[#c0392b] text-white font-bold text-sm transition-all disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-sm"
          >
            {loading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                Finding matches…
              </>
            ) : (
              <>
                <span>✦</span> Ask for a Recommendation
              </>
            )}
          </button>
        </form>

        {/* Footer links */}
        <div className="px-5 pb-4 border-t border-gray-100 pt-4 space-y-1">
          {[['⚙', 'Taste Profile'], ['🔖', 'Saved Collections'], ['⚙️', 'Settings'], ['?', 'Support']].map(([icon, label]) => (
            <button key={label} className="w-full flex items-center gap-3 text-sm text-gray-500 hover:text-gray-800 py-1.5 hover:bg-gray-50 rounded-lg px-2 transition-colors">
              <span>{icon}</span><span>{label}</span>
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}

function ActiveChip({ icon, label, onRemove }: { icon: string; label: string; onRemove: () => void }) {
  return (
    <div className="flex items-center justify-between bg-purple-50 border border-purple-100 rounded-lg px-3 py-1.5 text-sm">
      <span className="flex items-center gap-2 text-gray-700 font-medium truncate">
        <span>{icon}</span>
        <span className="truncate">{label}</span>
      </span>
      <button onClick={onRemove} className="ml-2 text-gray-400 hover:text-gray-600 text-base leading-none shrink-0">×</button>
    </div>
  );
}
