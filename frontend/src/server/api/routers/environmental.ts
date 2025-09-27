import { z } from "zod";
import { createTRPCRouter, publicProcedure } from "@/server/api/trpc";

// Input validation schemas
const QuerySchema = z.object({
  query: z.string().min(1, "Query cannot be empty"),
  category: z.enum(["deforestation", "biodiversity", "wildfire"]).optional(),
  timeRange: z.string().optional(),
});

const LocationSchema = z.object({
  lat: z.number(),
  lng: z.number(),
  name: z.string(),
  value: z.number(),
  severity: z.enum(["low", "medium", "high"]),
});

// Response type schemas
const VisualizationDataSchema = z.object({
  type: z.enum(["pinpoints", "heatmap", "numbers"]),
  data: z.unknown(),
  metadata: z.object({
    title: z.string(),
    description: z.string(),
    source: z.string(),
    lastUpdated: z.string(),
  }),
});

// Mock data for development
const mockPinpointData = [
  { lat: 46.5547, lng: -84.3675, name: "Tahquamenon Falls State Park", value: 85, severity: "low" as const },
  { lat: 45.0218, lng: -83.5539, name: "Huron-Manistee Forest", value: 65, severity: "medium" as const },
  { lat: 46.9059, lng: -88.5498, name: "Copper Harbor", value: 40, severity: "high" as const },
  { lat: 42.4072, lng: -83.9424, name: "Detroit River", value: 75, severity: "medium" as const },
  { lat: 44.3106, lng: -85.6027, name: "Traverse City Bay", value: 90, severity: "low" as const },
];

const mockHeatmapData = {
  bounds: {
    north: 48.0,
    south: 41.0,
    east: -82.0,
    west: -90.0,
  },
  gridSize: 10,
  data: Array.from({ length: 100 }, (_, i) => ({
    lat: 41 + (i % 10) * 0.7,
    lng: -90 + Math.floor(i / 10) * 0.8,
    intensity: Math.random(),
    value: Math.floor(Math.random() * 100),
  })),
};

const mockNumbersData = {
  totalAffectedArea: 1250000, // acres
  percentageChange: -12.5,
  timeframe: "2017-2024",
  keyMetrics: [
    { label: "Forest Coverage", value: "52.1%", change: -2.3 },
    { label: "Wetland Area", value: "11.2M acres", change: -0.8 },
    { label: "Species Count", value: "2,847", change: 1.2 },
    { label: "Protected Areas", value: "102", change: 3.0 },
  ],
};

// Helper function to simulate Gemini API processing
async function processWithGemini(query: string): Promise<{
  category: "deforestation" | "biodiversity" | "wildfire";
  summary: string;
  sources: string[];
  charities: Array<{ name: string; url: string; description: string }>;
}> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Simple query categorization (replace with actual Gemini API)
  let category: "deforestation" | "biodiversity" | "wildfire" = "biodiversity";
  if (query.toLowerCase().includes("forest") || query.toLowerCase().includes("deforest")) {
    category = "deforestation";
  } else if (query.toLowerCase().includes("fire") || query.toLowerCase().includes("wildfire")) {
    category = "wildfire";
  }

  const mockResponses = {
    deforestation: {
      summary: "Michigan's Upper Peninsula has experienced a 12.5% reduction in forest coverage from 2017-2024, primarily due to industrial logging and urban expansion. The Huron-Manistee National Forests show the most significant changes, with approximately 125,000 acres affected. Climate change has accelerated natural forest stress, making trees more susceptible to disease and extreme weather events.",
      sources: ["Michigan DNR Forest Report 2024", "USFS Upper Peninsula Survey", "Michigan Environmental Council"],
      charities: [
        { name: "Michigan Forest Association", url: "https://michiganforests.com", description: "Promoting sustainable forestry practices" },
        { name: "Trees for Tomorrow", url: "https://treesfortomorrow.com", description: "Reforestation and education programs" },
        { name: "Great Lakes Forest Alliance", url: "https://greatlakesforest.org", description: "Protecting Great Lakes region forests" },
      ],
    },
    biodiversity: {
      summary: "Michigan's Great Lakes wetlands support over 2,800 species, with Saginaw Bay and Thunder Bay serving as critical biodiversity hotspots. Recent studies show a 8.3% increase in migratory bird populations but a 15% decline in native fish species. Invasive species like zebra mussels continue to impact ecosystem balance, while restoration efforts have successfully protected 102 critical habitats.",
      sources: ["Michigan DNR Wildlife Survey 2024", "Great Lakes Biodiversity Report", "Audubon Michigan"],
      charities: [
        { name: "Ducks Unlimited", url: "https://ducks.org", description: "Wetland habitat conservation" },
        { name: "Great Lakes Protection Fund", url: "https://glpf.org", description: "Ecosystem restoration and protection" },
        { name: "Michigan Audubon", url: "https://michiganaudubon.org", description: "Bird and habitat conservation" },
      ],
    },
    wildfire: {
      summary: "Michigan's Upper Peninsula faces moderate wildfire risk, with 35,000 acres classified as high-risk zones. Recent drought conditions and increasing temperatures have elevated fire danger levels by 22% since 2020. The Michigan DNR has implemented enhanced monitoring systems and community education programs, successfully reducing average fire response time to 12 minutes.",
      sources: ["Michigan DNR Fire Division", "National Interagency Fire Center", "Michigan State Climatology Office"],
      charities: [
        { name: "Michigan Forest Fire Prevention", url: "https://michigan.gov/dnr", description: "Fire prevention and education" },
        { name: "Wildfire Recovery Fund", url: "https://wildfirerecovery.org", description: "Supporting fire-affected communities" },
        { name: "Forest Service Foundation", url: "https://nationalforests.org", description: "Supporting forest management and recovery" },
      ],
    },
  };

  // Ensure the returned object includes the 'category' property to match the expected type
  return {
    category,
    ...mockResponses[category],
  };
}

export const environmentalRouter = createTRPCRouter({
  // Main query processing endpoint
  processQuery: publicProcedure
    .input(QuerySchema)
    .mutation(async ({ input }) => {
      try {
        // Process query with Gemini (mocked for now)
        const processed = await processWithGemini(input.query);
        
        // Generate visualizations based on category
        const visualizations = await generateVisualizations(processed.category, input.timeRange);
        
        return {
          id: `query_${Date.now()}`,
          originalQuery: input.query,
          category: processed.category,
          summary: processed.summary,
          sources: processed.sources,
          charities: processed.charities,
          visualizations,
          shareableUrl: `${process.env.NEXTAUTH_URL}/results/${Date.now()}`,
          generatedAt: new Date().toISOString(),
        };
      } catch (error) {
        throw new Error("Failed to process environmental query");
      }
    }),

  // Get visualization data
  getVisualization: publicProcedure
    .input(z.object({
      type: z.enum(["pinpoints", "heatmap", "numbers"]),
      category: z.enum(["deforestation", "biodiversity", "wildfire"]),
    }))
    .query(async ({ input }) => {
      return await generateSingleVisualization(input.type, input.category);
    }),

  // Get predefined queries for the search interface
  getPredefinedQueries: publicProcedure
    .query(() => {
      return [
        "Biodiversity hotspots in Michigan's Great Lakes wetlands",
        "Deforestation trends in Michigan's Upper Peninsula from 2017 to 2024", 
        "Wildfire risk areas in Michigan's Upper Peninsula",
        "Wetland conservation efforts in Saginaw Bay",
        "Forest recovery after logging in Huron-Manistee",
        "Invasive species impact on Michigan lakes",
        "Climate change effects on Michigan wildlife",
        "Protected areas in Michigan's state parks",
      ];
    }),

  // Share/get results by ID
  getSharedResult: publicProcedure
    .input(z.object({ id: z.string() }))
    .query(async ({ input }) => {
      // In a real app, this would fetch from database
      // For now, return mock data
      return {
        id: input.id,
        found: true,
        data: mockPinpointData, // This would be the actual stored result
      };
    }),
});

// Helper function to generate visualizations
async function generateVisualizations(category: "deforestation" | "biodiversity" | "wildfire", timeRange?: string) {
  const visualizations = [];
  
  // Always generate all three types
  visualizations.push(
    await generateSingleVisualization("pinpoints", category),
    await generateSingleVisualization("heatmap", category), 
    await generateSingleVisualization("numbers", category)
  );

  return visualizations;
}

async function generateSingleVisualization(
  type: "pinpoints" | "heatmap" | "numbers",
  category: "deforestation" | "biodiversity" | "wildfire"
) {
  // Simulate processing delay
  await new Promise(resolve => setTimeout(resolve, 500));

  const metadata = {
    deforestation: {
      title: "Forest Coverage Changes",
      description: "Areas of significant forest loss and recovery in Michigan",
      source: "Michigan DNR, USFS",
    },
    biodiversity: {
      title: "Biodiversity Hotspots",
      description: "Species-rich areas and conservation priorities",
      source: "Michigan DNR Wildlife Division",
    },
    wildfire: {
      title: "Wildfire Risk Assessment", 
      description: "Fire danger zones and prevention areas",
      source: "Michigan DNR Fire Division",
    },
  };

  const baseMetadata = {
    ...metadata[category],
    lastUpdated: new Date().toISOString(),
  };

  switch (type) {
    case "pinpoints":
      return {
        type: "pinpoints" as const,
        data: mockPinpointData.map(point => ({
          ...point,
          // Adjust values based on category
          value: category === "wildfire" ? point.value * 0.6 : point.value,
        })),
        metadata: baseMetadata,
      };

    case "heatmap":
      return {
        type: "heatmap" as const,
        data: {
          ...mockHeatmapData,
          data: mockHeatmapData.data.map(cell => ({
            ...cell,
            intensity: category === "deforestation" ? 1 - cell.intensity : cell.intensity,
          })),
        },
        metadata: baseMetadata,
      };

    case "numbers":
      return {
        type: "numbers" as const,
        data: {
          ...mockNumbersData,
          keyMetrics: mockNumbersData.keyMetrics.map(metric => ({
            ...metric,
            // Adjust based on category
            change: category === "wildfire" ? Math.abs(metric.change) : metric.change,
          })),
        },
        metadata: baseMetadata,
      };

    default:
      throw new Error(`Unknown visualization type: ${type}`);
  }
}