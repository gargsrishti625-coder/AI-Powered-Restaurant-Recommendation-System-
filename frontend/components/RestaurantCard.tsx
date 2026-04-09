'use client';

import type { RecommendationItem } from '@/lib/types';

interface Props {
  rec: RecommendationItem;
  featured?: boolean;
}

// Cuisine → gradient
const CUISINE_GRADIENTS: Record<string, string> = {
  Italian: 'from-orange-400 to-red-500',
  Chinese: 'from-red-500 to-rose-700',
  Indian: 'from-amber-400 to-orange-600',
  'North Indian': 'from-amber-400 to-orange-600',
  'South Indian': 'from-green-400 to-teal-600',
  Continental: 'from-blue-400 to-indigo-600',
  American: 'from-sky-400 to-blue-600',
  Mexican: 'from-yellow-400 to-orange-500',
  Japanese: 'from-pink-400 to-red-500',
  Thai: 'from-teal-400 to-green-600',
  Mediterranean: 'from-cyan-400 to-blue-500',
  Cafe: 'from-amber-300 to-yellow-500',
  Pizza: 'from-orange-300 to-red-500',
  Biryani: 'from-yellow-500 to-amber-700',
  Seafood: 'from-cyan-500 to-blue-600',
  Bbq: 'from-red-600 to-orange-700',
  Korean: 'from-pink-300 to-red-400',
  French: 'from-indigo-400 to-purple-500',
};

function getCuisineGradient(cuisines: string): string {
  const first = cuisines.split(',')[0].trim();
  return CUISINE_GRADIENTS[first] ?? 'from-purple-400 to-pink-500';
}

const RANK_COLORS = ['', 'bg-amber-400', 'bg-gray-400', 'bg-amber-700'];

export default function RestaurantCard({ rec, featured = false }: Props) {
  const gradient = getCuisineGradient(rec.cuisine);
  const cuisineTags = rec.cuisine.split(',').map(c => c.trim()).filter(Boolean);
  const budgetSymbol = rec.estimated_cost <= 700 ? '₹' : rec.estimated_cost <= 2000 ? '₹₹' : '₹₹₹';
  const budgetLabel = rec.estimated_cost <= 700 ? 'Budget' : rec.estimated_cost <= 2000 ? 'Mid Range' : 'Premium';

  return (
    <div className={`bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow group ${featured ? 'flex flex-col sm:flex-row' : ''}`}>
      {/* Image area */}
      <div className={`relative overflow-hidden bg-gradient-to-br ${gradient} ${featured ? 'sm:w-48 h-40 sm:h-auto shrink-0' : 'h-44'}`}>
        {/* Decorative food emoji */}
        <div className="absolute inset-0 flex items-center justify-center opacity-20 text-white text-7xl select-none">
          {getCuisineEmoji(cuisineTags[0])}
        </div>
        {/* Subtle overlay pattern */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent" />
        {/* Rating badge */}
        <div className="absolute top-3 right-3 bg-white/95 backdrop-blur-sm rounded-full px-2.5 py-1 flex items-center gap-1 shadow-sm">
          <span className="text-amber-400 text-xs">★</span>
          <span className="text-xs font-bold text-gray-900">{rec.rating.toFixed(1)}</span>
        </div>
        {/* Rank badge */}
        <div className={`absolute top-3 left-3 w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-black shadow-sm ${RANK_COLORS[rec.rank] ?? 'bg-purple-500'}`}>
          {rec.rank}
        </div>
      </div>

      {/* Content */}
      <div className="p-4 flex-1">
        {/* Tags */}
        <div className="flex flex-wrap items-center gap-1.5 mb-2">
          {cuisineTags.slice(0, 3).map(tag => (
            <span key={tag} className="text-[11px] font-medium text-pink-700 bg-pink-50 border border-pink-100 px-2.5 py-0.5 rounded-full">
              {tag}
            </span>
          ))}
          <span className="text-[11px] font-medium text-pink-700 bg-pink-50 border border-pink-100 px-2.5 py-0.5 rounded-full">
            {budgetSymbol} – {budgetLabel}
          </span>
        </div>

        {/* Name */}
        <h2 className="text-base font-bold text-gray-900 mb-1 leading-snug group-hover:text-[#e23744] transition-colors">
          {rec.restaurant_name}
        </h2>

        {/* Stats row */}
        <div className="flex items-center gap-3 mb-3 text-xs text-gray-500">
          <span>₹{rec.estimated_cost.toLocaleString()} for two</span>
          <span className="text-gray-300">·</span>
          <span>{rec.votes.toLocaleString()} votes</span>
          <span className="text-gray-300">·</span>
          <ConfidenceBadge confidence={rec.confidence} />
        </div>

        {/* AI Insight */}
        <div className="bg-purple-50 border border-purple-100 rounded-xl p-3">
          <div className="flex items-center gap-1.5 mb-1.5">
            <span className="text-purple-600 text-[10px]">✦</span>
            <span className="text-[10px] font-bold text-purple-600 uppercase tracking-wider">AI Insight</span>
          </div>
          <p className="text-xs text-gray-700 italic leading-relaxed">
            &ldquo;{rec.ai_explanation}&rdquo;
          </p>
          {rec.tradeoffs && (
            <p className="mt-1.5 text-[11px] text-amber-700 bg-amber-50 rounded-lg px-2 py-1">
              ⚖ {rec.tradeoffs}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function ConfidenceBadge({ confidence }: { confidence: string }) {
  const map = {
    high: 'text-emerald-700 bg-emerald-50',
    medium: 'text-amber-700 bg-amber-50',
    low: 'text-red-700 bg-red-50',
  } as Record<string, string>;
  return (
    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${map[confidence] ?? map.medium}`}>
      {confidence} match
    </span>
  );
}

function getCuisineEmoji(cuisine: string): string {
  const map: Record<string, string> = {
    Italian: '🍝', Chinese: '🥢', Indian: '🍛', 'North Indian': '🍛',
    'South Indian': '🥘', Pizza: '🍕', Biryani: '🍲', Cafe: '☕',
    American: '🍔', Japanese: '🍱', Thai: '🍜', Seafood: '🦐',
    Bbq: '🔥', Mexican: '🌮', Continental: '🥗', Korean: '🥗',
    French: '🥐', Mediterranean: '🫒', Burger: '🍔', Desserts: '🍰',
    'Ice Cream': '🍦', Sushi: '🍣',
  };
  return map[cuisine] ?? '🍽️';
}
