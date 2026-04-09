'use client';

import { useState, useCallback } from 'react';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import ResultsPanel from '@/components/ResultsPanel';
import type { RecommendRequest, RecommendResponse } from '@/lib/types';
import { fetchRecommendations } from '@/lib/api';

export default function Home() {
  const [results, setResults] = useState<RecommendResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastRequest, setLastRequest] = useState<RecommendRequest | null>(null);

  const handleSearch = useCallback(async (req: RecommendRequest) => {
    setLoading(true);
    setError(null);
    setLastRequest(req);
    try {
      const data = await fetchRecommendations(req);
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
      setResults(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleRefresh = useCallback(() => {
    if (lastRequest) handleSearch(lastRequest);
  }, [lastRequest, handleSearch]);

  const handleClearFilter = useCallback((key: keyof RecommendRequest) => {
    if (!lastRequest) return;
    const updated = { ...lastRequest };
    if (key === 'cuisine') updated.cuisine = null;
    else if (key === 'budget') updated.budget = 'medium';
    else if (key === 'location') {
      setResults(null);
      setLastRequest(null);
      return;
    }
    handleSearch(updated);
  }, [lastRequest, handleSearch]);

  return (
    <div className="min-h-screen flex flex-col bg-[#fdf9f6]">
      <Header />
      <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6">
        <div className="flex flex-col lg:flex-row gap-6 items-start">

          {/* Sidebar (right on desktop, stacks below on mobile) */}
          <div className="order-2 lg:order-2 lg:sticky lg:top-20 w-full lg:w-auto">
            <Sidebar
              onSearch={handleSearch}
              loading={loading}
              activeFilters={lastRequest}
              onClearFilter={handleClearFilter}
            />
          </div>

          {/* Main content (left on desktop) */}
          <main className="order-1 lg:order-1 flex-1 min-w-0 flex flex-col">
            <ResultsPanel
              results={results}
              loading={loading}
              error={error}
              lastRequest={lastRequest}
              onRefresh={handleRefresh}
            />
          </main>

        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white mt-12">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
            <div>
              <span className="text-[#e23744] font-extrabold text-lg">Zomato AI</span>
              <p className="text-xs text-gray-400 mt-0.5">© 2024 Zomato AI Digital Hospitality</p>
            </div>
            <nav className="flex flex-wrap gap-x-6 gap-y-2 text-xs text-gray-500">
              {['About', 'Investor Relations', 'Report Fraud', 'Contact', 'Privacy', 'Terms'].map(l => (
                <a key={l} href="#" className="hover:text-gray-800 uppercase tracking-wide">{l}</a>
              ))}
            </nav>
          </div>
        </div>
      </footer>
    </div>
  );
}
