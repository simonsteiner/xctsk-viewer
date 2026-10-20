// Task map: draws the task GeoJSON (turnpoint cylinders, routes) on a
// Leaflet map and adds the airspace overlay. The page passes the GeoJSON in.
function initMap(geojson) {
    // Initialize the map
    var map = L.map('map').setView([46.0, 8.0], 10);

    // Add Stadia Maps terrain layer
    L.tileLayer('https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://stadiamaps.com/" target="_blank">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>'
    }).addTo(map);

    var bounds = L.latLngBounds();

    // Debug: Log GeoJSON data to console
    console.log('GeoJSON data:', geojson);
    if (geojson && geojson.features) {
        console.log('Number of features:', geojson.features.length);
        geojson.features.forEach(function (feature, index) {
            console.log('Feature ' + index + ':', feature.properties.type, feature.properties.name || 'unnamed', feature.geometry.type);
        });
    }

    // Calculate bounds from GeoJSON features
    if (geojson && geojson.features) {
        geojson.features.forEach(function (feature) {
            if (feature.geometry && feature.geometry.type === 'Polygon' && feature.geometry.coordinates) {
                feature.geometry.coordinates[0].forEach(function (coord) {
                    bounds.extend([coord[1], coord[0]]);
                });
            } else if (feature.geometry && feature.geometry.type === 'LineString' && feature.geometry.coordinates) {
                feature.geometry.coordinates.forEach(function (coord) {
                    bounds.extend([coord[1], coord[0]]);
                });
            } else if (feature.geometry && feature.geometry.type === 'Point' && feature.geometry.coordinates) {
                bounds.extend([feature.geometry.coordinates[1], feature.geometry.coordinates[0]]);
            }
        });
    }

    // Style function for features - use colors from GeoJSON properties
    function featureStyle(feature) {
        if (!feature.properties) return {};

        var props = feature.properties;

        // If colors are defined in properties, use them directly
        if (props.color) {
            return {
                color: props.color,
                weight: props.weight || 2,
                opacity: props.opacity || 0.7,
                fillColor: props.fillColor || props.color,
                fillOpacity: props.fillOpacity || 0.1
            };
        }
    }

    // Simplified feature interaction without hover effects
    function onEachFeature(feature, layer) {
        var props = feature.properties;
        var name = props.name;
        var description = props.description;
        var radius = props.radius;
        var type = props.type;
        var ctype = props.ctype;

        // Add arrows to optimized route
        if (type === 'optimized_route' && props.arrowheads) {
            // Create arrow decorators
            var arrowDecorator = L.polylineDecorator(layer, {
                patterns: [{
                    offset: '10%',
                    repeat: props.arrow_spacing ? (props.arrow_spacing + 'm') : '50000m',
                    symbol: L.Symbol.arrowHead({
                        pixelSize: props.arrow_size || 8,
                        headAngle: 60,
                        pathOptions: {
                            fillOpacity: 1,
                            weight: 0,
                            color: props.arrow_color || props.color || '#ff4136'
                        }
                    })
                }]
            });
            arrowDecorator.addTo(map);
        }

        // Create comprehensive popup content
        var popupContent = '<div>';
        if (name) {
            popupContent += '<h6><strong>' + name + '</strong></h6>';
        } else if (type) {
            popupContent += '<h6>' + type.charAt(0).toUpperCase() + type.slice(1) + '</h6>';
        }

        if (description) {
            popupContent += '<p>' + description + '</p>';
        }

        if (ctype) {
            popupContent += '<p><em>Type: ' + ctype + '</em></p>';
        } else if (type && type !== 'cylinder') {
            popupContent += '<p><em>Type: ' + type + '</em></p>';
        }

        if (radius) {
            popupContent += '<small>Radius: ' + radius + 'm</small>';
        }

        popupContent += '</div>';

        if (name || description || type) {
            layer.bindPopup(popupContent);
        }
    }

    // Function to handle point features (create circles for cylinder turnpoints)
    function pointToLayer(feature, latlng) {
        if (feature.properties && feature.properties.type === 'cylinder' && feature.properties.radius) {
            return L.circle(latlng, {
                radius: feature.properties.radius
            });
        }
        return L.marker(latlng);
    }

    // Add GeoJSON data to map
    if (geojson) {
        L.geoJSON(geojson, {
            style: featureStyle,
            onEachFeature: onEachFeature,
            pointToLayer: pointToLayer
        }).addTo(map);
    }

    // Fit bounds or set default view
    if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [20, 20] });
    } else {
        console.warn('No valid bounds found, using default view');
    }

    // Add the airspace overlay (lazy-loaded, toggleable)
    addAirspaceOverlay(map);
}
