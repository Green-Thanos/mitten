// Type definitions for environmental data
export interface LocationPoint {
    lat: number;
    lng: number;
    name: string;
    value: number;
    severity: "low" | "medium" | "high";
  }
  
  export interface HeatmapCell {
    lat: number;
    lng: number;
    intensity: number;
    value: number;
  }
  
  export interface HeatmapData {
    bounds: {
      north: number;
      south: number;
      east: number;
      west: number;
    };
    gridSize: number;
    data: HeatmapCell[];
  }
  
  export interface KeyMetric {
    label: string;
    value: string;
    change: number;
  }
  
  export interface NumbersData {
    totalAffectedArea: number;
    percentageChange: number;
    timeframe: string;
    keyMetrics: KeyMetric[];
  }
  
  export interface VisualizationMetadata {
    title: string;
    description: string;
    source: string;
    lastUpdated: string;
  }
  
  export interface Visualization {
    type: "pinpoints" | "heatmap" | "numbers";
    data: LocationPoint[] | HeatmapData | NumbersData;
    metadata: VisualizationMetadata;
  }
  
  export interface Charity {
    name: string;
    url: string;
    description: string;
  }
  
  export interface EnvironmentalResult {
    id: string;
    originalQuery: string;
    category: "deforestation" | "biodiversity" | "wildfire";
    summary: string;
    sources: string[];
    charities: Charity[];
    visualizations: Visualization[];
    shareableUrl: string;
    generatedAt: string;
  }
  
  export interface SearchInterfaceProps {
    onResults?: (results: EnvironmentalResult) => void;
    onSearchStart?: () => void;
    className?: string;
  }
  
  export interface VisualizationProps {
    data: any;
    metadata: VisualizationMetadata;
  }
  
  export interface ResultsLayoutProps {
    results: EnvironmentalResult | null;
    isLoading?: boolean;
  }