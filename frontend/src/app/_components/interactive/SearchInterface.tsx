"use client"

import React, { useState, useRef, useEffect } from "react";
import { ChevronDown, Search, Sparkles, Loader2, MapPin, BarChart3, Hash } from "lucide-react";

interface SearchInterfaceProps {
  onResults?: (results: any) => void;
  className?: string;
}

export default function EnhancedSearchInterface({ onResults, className = "" }: SearchInterfaceProps) {
  const [query, setQuery] = useState("");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedVisualizationType, setSelectedVisualizationType] = useState<"pinpoints" | "heatmap" | "numbers" | "all">("all");
  const dropdownRef = useRef<HTMLDivElement>(null);

  // FastAPI backend integration
  const [processQuery, setProcessQuery] = useState({
    isLoading: false,
    error: null as string | null,
  });

  // Predetermined Michigan environmental queries
  const predefinedQueries = [
    "Biodiversity hotspots in Michigan's Great Lakes wetlands",
    "Deforestation trends in Michigan's Upper Peninsula from 2017 to 2024", 
    "Wildfire risk areas in Michigan's Upper Peninsula",
    "Wetland conservation efforts in Saginaw Bay",
    "Forest recovery after logging in Huron-Manistee",
    "Invasive species impact on Michigan lakes",
    "Climate change effects on Michigan wildlife",
    "Protected areas in Michigan's state parks",
  ];

  // FastAPI call function
  const callFastAPI = async (queryData: { query: string; timeRange?: string }) => {
    setProcessQuery({ isLoading: true, error: null });
    
    try {
      const response = await fetch('/api/environmental/process-query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: queryData.query,
          category: undefined, // Let the backend determine category
          timeRange: queryData.timeRange || "2017-2024",
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Query processed:", data);
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
        timeRange: "2017-2024", // Default timeframe
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