'use client';

import React from 'react';
import 'leaflet/dist/leaflet.css';
import type {
  EnvironmentalResult,
  Category,
  Charity,
  Visualization,
} from '@/app/_types/resultsLayout';
// import { hotspotIcon } from '@/lib/leafletIcon';
import ShareResultsModal from '@/app/_components/interactive/resultsModal';

import dynamic from 'next/dynamic';
import type { LatLngExpression } from 'leaflet';

const MapContainer = dynamic(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { ssr: false }
);

const TileLayer = dynamic(
  () => import('react-leaflet').then((mod) => mod.TileLayer),
  { ssr: false }
);

const Marker = dynamic(
    () => import('react-leaflet').then((mod) => mod.Marker),
    { ssr: false }
  );
  
  const Popup = dynamic(
    () => import('react-leaflet').then((mod) => mod.Popup),
    { ssr: false }
  );

interface LeafletMapProps {
  center?: LatLngExpression;
  zoom?: number;
}

interface ResultsLayoutProps {
  results: EnvironmentalResult | null;
  isLoading?: boolean;
}

const ResultsLayout: React.FC<ResultsLayoutProps> = ({
  results,
  isLoading = false,
}) => {
    const [isClient, setIsClient] = React.useState(false);
    const [clientHotspotIcon, setClientHotspotIcon] = React.useState<any>(null);

React.useEffect(() => {
  import('leaflet').then((L) => {
    const icon = L.divIcon({
      html: `<img src="/icons/hotspot.svg" style="width:32px;height:32px;" />`,
      className: "", // remove default Leaflet classes if you want
      iconSize: [32, 32],
      iconAnchor: [16, 32],
      popupAnchor: [0, -32],
    });
    setClientHotspotIcon(icon);
  });
}, []);

React.useEffect(() => {
  setIsClient(true);
}, [results]);


  const handleShare = React.useCallback(async (url: string) => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Michigan Environmental Data - Enviducate',
          text: results
            ? `Check out these insights: ${results.originalQuery}`
            : 'Environmental data from Enviducate',
          url,
        });
      } catch {
        await navigator.clipboard.writeText(url);
      }
    } else {
      await navigator.clipboard.writeText(url);
    }
  }, [results]);

  const getCategoryColor = (category: Category): string => {
    switch (category) {
      case 'deforestation':
        return 'text-orange-300';
      case 'biodiversity':
        return 'text-green-300';
      case 'wildfire':
        return 'text-red-300';
      default:
        return 'text-blue-300';
    }
  };

  const getCategoryIcon = (category: Category): string => {
    switch (category) {
      case 'deforestation':
        return '🌲';
      case 'biodiversity':
        return '🦋';
      case 'wildfire':
        return '🔥';
      default:
        return '🌍';
    }
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-6 p-6 min-h-screen">
        {[...Array(2)].map((_, i) => (
          <div
            key={i}
            className="bg-black/20 backdrop-blur-md border border-white/10 rounded-2xl p-6 animate-pulse"
          >
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
          <p className="text-white/50">
            Ask a question about Michigan's environment to get started
          </p>
        </div>
      </div>
    );
  }

  return (
    
    <div id="results-container" className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6 min-h-screen">
      {/* LEFT COLUMN (scrollable) */}
      <div className="bg-black/20 backdrop-blur-md border border-white/10 rounded-2xl p-6 space-y-6 overflow-y-auto max-h-[calc(100vh-3rem)]">
        {/* Summary Section */}
        <div className="border-b border-white/10 pb-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">{getCategoryIcon(results.category)}</span>
            <span
              className={`text-sm uppercase tracking-wide font-medium ${getCategoryColor(
                results.category
              )}`}
            >
              {results.category}
            </span>
          </div>
          <h2 className="text-xl font-semibold text-white">
            {results.originalQuery}
          </h2>
          <div className="text-xs text-white/50 mt-2">
            Generated {new Date(results.generatedAt).toLocaleString()}
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-green-300">
            Environmental Analysis
          </h3>
          <p className="text-white/90 leading-relaxed">{results.summary} <br/><br/> *Note Data Points Reduced to 30-50 Most Relevant Points for Performance</p>
        </div>

        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-white/70 uppercase tracking-wide">
            Sources
          </h3>
          <div className="space-y-2">
            {results.sources.map((source: string, index: number) => (
              <div key={index} className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-green-400 mt-2 flex-shrink-0" />
                <span className="text-sm text-white/70">{source}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Charities Section */}
        <div className="space-y-4 border-t border-white/10 pt-6">
          <h3 className="text-lg font-semibold text-green-300">Ways to Help</h3>
          <div className="space-y-3">
            {results.charities.map((charity: Charity, index: number) => (
              <div
                key={index}
                className="bg-white/5 rounded-lg p-4 hover:bg-white/10 transition-colors group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-white group-hover:text-green-300 transition-colors">
                      {charity.name}
                    </h4>
                    <p className="text-sm text-white/70 mt-1">
                      {charity.description}
                    </p>
                  </div>
                  <a
                    href={charity.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-white/50 hover:text-green-300 transition-colors"
                  >
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M18 13V19A2 2 0 0 1 16 21H5A2 2 0 0 1 3 19V8A2 2 0 0 1 5 6H11"
                      />
                      <polyline
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        points="15 3 21 3 21 9"
                      />
                      <line
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        x1="10"
                        y1="14"
                        x2="21"
                        y2="3"
                      />
                    </svg>
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Share Section */}
        <div className="space-y-4 border-t border-white/10 pt-6">
          <h3 className="text-lg font-semibold text-green-300">Share Results</h3>
          <div className="space-y-3">
          {isClient && (
            <ShareResultsModal triggerText="Share These Insights" containerId="results-container" />
            )}
          </div>
        </div>
      </div>

      {/* RIGHT COLUMN – Placeholder Map */}
      <div className="bg-black/20 backdrop-blur-md border border-white/10 rounded-2xl overflow-hidden">
        <MapContainer
          key={results.generatedAt}
          center={[43.3338, -84.8024] as [number, number]}
          zoom={8}
          style={{ height: '100%', width: '100%', minHeight: 'calc(100vh - 3rem)' }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

            {clientHotspotIcon && results.visualizations
                .filter((v) => v.type === "pinpoints")
                .flatMap((v) =>
                v.data.map((point: any, index: number) => (
                    <Marker key={index} position={[point.lat, point.lng]} icon={clientHotspotIcon}>
                    <Popup>
                        <strong>{point.label}</strong>
                        <br />
                        {v.metadata.title}
                    </Popup>
                    </Marker>
                ))
                )}
        </MapContainer>
      </div>
    </div>
  );
};

export default ResultsLayout;
