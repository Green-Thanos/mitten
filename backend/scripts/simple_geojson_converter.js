import fs from 'fs';

const inputFileName = "Michigan_Gas_Storage_Fields.geojson";
const outputFileName = "MockGasStorage.json";

// Load the GeoJSON
const geojson = JSON.parse(fs.readFileSync(inputFileName, 'utf8'));

// Flatten coordinates into a single array
function extractCoordinates(geojson) {
  const coords = [];

  geojson.features.forEach((feature) => {
    const label = feature.properties?.FieldName || "Unknown";
    const geometry = feature.geometry;

    if (geometry.type === "Polygon") {
      geometry.coordinates.forEach((ring) => {
        ring.forEach(([lng, lat]) => {
          coords.push({ lat, lng, label });
        });
      });
    } else if (geometry.type === "MultiPolygon") {
      geometry.coordinates.forEach((poly) => {
        poly.forEach((ring) => {
          ring.forEach(([lng, lat]) => {
            coords.push({ lat, lng, label });
          });
        });
      });
    } else if (geometry.type === "Point") {
      const [lng, lat] = geometry.coordinates;
      coords.push({ lat, lng, label });
    }
  });

  return coords;
}

// Sample 50 points evenly
function sampleCoordinates(coords, n = 50) {
  const step = Math.max(Math.floor(coords.length / n), 1);
  const sampled = [];
  for (let i = 0; i < coords.length && sampled.length < n; i += step) {
    sampled.push(coords[i]);
  }
  return sampled;
}

// Extract and sample
const allCoords = extractCoordinates(geojson);
const sampledCoords = sampleCoordinates(allCoords, 50);

// Build the JSON object in the same format as MockData
const MockDataJSON = {
  id: "mock_1",
  originalQuery: "Michigan Gas Storage Fields",
  category: "energy",
  summary: "Sampled gas storage field coordinates in Michigan.",
  sources: [
    "Michigan Gas Storage Data 2025"
  ],
  charities: [],
  visualizations: [
    {
      type: "pinpoints",
      data: sampledCoords,
      metadata: {
        title: "Gas Storage Fields",
        description: "50 sampled coordinates from Michigan gas storage fields.",
        source: "Michigan Gas Storage Data",
        lastUpdated: new Date().toISOString()
      }
    }
  ],
  shareableUrl: "https://enviducate.org/mock-result",
  generatedAt: new Date().toISOString()
};

// Write to a JSON file
fs.writeFileSync(outputFileName, JSON.stringify(MockDataJSON, null, 2));
console.log(`${outputFileName} created successfully!`);

