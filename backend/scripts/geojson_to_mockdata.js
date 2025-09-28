#!/usr/bin/env node
/**
 * GeoJSON to MockData Converter
 * Converts GeoJSON files to MockData format for the Enviducate platform
 */

const fs = require('fs');
const path = require('path');

/**
 * Extract coordinates from GeoJSON features
 * @param {Object} geojson - GeoJSON object
 * @returns {Array} Array of coordinate objects with lat, lng, and label
 */
function extractCoordinates(geojson) {
    const coords = [];

    if (!geojson.features) {
        console.error('❌ Invalid GeoJSON: No features found');
        return coords;
    }

    geojson.features.forEach((feature) => {
        const label = feature.properties?.FieldName || feature.properties?.name || "Unknown";
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

/**
 * Sample coordinates evenly
 * @param {Array} coords - Array of coordinate objects
 * @param {number} n - Number of samples to take
 * @returns {Array} Sampled coordinates
 */
function sampleCoordinates(coords, n = 50) {
    if (coords.length <= n) {
        return coords;
    }

    const step = Math.max(Math.floor(coords.length / n), 1);
    const sampled = [];
    for (let i = 0; i < coords.length && sampled.length < n; i += step) {
        sampled.push(coords[i]);
    }
    return sampled;
}

/**
 * Generate category based on filename or content
 * @param {string} filename - Name of the file
 * @param {Array} coords - Coordinate data
 * @returns {string} Category string
 */
function generateCategory(filename, coords) {
    const name = filename.toLowerCase();
    
    if (name.includes('gas') || name.includes('energy') || name.includes('oil')) {
        return 'energy';
    } else if (name.includes('water') || name.includes('lake') || name.includes('river')) {
        return 'water';
    } else if (name.includes('forest') || name.includes('tree') || name.includes('wood')) {
        return 'forest';
    } else if (name.includes('wildlife') || name.includes('animal') || name.includes('bird')) {
        return 'wildlife';
    } else if (name.includes('air') || name.includes('pollution') || name.includes('quality')) {
        return 'air';
    } else {
        return 'environmental';
    }
}

/**
 * Generate basic summary based on data
 * @param {string} filename - Name of the file
 * @param {Array} coords - Coordinate data
 * @param {string} category - Data category
 * @returns {string} Summary text
 */
function generateSummary(filename, coords, category) {
    const count = coords.length;
    const categoryMap = {
        'energy': 'energy infrastructure and facilities',
        'water': 'water bodies and aquatic features',
        'forest': 'forest areas and vegetation',
        'wildlife': 'wildlife habitats and species locations',
        'air': 'air quality monitoring points',
        'environmental': 'environmental monitoring points'
    };

    const description = categoryMap[category] || 'environmental features';
    
    return `Geospatial data containing ${count} coordinate points representing ${description} in Michigan. This dataset provides valuable insights into the distribution and characteristics of ${description} across the state.`;
}

/**
 * Get relevant charities based on category
 * @param {string} category - Data category
 * @returns {Array} Array of charity objects
 */
function getRelevantCharities(category) {
    const charityMap = {
        'energy': [
            {
                name: "Michigan Environmental Council",
                url: "https://www.environmentalcouncil.org",
                description: "Advocating for clean energy and environmental protection in Michigan"
            },
            {
                name: "Sierra Club Michigan",
                url: "https://www.sierraclub.org/michigan",
                description: "Environmental protection and clean energy advocacy"
            }
        ],
        'water': [
            {
                name: "Great Lakes Protection Fund",
                url: "https://www.glpf.org",
                description: "Protecting the Great Lakes ecosystem"
            },
            {
                name: "Michigan Environmental Council",
                url: "https://www.environmentalcouncil.org",
                description: "Water quality protection in Michigan"
            }
        ],
        'forest': [
            {
                name: "Michigan Nature Association",
                url: "https://www.michigannature.org",
                description: "Protecting Michigan's natural areas and forests"
            },
            {
                name: "The Nature Conservancy Michigan",
                url: "https://www.nature.org/michigan",
                description: "Forest conservation and restoration"
            }
        ],
        'wildlife': [
            {
                name: "Michigan Audubon",
                url: "https://www.michiganaudubon.org",
                description: "Bird and wildlife conservation"
            },
            {
                name: "Michigan Nature Association",
                url: "https://www.michigannature.org",
                description: "Wildlife habitat protection"
            }
        ],
        'air': [
            {
                name: "Michigan Environmental Council",
                url: "https://www.environmentalcouncil.org",
                description: "Air quality protection and environmental health"
            },
            {
                name: "American Lung Association Michigan",
                url: "https://www.lung.org/michigan",
                description: "Clean air advocacy and lung health"
            }
        ]
    };

    return charityMap[category] || [
        {
            name: "Michigan Environmental Council",
            url: "https://www.environmentalcouncil.org",
            description: "Environmental protection in Michigan"
        },
        {
            name: "The Nature Conservancy Michigan",
            url: "https://www.nature.org/michigan",
            description: "Conservation and environmental protection"
        }
    ];
}

/**
 * Process a single GeoJSON file
 * @param {string} inputPath - Path to input GeoJSON file
 * @param {string} outputPath - Path to output JSON file
 */
function processFile(inputPath, outputPath) {
    try {
        console.log(`🔄 Processing: ${inputPath}`);
        
        // Load the GeoJSON
        const geojson = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
        
        // Extract coordinates
        const allCoords = extractCoordinates(geojson);
        if (allCoords.length === 0) {
            console.error(`❌ No coordinates found in ${inputPath}`);
            return false;
        }
        
        // Sample coordinates
        const sampledCoords = sampleCoordinates(allCoords, 50);
        
        // Generate metadata
        const filename = path.basename(inputPath, path.extname(inputPath));
        const category = generateCategory(filename, allCoords);
        const summary = generateSummary(filename, allCoords, category);
        const charities = getRelevantCharities(category);
        
        // Build the JSON object in MockData format
        const mockDataJSON = {
            id: `mock_${Date.now()}`,
            originalQuery: filename.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            category: category,
            summary: summary,
            sources: [
                "Michigan Environmental Data 2025",
                "Geospatial Analysis"
            ],
            charities: charities,
            visualizations: [
                {
                    type: "pinpoints",
                    data: sampledCoords,
                    metadata: {
                        title: filename.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                        description: summary,
                        source: "Michigan Environmental Data",
                        lastUpdated: new Date().toISOString(),
                        totalPoints: allCoords.length,
                        sampledPoints: sampledCoords.length
                    }
                }
            ],
            shareableUrl: `https://enviducate.org/mock-result-${Date.now()}`,
            generatedAt: new Date().toISOString()
        };
        
        // Write to output file
        fs.writeFileSync(outputPath, JSON.stringify(mockDataJSON, null, 2));
        console.log(`✅ Created: ${outputPath}`);
        
        return true;
        
    } catch (error) {
        console.error(`❌ Error processing ${inputPath}:`, error.message);
        return false;
    }
}

/**
 * Process all GeoJSON files in a directory
 * @param {string} inputDir - Input directory path
 * @param {string} outputDir - Output directory path
 */
function processDirectory(inputDir, outputDir) {
    try {
        // Create output directory if it doesn't exist
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        // Find all GeoJSON files
        const files = fs.readdirSync(inputDir)
            .filter(file => file.endsWith('.geojson') || file.endsWith('.json'))
            .map(file => path.join(inputDir, file));
        
        if (files.length === 0) {
            console.error(`❌ No GeoJSON files found in ${inputDir}`);
            return;
        }
        
        console.log(`🔄 Found ${files.length} GeoJSON files to process`);
        
        let successCount = 0;
        files.forEach(inputFile => {
            const filename = path.basename(inputFile, path.extname(inputFile));
            const outputFile = path.join(outputDir, `${filename}_processed.json`);
            
            if (processFile(inputFile, outputFile)) {
                successCount++;
            }
        });
        
        console.log(`✅ Successfully processed ${successCount}/${files.length} files`);
        
    } catch (error) {
        console.error(`❌ Error processing directory ${inputDir}:`, error.message);
    }
}

// Main execution
function main() {
    const args = process.argv.slice(2);
    
    if (args.length < 2) {
        console.log('Usage: node geojson_to_mockdata.js <input_path> <output_path>');
        console.log('  input_path: Path to GeoJSON file or directory');
        console.log('  output_path: Path to output JSON file or directory');
        process.exit(1);
    }
    
    const inputPath = args[0];
    const outputPath = args[1];
    
    if (fs.statSync(inputPath).isDirectory()) {
        processDirectory(inputPath, outputPath);
    } else {
        processFile(inputPath, outputPath);
    }
}

// Run if called directly
if (require.main === module) {
    main();
}

module.exports = {
    extractCoordinates,
    sampleCoordinates,
    generateCategory,
    generateSummary,
    getRelevantCharities,
    processFile,
    processDirectory
};

