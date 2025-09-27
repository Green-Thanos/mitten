"use client";

import { auth } from "@/server/auth";
import { redirect } from "next/navigation";
import dynamic from "next/dynamic";
import { useState, useRef, useEffect, Suspense } from "react";
import type { Session } from "next-auth";
// import { signOut } from "next-auth/react";
import Link from "next/link";

import { 
  ChevronDown, Search, Sparkles, Loader2, MapPin, BarChart3, Hash, 
  ArrowLeft, User, LogOut, Share2, ExternalLink, TrendingUp, TrendingDown, Minus
} from "lucide-react";

const Globe = dynamic(() => import("@/app/_components/interactive/globe"), {
  ssr: false
});

// Type definitions
interface EnvironmentalResult {
  id: string;
  originalQuery: string;
  category: "deforestation" | "biodiversity" | "wildfire";
  summary: string;
  sources: string[];
  charities: Array<{ name: string; url: string; description: string }>;
  visualizations: Array<{
    type: "pinpoints" | "heatmap" | "numbers";
    data: any;
    metadata: {
      title: string;
      description: string;
      source: string;
      lastUpdated: string;
    };
  }>;
  shareableUrl: string;
  generatedAt: string;
}

// Search Interface Component
function SearchInterface({ 
  onResults, 
  onSearchStart, 
  className = "" 
}: {
  onResults?: (results: EnvironmentalResult) => void;
  onSearchStart?: () => void;
  className?: string;
}) {
  const [query, setQuery] = useState("");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedVisualizationType, setSelectedVisualizationType] = useState<"pinpoints" | "heatmap" | "numbers" | "all">("all");
  const [processQuery, setProcessQuery] = useState({
    isLoading: false,
    error: null as string | null,
  });
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Predetermined Michigan environmental queries
  const predefinedQueries = [
    "Biodiversity hotspots in Michigan's Great Lakes wetlands",
    "Deforestation trends in Michigan's Upper Peninsula from 2017 to 2024", 
    "Wildfire risk areas in Michigan's Upper Peninsula",
    "Wetland conservation efforts in Saginay Bay",
    "Forest recovery after logging in Huron-Manistee",
    "Invasive species impact on Michigan lakes",
    "Climate change effects on Michigan wildlife",
    "Protected areas in Michigan's state parks",
  ];

  // FastAPI call function
  const callFastAPI = async (queryData: { query: string; timeRange?: string }) => {
    setProcessQuery({ isLoading: true, error: null });
    onSearchStart?.();
    
    try {
      const response = await fetch('/api/environmental/process-query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: queryData.query,
          category: undefined,
          timeRange: queryData.timeRange || "2017-2024",
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      onResults?.(data);
      setProcessQuery({ isLoading: false, error: null });
    } catch (error) {
      console.error("Query processing failed:", error);
      setProcessQuery({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Failed to process query'
      });
    }
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSearch = async (searchQuery: string = query) => {
    if (!searchQuery.trim()) return;
    try {
      await callFastAPI({
        query: searchQuery,
        timeRange: "2017-2024",
      });
    } catch (error) {
      console.error("Search failed:", error);
    }
  };

  const handlePredefinedQuery = (selectedQuery: string) => {
    setQuery(selectedQuery);
    setIsDropdownOpen(false);
    handleSearch(selectedQuery);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  const isLoading = processQuery.isLoading;

  return (
    <div className={`fixed bottom-8 left-1/2 transform -translate-x-1/2 z-10 ${className}`}>
      <div className="relative" ref={dropdownRef}>
        {/* Search Input Container */}
        <div className="bg-black/20 backdrop-blur-md border border-white/10 rounded-2xl p-1 shadow-2xl">
          <div className="flex items-center gap-2">
            {/* Dropdown Button */}
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center gap-2 px-4 py-3 text-white/70 hover:text-white transition-colors"
              disabled={isLoading}
            >
              <Sparkles className="w-4 h-4" />
              <ChevronDown className={`w-4 h-4 transition-transform ${isDropdownOpen ? "rotate-180" : ""}`} />
            </button>

            {/* Search Input */}
            <div className="flex-1 relative">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about Michigan's environment..."
                className="w-full bg-transparent text-white placeholder-white/50 outline-none py-3 pr-12 text-lg min-w-[400px]"
                disabled={isLoading}
              />

              {/* Search Button */}
              <button
                onClick={() => handleSearch()}
                disabled={isLoading || !query.trim()}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 rounded-lg bg-green-500/20 hover:bg-green-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 text-white animate-spin" />
                ) : (
                  <Search className="w-4 h-4 text-white" />
                )}
              </button>
            </div>

            {/* Visualization Type Selector */}
            <div className="flex items-center gap-1 px-2">
              <button
                onClick={() => setSelectedVisualizationType("all")}
                className={`p-2 rounded-lg transition-colors ${
                  selectedVisualizationType === "all"
                    ? "bg-green-500/30 text-green-300"
                    : "text-white/50 hover:text-white/70 hover:bg-white/5"
                }`}
                title="All visualizations"
              >
                <BarChart3 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setSelectedVisualizationType("pinpoints")}
                className={`p-2 rounded-lg transition-colors ${
                  selectedVisualizationType === "pinpoints"
                    ? "bg-green-500/30 text-green-300"
                    : "text-white/50 hover:text-white/70 hover:bg-white/5"
                }`}
                title="Location pinpoints"
              >
                <MapPin className="w-4 h-4" />
              </button>
              <button
                onClick={() => setSelectedVisualizationType("numbers")}
                className={`p-2 rounded-lg transition-colors ${
                  selectedVisualizationType === "numbers"
                    ? "bg-green-500/30 text-green-300"
                    : "text-white/50 hover:text-white/70 hover:bg-white/5"
                }`}
                title="Key metrics"
              >
                <Hash className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Dropdown Menu */}
        {isDropdownOpen && (
          <div className="absolute bottom-full mb-2 left-0 right-0 bg-black/30 backdrop-blur-md border border-white/10 rounded-xl shadow-2xl overflow-hidden">
            <div className="p-2">
              <div className="text-white/50 text-xs uppercase tracking-wide px-3 py-2 font-medium">
                Michigan Environmental Queries
              </div>
              {predefinedQueries?.map((predefinedQuery, index) => (
                <button
                  key={index}
                  onClick={() => handlePredefinedQuery(predefinedQuery)}
                  className="w-full text-left px-3 py-2 text-white/80 hover:text-white hover:bg-white/5 rounded-lg transition-colors text-sm group"
                  disabled={isLoading}
                >
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-400/50 group-hover:bg-green-400 transition-colors" />
                    {predefinedQuery}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 bg-black/30 backdrop-blur-md border border-white/10 rounded-lg px-4 py-2">
            <div className="flex items-center gap-2 text-white/70 text-sm">
              <Loader2 className="w-4 h-4 animate-spin" />
              Analyzing Michigan environmental data...
            </div>
          </div>
        )}

        {/* Error State */}
        {processQuery.error && (
          <div className="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 bg-red-500/20 backdrop-blur-md border border-red-500/30 rounded-lg px-4 py-2">
            <div className="text-red-300 text-sm">
              {processQuery.error}
            </div>
          </div>
        )}
      </div>

      {/* Floating hint */}
      <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 text-white/40 text-xs animate-pulse">
        Ask about Michigan's environment
      </div>
    </div>
  );
}

// Visualization Components
const PinpointVisualization = ({ data, metadata }: any) => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high": return "bg-red-500";
      case "medium": return "bg-yellow-500";
      case "low": return "bg-green-500";
      default: return "bg-gray-500";
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-green-300 flex items-center gap-2">
        <MapPin className="w-5 h-5" />
        {metadata.title}
      </h3>
      
      <div className="relative bg-gradient-to-br from-green-900/20 to-blue-900/20 rounded-lg p-6 border border-green-500/20">
        <div className="relative w-full h-64 bg-green-950/30 rounded-lg overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-green-800/20 to-green-600/20 rounded-lg">
            <div className="text-center pt-20 text-green-400/50 text-sm">Michigan Environmental Data</div>
          </div>
          
          {data.map((point: any, index: number) => (
            <div
              key={index}
              className="absolute group cursor-pointer"
              style={{
                left: `${20 + (index % 3) * 25}%`,
                top: `${30 + Math.floor(index / 3) * 20}%`,
              }}
            >
              <div className={`w-3 h-3 rounded-full ${getSeverityColor(point.severity)} animate-pulse shadow-lg`} />
              <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black/80 text-white text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                <div className="font-medium">{point.name}</div>
                <div className="text-green-300">Value: {point.value}</div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="flex items-center gap-4 mt-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-green-300">Low Risk</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <span className="text-yellow-300">Medium Risk</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-red-300">High Risk</span>
          </div>
        </div>
      </div>
      
      <div className="text-xs text-white/50">{metadata.description}</div>
    </div>
  );
};

const HeatmapVisualization = ({ data, metadata }: any) => {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-green-300 flex items-center gap-2">
        <BarChart3 className="w-5 h-5" />
        {metadata.title}
      </h3>
      
      <div className="bg-gradient-to-br from-green-900/20 to-blue-900/20 rounded-lg p-6 border border-green-500/20">
        <div className="grid grid-cols-10 gap-1 w-full h-64">
          {data.data.map((cell: any, index: number) => (
            <div
              key={index}
              className="rounded-sm transition-all duration-300 hover:scale-110 cursor-pointer"
              style={{
                backgroundColor: `rgba(${
                  cell.intensity > 0.7 ? '239, 68, 68' :
                  cell.intensity > 0.4 ? '245, 158, 11' : '34, 197, 94'
                }, ${0.3 + cell.intensity * 0.7})`,
              }}
              title={`Intensity: ${(cell.intensity * 100).toFixed(1)}%`}
            />
          ))}
        </div>
        
        <div className="flex items-center justify-between mt-4 text-xs">
          <span className="text-green-300">Low Intensity</span>
          <div className="flex-1 mx-4 h-2 bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 rounded-full" />
          <span className="text-red-300">High Intensity</span>
        </div>
      </div>
      
      <div className="text-xs text-white/50">{metadata.description}</div>
    </div>
  );
};

const NumbersVisualization = ({ data, metadata }: any) => {
  const getTrendIcon = (change: number) => {
    if (change > 0) return <TrendingUp className="w-4 h-4 text-green-400" />;
    if (change < 0) return <TrendingDown className="w-4 h-4 text-red-400" />;
    return <Minus className="w-4 h-4 text-gray-400" />;
  };

  const getTrendColor = (change: number) => {
    if (change > 0) return "text-green-400";
    if (change < 0) return "text-red-400";
    return "text-gray-400";
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-green-300 flex items-center gap-2">
        <Hash className="w-5 h-5" />
        {metadata.title}
      </h3>
      
      <div className="bg-gradient-to-br from-green-900/20 to-blue-900/20 rounded-lg p-6 border border-green-500/20 space-y-4">
        <div className="text-center pb-4 border-b border-green-500/20">
          <div className="text-3xl font-bold text-white">{data.totalAffectedArea.toLocaleString()}</div>
          <div className="text-green-300">Total Affected Area (acres)</div>
          <div className={`flex items-center justify-center gap-1 mt-2 ${getTrendColor(data.percentageChange)}`}>
            {getTrendIcon(data.percentageChange)}
            <span className="text-sm">{Math.abs(data.percentageChange)}% since {data.timeframe}</span>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          {data.keyMetrics.map((metric: any, index: number) => (
            <div key={index} className="bg-white/5 rounded-lg p-3">
              <div className="text-lg font-semibold text-white">{metric.value}</div>
              <div className="text-sm text-green-300">{metric.label}</div>
              <div className={`flex items-center gap-1 mt-1 text-xs ${getTrendColor(metric.change)}`}>
                {getTrendIcon(metric.change)}
                <span>{Math.abs(metric.change)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="text-xs text-white/50">{metadata.description}</div>
    </div>
  );
};

// Results Layout Component
function ResultsLayout({ results, isLoading = false }: {
  results: EnvironmentalResult | null;
  isLoading?: boolean;
}) {
  const [selectedVisualization, setSelectedVisualization] = useState<"pinpoints" | "heatmap" | "numbers">("pinpoints");

  const handleShare = async (url: string) => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Michigan Environmental Data - Enviducate',
          text: results ? `Check out these insights: ${results.originalQuery}` : 'Environmental data from Enviducate',
          url: url,
        });
      } catch (error) {
        navigator.clipboard.writeText(url);
      }
    } else {
      navigator.clipboard.writeText(url);
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "deforestation": return "text-orange-300";
      case "biodiversity": return "text-green-300";
      case "wildfire": return "text-red-300";
      default: return "text-blue-300";
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "deforestation": return "🌲";
      case "biodiversity": return "🦋";
      case "wildfire": return "🔥";
      default: return "🌍";
    }
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6 min-h-screen">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-black/20 backdrop-blur-md border border-white/10 rounded-2xl p-6 animate-pulse">
            <div className="h-6 bg-white/10 rounded mb-4" />
            <div className="h-32 bg-white/5 rounded mb-4" />
            <div className="h-4 bg-white/10 rounded mb-2" />
            <div className="h-4 bg-white/10 rounded w-3/4" />
          </div>
        ))}
      </div>
    );
  }

  if (!results) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center text-white/70">
          <div className="text-6xl mb-4">🌍</div>
          <h2 className="text-2xl font-semibold mb-2">Welcome to Enviducate</h2>
          <p className="text-white/50">Ask a question about Michigan's environment to get started</p>
        </div>
      </div>
    );
  }

  const currentVisualization = results.visualizations.find(v => v.type === selectedVisualization);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6 min-h-screen">
      {/* LEFT COLUMN - Summary */}
      <div className="bg-black/20 backdrop-blur-md border border-white/10 rounded-2xl p-6 space-y-6">
        <div className="border-b border-white/10 pb-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">{getCategoryIcon(results.category)}</span>
            <span className={`text-sm uppercase tracking-wide font-medium ${getCategoryColor(results.category)}`}>
              {results.category}
            </span>
          </div>
          <h2 className="text-xl font-semibold text-white">{results.originalQuery}</h2>
          <div className="text-xs text-white/50 mt-2">
            Generated {new Date(results.generatedAt).toLocaleString()}
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-green-300">Environmental Analysis</h3>
          <p className="text-white/90 leading-relaxed">{results.summary}</p>
        </div>

        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-white/70 uppercase tracking-wide">Sources</h3>
          <div className="space-y-2">
            {results.sources.map((source, index) => (
              <div key={index} className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-green-400 mt-2 flex-shrink-0" />
                <span className="text-sm text-white/70">{source}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CENTER COLUMN - Visualization */}
      <div className="bg-black/20 backdrop-blur-md border border-white/10 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6 border-b border-white/10 pb-4">
          <h2 className="text-xl font-semibold text-white">Environmental Data</h2>
          <div className="flex items-center gap-1 bg-white/5 rounded-lg p-1">
            <button
              onClick={() => setSelectedVisualization("pinpoints")}
              className={`p-2 rounded-md transition-colors ${
                selectedVisualization === "pinpoints"
                  ? "bg-green-500/30 text-green-300"
                  : "text-white/50 hover:text-white/70"
              }`}
            >
              <MapPin className="w-4 h-4" />
            </button>
            <button
              onClick={() => setSelectedVisualization("heatmap")}
              className={`p-2 rounded-md transition-colors ${
                selectedVisualization === "heatmap"
                  ? "bg-green-500/30 text-green-300"
                  : "text-white/50 hover:text-white/70"
              }`}
            >
              <BarChart3 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setSelectedVisualization("numbers")}
              className={`p-2 rounded-md transition-colors ${
                selectedVisualization === "numbers"
                  ? "bg-green-500/30 text-green-300"
                  : "text-white/50 hover:text-white/70"
              }`}
            >
              <Hash className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="h-full">
          {currentVisualization && (
            <div>
              {selectedVisualization === "pinpoints" && (
                <PinpointVisualization 
                  data={currentVisualization.data} 
                  metadata={currentVisualization.metadata} 
                />
              )}
              {selectedVisualization === "heatmap" && (
                <HeatmapVisualization 
                  data={currentVisualization.data} 
                  metadata={currentVisualization.metadata} 
                />
              )}
              {selectedVisualization === "numbers" && (
                <NumbersVisualization 
                  data={currentVisualization.data} 
                  metadata={currentVisualization.metadata} 
                />
              )}
            </div>
          )}
        </div>

        <div className="mt-6 pt-4 border-t border-white/10">
          <div className="text-xs text-white/50">
            Data source: {currentVisualization?.metadata.source} • 
            Last updated: {currentVisualization ? new Date(currentVisualization.metadata.lastUpdated).toLocaleDateString() : 'N/A'}
          </div>
        </div>
      </div>

      {/* RIGHT COLUMN - Resources */}
      <div className="bg-black/20 backdrop-blur-md border border-white/10 rounded-2xl p-6 space-y-6">
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-green-300">Ways to Help</h3>
          <div className="space-y-3">
            {results.charities.map((charity, index) => (
              <div key={index} className="bg-white/5 rounded-lg p-4 hover:bg-white/10 transition-colors group">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-white group-hover:text-green-300 transition-colors">
                      {charity.name}
                    </h4>
                    <p className="text-sm text-white/70 mt-1">{charity.description}</p>
                  </div>
                  <a
                    href={charity.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-white/50 hover:text-green-300 transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-4 border-t border-white/10 pt-6">
          <h3 className="text-lg font-semibold text-green-300">Share Results</h3>
          <div className="space-y-3">
            <button
              onClick={() => handleShare(results.shareableUrl)}
              className="w-full flex items-center gap-3 bg-green-500/20 hover:bg-green-500/30 text-green-300 rounded-lg p-3 transition-colors group"
            >
              <Share2 className="w-4 h-4 group-hover:scale-110 transition-transform" />
              <span>Share These Insights</span>
            </button>
            
            <div className="grid grid-cols-2 gap-2">
              <a
                href={`https://twitter.com/intent/tweet?text=Check out these Michigan environmental insights from Enviducate&url=${encodeURIComponent(results.shareableUrl)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 rounded-lg p-2 transition-colors text-sm"
              >
                <span>𝕏</span>
                Twitter
              </a>
              <a
                href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(results.shareableUrl)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 bg-blue-700/20 hover:bg-blue-700/30 text-blue-300 rounded-lg p-2 transition-colors text-sm"
              >
                <span>in</span>
                LinkedIn
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Main App Component
export default function AppPage() {
  const [results, setResults] = useState<EnvironmentalResult | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [session, setSession] = useState<Session | null>(null);

  // Handle auth check on mount
  useEffect(() => {
    // You'll need to implement this based on your auth system
    // This is a placeholder
    const checkAuth = async () => {
        try {
            const response = await fetch("/api/auth/session");
    
            // ✅ Check the status first
            if (!response.ok) {
              // not logged in or error
              redirect("/"); // redirect to home
              return;
            }
    
            // ✅ parse JSON
            const sessionData = await response.json();
    
            if (!sessionData) {
              // no session object returned
              redirect("/");
              return;
            }
    
            // ✅ we have a session
            setSession(sessionData);
          } catch (error) {
            console.error("Auth check failed:", error);
            redirect("/"); // redirect on error
          }
        };

    checkAuth();
  }, []);

  // Handle search results from SearchInterface
  const handleResults = (newResults: EnvironmentalResult) => {
    setResults(newResults);
    setShowResults(true);
    setIsSearching(false);
  };

  // Handle going back to search view
  const handleBackToSearch = () => {
    setShowResults(false);
  };

  // Handle search start (for loading states)
  const handleSearchStart = () => {
    setIsSearching(true);
  };

  // Handle sign out
  const handleSignOut = () => {
    window.location.href="/api/auth/signout";
  };

  // Show loading while checking auth
  if (!session) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-black">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-green-500/30 border-t-green-500 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-white/70">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-black overflow-hidden">
      {/* Header Bar */}
      <div className="absolute top-0 left-0 right-0 z-20 bg-black/20 backdrop-blur-md border-b border-white/10">
        <div className="flex items-center justify-between px-6 py-4">
          {/* Left side - Logo/Title and Back Button */}
          <div className="flex items-center gap-4">
            {showResults && (
              <button
                onClick={handleBackToSearch}
                className="flex items-center gap-2 text-white/70 hover:text-white transition-colors p-2 rounded-lg hover:bg-white/5"
              >
                <ArrowLeft className="w-4 h-4" />
                <span className="text-sm">New Search</span>
              </button>
            )}
             <Link href="/" className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-green-500 to-blue-500 flex items-center justify-center">
                    <span className="text-white font-bold text-sm">E</span>
                </div>
                <div>
                    <h1 className="text-lg font-semibold text-white">Enviducate</h1>
                    <p className="text-xs text-white/50">
                    Envision a better environment through education
                    </p>
                </div>
                </Link>
          </div>

          {/* Right side - User Info */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-white/70">
              <User className="w-4 h-4" />
              <span className="text-sm">{session.user?.email || 'User'}</span>
            </div>
            <button
              onClick={handleSignOut}
              className="flex items-center gap-2 text-white/50 hover:text-red-300 transition-colors p-2 rounded-lg hover:bg-red-500/10"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="pt-20"> {/* Offset for header */}
        {!showResults ? (
          // Search View - Globe background with search interface
          <>
            <Suspense fallback={
              <div className="flex items-center justify-center min-h-screen">
                <div className="text-white/50">Loading environment...</div>
              </div>
            }>
              <Globe />
            </Suspense>
            
            <SearchInterface 
              onResults={handleResults}
              onSearchStart={handleSearchStart}
              className={isSearching ? "opacity-75" : ""}
            />

            {/* Welcome Message when not searching */}
            {!isSearching && (
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center pointer-events-none">
                <div className="text-6xl mb-4">🌍</div>
                <h2 className="text-3xl font-bold text-white mb-2">Welcome to Enviducate</h2>
                <p className="text-white/70 text-lg">
                  Ask questions about Michigan's environment to explore data-driven insights
                </p>
                <div className="flex items-center justify-center gap-6 mt-6 text-sm text-white/50">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-400" />
                    <span>Biodiversity</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-orange-400" />
                    <span>Deforestation</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-red-400" />
                    <span>Wildfire Risk</span>
                  </div>
                </div>
              </div>
            )}

            {/* Loading overlay when searching */}
            {isSearching && (
              <div className="absolute inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-10">
                <div className="text-center">
                  <div className="w-12 h-12 border-2 border-green-500/30 border-t-green-500 rounded-full animate-spin mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">Analyzing Environmental Data</h3>
                  <p className="text-white/70">Processing your query with AI and satellite imagery...</p>
                </div>
              </div>
            )}
          </>
        ) : (
          // Results View - Three column layout
          <ResultsLayout 
            results={results} 
            isLoading={isSearching}
          />
        )}
      </div>

      {/* Floating Search Button (when in results view) */}
      {showResults && (
        <button
          onClick={handleBackToSearch}
          className="fixed bottom-6 right-6 bg-green-500 hover:bg-green-600 text-white rounded-full p-4 shadow-2xl transition-colors z-20 group"
        >
          <div className="flex items-center gap-2">
            <span className="text-2xl">🔍</span>
            <span className="text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap">
              New Search
            </span>
          </div>
        </button>
      )}
    </div>
  );
}