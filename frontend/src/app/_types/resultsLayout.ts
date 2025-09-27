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
  
  export interface EnvironmentalResult {
    category: Category;
    originalQuery: string;
    generatedAt: string; // ISO string
    summary: string;
    sources: string[];
    charities: Charity[];
    visualizations?: Visualization[];
    shareableUrl: string;
  }
  