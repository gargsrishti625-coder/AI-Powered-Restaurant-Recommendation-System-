'use client';

import type { RecommendResponse, RecommendRequest } from '@/lib/types';
import RestaurantCard from './RestaurantCard';

interface Props {
  results: RecommendResponse | null;
  loading: boolean;
  error: string | null;
  lastRequest: RecommendRequest | null;
  onRefresh: () => void;
}

export default function ResultsPanel({ results, loading, error, lastRequest, onRefresh }: Props) {
  if (loading) return <LoadingSkeleton />;

  if (error) return (
    <div className="flex-1 flex flex-col items-center justify-center py-24 text-center">
      <div className="text-4xl mb-4">⚠️</div>
      <h2 className="text-lg font-bold text-gray-800 mb-2">Something went wrong</h2>
      <p className="text-sm text-gray-500 max-w-sm">{error}</p>
    </div>
  );

  if (!results) return <EmptyState />;

  if (results.status === 'no_results' || results.recommendations.length === 0) return (
    <div className="flex-1 flex flex-col items-center justify-center py-24 text-center">
      <div className="text-4xl mb-4">🍽️</div>
      <h2 className="text-lg font-bold text-gray-800 mb-2">No restaurants found</h2>
      <p className="text-sm text-gray-500 max-w-sm">
        {results.error_detail ?? 'Try a different location, lower the minimum rating, or widen the budget.'}
      </p>
    </div>
  );

  const [top, ...rest] = results.recommendations;
  const budgetLabel = lastRequest?.budget === 'low' ? 'budget-friendly' : lastRequest?.budget === 'high' ? 'premium' : 'mid-range';
  const cuisineLabel = lastRequest?.cuisine ? lastRequest.cuisine.split(',').slice(0, 2).join(' & ') : 'curated';

  return (
    <div className="flex-1">
      {/* AI Journey header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-[10px] font-bold text-purple-600 bg-purple-100 px-2.5 py-1 rounded-full uppercase tracking-wider flex items-center gap-1">
            <span>✦</span> AI Curated Journey
          </span>
          {results.fallback_used && (
            <span className="text-[10px] font-medium text-amber-600 bg-amber-50 px-2.5 py-1 rounded-full border border-amber-100">
              ⚡ Baseline ranked
            </span>
          )}
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 leading-tight mb-1">
          Your Perfect Pairings in{' '}
          <span className="text-[#e23744]">{results.city}</span>
        </h1>
        <p className="text-sm text-gray-600">
          Based on your craving for{' '}
          <strong className="text-gray-900">{cuisineLabel}</strong> and a{' '}
          <strong className="text-gray-900">{budgetLabel} budget</strong>,
          {' '}I&apos;ve curated these hidden gems.
        </p>

        {/* Meta + Refresh */}
        <div className="flex items-center gap-3 mt-4 flex-wrap">
          <button
            onClick={onRefresh}
            className="flex items-center gap-2 bg-[#e23744] hover:bg-[#c0392b] text-white text-xs font-bold px-4 py-2 rounded-full transition-colors shadow-sm uppercase tracking-wide"
          >
            <span>↻</span> Refresh Suggestions
          </button>
          <div className="flex items-center gap-2 flex-wrap">
            <MetaChip icon="🔍" text={`${results.total_candidates_found.toLocaleString()} screened`} />
            <MetaChip icon="⏱" text={`${(results.latency_ms / 1000).toFixed(1)}s`} />
            <MetaChip icon={results.fallback_used ? '⚡' : '✨'} text={results.fallback_used ? 'Baseline' : 'AI ranked'} />
          </div>
        </div>
      </div>

      {/* Cards grid */}
      <div className="space-y-4">
        {/* Top card – full width / featured */}
        {top && <RestaurantCard rec={top} featured />}

        {/* Remaining cards in a 2-col grid */}
        {rest.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {rest.map(rec => (
              <RestaurantCard key={rec.restaurant_id} rec={rec} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function MetaChip({ icon, text }: { icon: string; text: string }) {
  return (
    <span className="text-xs text-gray-500 bg-white border border-gray-200 rounded-full px-3 py-1 flex items-center gap-1.5">
      <span>{icon}</span>{text}
    </span>
  );
}

function EmptyState() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center py-24 text-center">
      <div className="w-20 h-20 rounded-full bg-purple-50 flex items-center justify-center text-4xl mb-5">🔍</div>
      <h2 className="text-xl font-extrabold text-gray-800 mb-2">Ready to explore?</h2>
      <p className="text-sm text-gray-500 max-w-xs leading-relaxed">
        Set your preferences and hit <strong>Ask for a Recommendation</strong>.<br />
        Gemini AI will find and explain the best matches.
      </p>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="flex-1">
      {/* Header skeleton */}
      <div className="mb-6 space-y-3">
        <div className="skeleton h-5 w-40 rounded-full" />
        <div className="skeleton h-8 w-80 rounded-xl" />
        <div className="skeleton h-4 w-64 rounded-lg" />
        <div className="skeleton h-8 w-44 rounded-full" />
      </div>

      {/* Featured card skeleton */}
      <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden mb-4 flex flex-col sm:flex-row">
        <div className="skeleton sm:w-48 h-40 sm:h-auto" />
        <div className="p-4 flex-1 space-y-3">
          <div className="flex gap-2">
            <div className="skeleton h-5 w-16 rounded-full" />
            <div className="skeleton h-5 w-20 rounded-full" />
          </div>
          <div className="skeleton h-5 w-48 rounded-lg" />
          <div className="skeleton h-4 w-32 rounded-lg" />
          <div className="skeleton h-16 rounded-xl" />
        </div>
      </div>

      {/* Grid cards skeleton */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
            <div className="skeleton h-44" />
            <div className="p-4 space-y-2.5">
              <div className="flex gap-2">
                <div className="skeleton h-5 w-16 rounded-full" />
                <div className="skeleton h-5 w-14 rounded-full" />
              </div>
              <div className="skeleton h-5 w-36 rounded-lg" />
              <div className="skeleton h-14 rounded-xl" />
            </div>
          </div>
        ))}
      </div>

      {/* Loading message */}
      <div className="text-center mt-8 text-sm text-gray-400 flex items-center justify-center gap-2">
        <span className="w-4 h-4 border-2 border-gray-300 border-t-[#e23744] rounded-full animate-spin" />
        Gemini is finding your perfect matches…
      </div>
    </div>
  );
}
