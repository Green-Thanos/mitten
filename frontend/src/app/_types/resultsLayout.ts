// types.ts
export interface Charity {
    name: string;
    description: string;
    url: string;
  }
  
  export interface Visualization {
    id: string;
    description: string;
    imageUrl: string;
  }
  
  export type Category =
    | 'deforestation'
    | 'biodiversity'
    | 'wildfire'
    | 'other';
  
  // Define an interface for Map Marker Points
export interface MapMarker {
  lat: number;
  lng: number;
  label: string;
}

// Extend your EnvironmentalResult interface if needed
export interface Visualization {
  type: "pinpoints" | "heatmap" | "numbers";
  data: any;
  metadata: {
    title: string;
    description: string;
    source: string;
    lastUpdated: string;
  };
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
