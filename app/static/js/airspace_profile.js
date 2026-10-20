// Side-view profile: renders the vertical cross-section of the airspaces at a
// point (an SVG bar per airspace plus a details list) as panel markup.

var UNLIMITED_DISPLAY_MARGIN = 1.15; // headroom above the highest finite bound

function formatMeters(m) {
    return Math.round(m) + ' m';
}

// Human-readable resolved bounds line, e.g. "GND – 2438 m AMSL".
// Bounds that cannot be resolved to meters (unlimited or unknown)
// fall back to their original text.
function describeBounds(p, ground) {
    var lower = resolveAltitudeMeters(p.lowerMeters, p.lowerRef, ground || 0);
    var upper = resolveAltitudeMeters(p.upperMeters, p.upperRef, ground || 0);
    var lowerTxt = lower === null ? escapeHtml(p.lowerBound) : formatMeters(lower) + ' AMSL';
    var upperTxt = upper === null ? escapeHtml(p.upperBound) : formatMeters(upper) + ' AMSL';
    return escapeHtml(p.lowerBound || '?') + ' &ndash; ' + escapeHtml(p.upperBound || '?')
        + ' <span class="sideview-resolved">(&asymp; ' + lowerTxt + ' &ndash; ' + upperTxt + ')</span>';
}

function niceTickStep(range) {
    var targets = [100, 200, 250, 500, 1000, 2000, 2500, 5000, 10000];
    var raw = range / 6;
    for (var i = 0; i < targets.length; i++) {
        if (targets[i] >= raw) return targets[i];
    }
    return targets[targets.length - 1];
}

// Panel markup for the airspaces (features) at latlng. ground is the
// ground elevation in meters, or null when unknown; note is an optional
// status line shown above the plot.
function buildSideViewHTML(latlng, ground, features, note) {
    var groundM = (ground === null || ground === undefined) ? null : ground;
    var g = groundM || 0;

    // Sort ground-up so bar order matches the physical stack,
    // resolving AGL floors against the known ground elevation
    function groundSortKey(p) {
        var v = resolveAltitudeMeters(p.lowerMeters, p.lowerRef, g);
        return v === null ? 0 : v;
    }
    var sorted = features.slice().sort(function (a, b) {
        return groundSortKey(a.properties) - groundSortKey(b.properties);
    });

    // Vertical extent of the plot
    var maxFinite = 0;
    sorted.forEach(function (f) {
        var p = f.properties;
        var lower = resolveAltitudeMeters(p.lowerMeters, p.lowerRef, g);
        var upper = resolveAltitudeMeters(p.upperMeters, p.upperRef, g);
        maxFinite = Math.max(maxFinite, lower || 0, upper || 0);
    });
    maxFinite = Math.max(maxFinite, g + 1000);
    var maxAlt = Math.ceil((maxFinite * UNLIMITED_DISPLAY_MARGIN) / 500) * 500;

    // SVG geometry
    var W = 460, H = 320;
    var m = { top: 14, right: 12, bottom: 22, left: 58 };
    var plotW = W - m.left - m.right;
    var plotH = H - m.top - m.bottom;
    function y(alt) { return m.top + plotH - (alt / maxAlt) * plotH; }

    var svg = '<svg viewBox="0 0 ' + W + ' ' + H + '" class="sideview-svg" role="img" aria-label="Vertical airspace profile">';
    svg += '<rect x="' + m.left + '" y="' + m.top + '" width="' + plotW + '" height="' + plotH + '" class="sideview-sky"/>';

    // Y axis ticks + gridlines
    var step = niceTickStep(maxAlt);
    for (var alt = 0; alt <= maxAlt; alt += step) {
        var ty = y(alt);
        svg += '<line x1="' + m.left + '" y1="' + ty + '" x2="' + (W - m.right) + '" y2="' + ty + '" class="sideview-grid"/>';
        svg += '<text x="' + (m.left - 6) + '" y="' + (ty + 3.5) + '" class="sideview-tick" text-anchor="end">' + alt + '</text>';
    }
    svg += '<text x="12" y="' + (m.top + 2) + '" class="sideview-axis-label">m AMSL</text>';

    // Ground
    if (groundM !== null) {
        var gy = y(Math.min(groundM, maxAlt));
        svg += '<rect x="' + m.left + '" y="' + gy + '" width="' + plotW + '" height="' + (m.top + plotH - gy) + '" class="sideview-ground"/>';
        svg += '<line x1="' + m.left + '" y1="' + gy + '" x2="' + (W - m.right) + '" y2="' + gy + '" class="sideview-ground-line"/>';
        svg += '<text x="' + (W - m.right - 4) + '" y="' + (gy - 4) + '" text-anchor="end" class="sideview-ground-label">ground ' + formatMeters(groundM) + '</text>';
    }

    // Airspace columns
    var n = sorted.length;
    var slot = n ? plotW / n : plotW;
    var barW = Math.min(slot * 0.72, 90);

    sorted.forEach(function (f, i) {
        var p = f.properties;
        var color = safeColor(p.color);
        var lower = resolveAltitudeMeters(p.lowerMeters, p.lowerRef, g) || 0;
        var upperRaw = resolveAltitudeMeters(p.upperMeters, p.upperRef, g);
        // Only a true unlimited ceiling extends to the plot top with an ∞
        // marker; unknown/unparseable uppers get a short dashed band with "?"
        var unlimited = p.upperRef === 'UNLIMITED';
        var unknownUpper = !unlimited && upperRaw === null;
        var upper = unlimited ? maxAlt
            : unknownUpper ? Math.min(lower + 0.08 * maxAlt, maxAlt)
                : Math.min(upperRaw, maxAlt);

        var x = m.left + slot * i + (slot - barW) / 2;
        var yTop = y(upper);
        var yBottom = y(Math.min(lower, maxAlt));
        var h = Math.max(yBottom - yTop, 2);

        svg += '<g class="sideview-bar">';
        svg += '<rect x="' + x + '" y="' + yTop + '" width="' + barW + '" height="' + h + '" fill="' + color
            + '" fill-opacity="0.45" stroke="' + color + '" stroke-width="1.5"' + (unlimited || unknownUpper ? ' stroke-dasharray="4 3"' : '') + '/>';
        if (unlimited || unknownUpper) {
            svg += '<text x="' + (x + barW / 2) + '" y="' + (yTop + 12) + '" text-anchor="middle" class="sideview-unlimited">' + (unlimited ? '&#8734;' : '?') + '</text>';
        }
        // Number badge linking bar to the list below
        var badgeY = Math.max(yTop + h / 2, yTop + 10);
        svg += '<circle cx="' + (x + barW / 2) + '" cy="' + badgeY + '" r="9" fill="' + color + '"/>';
        svg += '<text x="' + (x + barW / 2) + '" y="' + (badgeY + 3.5) + '" text-anchor="middle" class="sideview-badge">' + (i + 1) + '</text>';
        svg += '<title>' + escapeHtml(p.name || 'Airspace') + ' (Class ' + escapeHtml(p.class || '?') + ')\n'
            + escapeHtml(p.lowerBound || '?') + ' – ' + escapeHtml(p.upperBound || '?') + '</title>';
        svg += '</g>';
    });

    svg += '<line x1="' + m.left + '" y1="' + m.top + '" x2="' + m.left + '" y2="' + (m.top + plotH) + '" class="sideview-axis"/>';
    svg += '</svg>';

    // Details list
    var list;
    if (n) {
        list = sorted.map(function (f, i) {
            var p = f.properties;
            return '<div class="sideview-item" onclick="zoomToAirspaceFeature(' + f._idx + ')" title="Zoom to airspace">'
                + '<span class="sideview-item-badge" style="background:' + safeColor(p.color) + '">' + (i + 1) + '</span>'
                + '<div class="stacked-text">'
                + '<div class="stacked-name">' + escapeHtml(p.name || 'Airspace')
                + ' <span class="sideview-class">Class ' + escapeHtml(p.class || '?') + '</span></div>'
                + '<div class="stacked-bounds">' + describeBounds(p, groundM) + '</div>'
                + '</div></div>';
        }).join('');
    } else {
        list = '<div class="sideview-empty">No airspaces at this point.</div>';
    }

    var groundTxt = groundM === null
        ? ''
        : '<span class="sideview-ground-info">Ground: ' + formatMeters(groundM) + ' AMSL</span>';

    return '<div class="sideview-header"><div><strong>Side view</strong>'
        + '<span class="sideview-coords">' + latlng.lat.toFixed(4) + ', ' + latlng.lng.toFixed(4) + '</span>'
        + groundTxt + '</div>'
        + '<button class="sideview-close" onclick="closeAirspaceSideView()" title="Close" aria-label="Close side view">&times;</button></div>'
        + (note ? '<div class="sideview-note">' + escapeHtml(note) + '</div>' : '')
        + svg
        + '<div class="sideview-list">' + list + '</div>';
}
