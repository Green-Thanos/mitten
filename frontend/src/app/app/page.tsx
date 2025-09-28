"use client";

import { redirect, useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { useState, useRef, useEffect, Suspense } from "react";
import type { Session } from "next-auth";
import Link from "next/link";
import ResultsLayout from "@/app/_components/interactive/resultsLayout";

import { 
  ChevronDown, Search, Sparkles, Loader2, MapPin, BarChart3, Hash, 
  ArrowLeft, User, LogOut, Share2, ExternalLink, TrendingUp, TrendingDown, Minus
} from "lucide-react";

const Globe = dynamic(() => import("@/app/_components/interactive/globe"), {
  ssr: false
});

const MockData = {
    id: "mock_1",
    originalQuery: "Biodiversity hotspots in Michigan's Great Lakes wetlands",
    category: "biodiversity",
    summary: "Michigan's Great Lakes wetlands host diverse and unique species. Current hotspots include Saginaw Bay, St. Clair flats, and the western UP. Conservation actions have improved biodiversity in select areas, but invasive species remain a problem.",
    sources: [
      "Michigan Department of Natural Resources 2025 Wetlands Report",
      "Great Lakes Biodiversity Project 2024 Findings",
      "USGS Great Lakes Program"
    ],
    charities: [
      {
        name: "Michigan Wetlands Association",
        url: "https://www.mi-wetlands.org",
        description: "Protecting and restoring wetland habitats in Michigan."
      },
      {
        name: "Great Lakes Conservation Fund",
        url: "https://www.glcfund.org",
        description: "Supporting biodiversity and resilient habitats throughout the Great Lakes region."
      }
    ],
    visualizations: [
        {
            type: "pinpoints",
            data: [
                { lat: 43.6, lng: -83.9, label: "Saginaw Bay" },
                { lat: 42.5, lng: -82.6, label: "St. Clair Flats" },
                { lat: 46.5, lng: -90.0, label: "Western Upper Peninsula" }
            ],
            metadata: {
                title: "Biodiversity Hotspots",
                description: "Key wetland areas in Michigan with rich biodiversity.",
                source: "Michigan Department of Natural Resources",
                lastUpdated: "2025-09-21"
            }
        }
    ],
    shareableUrl: "https://enviducate.org/mock-result",
    generatedAt: new Date().toISOString()
}

// Type definitions
interface EnvironmentalResult {
  id: string;
  originalQuery: string;
  category: string;
  summary: string;
  sources: string[];
  charities: Array<{ name: string; url: string; description: string }>;
  visualizations: Array<{
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
    "E Coli Related NPDES Facilities",
    "Protected areas in Michigan and Environmental Collection Points",
    "Michigan Gas Storage Fields"
  ];

  const callFastAPI = async (queryData: { query: string }) => {
    setProcessQuery({ isLoading: true, error: null });
    onSearchStart?.();
  
    try {
      let data: EnvironmentalResult;
      let response;

      switch(queryData.query) {
        case "Michigan Gas Storage Fields":
            response = await fetch('/data/mockData_gasFields.json');
            if (!response.ok) throw new Error("Failed to load gas fields data");
            data = await response.json();
            break;
        case "Protected areas in Michigan and Environmental Collection Points":
            response = await fetch('/data/FCMPSamplingData.json');
            if (!response.ok) throw new Error("Failed to load Environment collection data");
            data = await response.json();
            break;
        case "E Coli Related NPDES Facilities":
            response = await fetch('/data/EcoliRelatedNPDES.json');
            if (!response.ok) throw new Error("Failed to load Environment collection data");
            data = await response.json();
            break;
        default:
            data = MockData;
      }
  
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
            {/* <div className="flex items-center gap-1 px-2">
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
            </div> */}
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
 

// Main App Component
export default function AppPage() {
    const router = useRouter();
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
              router.push("/"); // router.push to home
              return;
            }
    
            // ✅ parse JSON
            const sessionData = await response.json();
    
            if (!sessionData) {
              // no session object returned
              router.push("/");
              return;
            }
    
            // ✅ we have a session
            setSession(sessionData);
          } catch (error) {
            console.error("Auth check failed:", error);
            router.push("/"); // router.push on error
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
    router.push("/api/auth/signout");
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
             <Link href="/app" className="flex items-center gap-3">
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
            results={results as any} 
            isLoading={isSearching}
          />
        )}
      </div>

      {/* Floating Search Button (when in results view) */}
      {/* {showResults && (
        <div>hi</div>
      )} */}
    </div>
  );
}