// Airspace helpers shared by the overlay, the stacked popup and the side view:
// markup escaping, point-in-airspace lookup and altitude resolution.

// Airspace properties come from untrusted data (uploaded OpenAir files
// and the xcontest API), so escape everything before building markup.
function escapeHtml(value) {
    return String(value == null ? '' : value)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}
// Only allow simple hex colours in style attributes; fall back to grey.
function safeColor(value) {
    return /^#[0-9a-fA-F]{3,8}$/.test(value || '') ? value : '#999999';
}

// Ray casting on a GeoJSON ring ([lng, lat] pairs)
function pointInRing(lng, lat, ring) {
    var inside = false;
    for (var i = 0, j = ring.length - 1; i < ring.length; j = i++) {
        var xi = ring[i][0], yi = ring[i][1];
        var xj = ring[j][0], yj = ring[j][1];
        if (((yi > lat) !== (yj > lat)) &&
            (lng < (xj - xi) * (lat - yi) / (yj - yi) + xi)) {
            inside = !inside;
        }
    }
    return inside;
}

function featureContainsPoint(feature, latlng) {
    if (!feature.geometry || feature.geometry.type !== 'Polygon') return false;
    var rings = feature.geometry.coordinates;
    if (!rings.length || !pointInRing(latlng.lng, latlng.lat, rings[0])) return false;
    // Point must not fall into a hole
    for (var i = 1; i < rings.length; i++) {
        if (pointInRing(latlng.lng, latlng.lat, rings[i])) return false;
    }
    return true;
}

// Every airspace in the GeoJSON collection that contains the point.
function findAirspacesAtPoint(airspaceData, latlng) {
    if (!airspaceData || !airspaceData.features) return [];
    return airspaceData.features.filter(function (f) { return featureContainsPoint(f, latlng); });
}

// Resolve a bound to meters AMSL for sorting/plotting.
// AGL bounds are offset by the ground elevation when known.
function resolveAltitudeMeters(meters, ref, groundElevation) {
    if (meters === null || meters === undefined) return null; // unlimited/unknown
    if (ref === 'AGL') return (groundElevation || 0) + meters;
    return meters; // AMSL or FL (standard atmosphere approximation)
}

function sortKeyLower(props) {
    var v = resolveAltitudeMeters(props.lowerMeters, props.lowerRef, 0);
    return v === null ? 0 : v;
}

// Popup listing every airspace at a clicked point. Each item zooms to its
// airspace through the global zoomToAirspaceFeature the overlay defines.
function generateStackedListHTML(features) {
    // Highest floor first, so the list reads like the vertical stack
    var sorted = features.slice().sort(function (a, b) {
        return sortKeyLower(b.properties) - sortKeyLower(a.properties);
    });

    var items = sorted.map(function (feature) {
        var p = feature.properties;
        return '<div class="stacked-item" onclick="zoomToAirspaceFeature(' + feature._idx + ')" title="Zoom to airspace">'
            + '<span class="stacked-color" style="background:' + safeColor(p.color) + '"></span>'
            + '<div class="stacked-text">'
            + '<div class="stacked-name">' + escapeHtml(p.name || 'Airspace') + '</div>'
            + '<div class="stacked-bounds">Class ' + escapeHtml(p.class || '?') + ' &middot; '
            + escapeHtml(p.lowerBound || '?') + ' &ndash; ' + escapeHtml(p.upperBound || '?') + '</div>'
            + '</div></div>';
    }).join('');

    return '<div class="stacked-popup">'
        + '<div class="stacked-title">' + sorted.length + ' airspace' + (sorted.length !== 1 ? 's' : '') + ' at this point</div>'
        + items + '</div>';
}
