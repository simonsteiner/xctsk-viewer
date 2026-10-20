// Airspace overlay: a toggleable, lazy-loaded Leaflet layer over the task map,
// with its legend, upload control, stacked popup and side view.


// Fetch airspace GeoJSON and expose it as a toggleable Leaflet overlay.
// Colouring, class-badge popups, hover highlight and legend follow the
// airspace-viewer project; adapted here to a lazy-loaded secondary overlay.
function addAirspaceOverlay(map) {
    var defaultWeight = 2;
    var highlightWeight = 5;

    // Style airspace features from the colour supplied in their properties
    function airspaceStyle(feature) {
        var color = (feature.properties && feature.properties.color) || '#999999';
        var isLine = feature.geometry && feature.geometry.type === 'LineString';
        return {
            color: color,
            weight: isLine ? 3 : defaultWeight,
            opacity: 0.6,
            fillColor: color,
            fillOpacity: isLine ? 0 : 0.35
        };
    }

    // Clicks are handled on the map itself (stacked popup of every airspace
    // at the clicked point), so features only wire up the hover highlight
    // and keep a feature -> layer link for zooming from the popup list.
    function onEachAirspace(feature, layer) {
        feature._layer = layer;
        layer.on('mouseover', function () { layer.setStyle({ weight: highlightWeight }); });
        layer.on('mouseout', function () { layer.setStyle({ weight: airspaceStyle(feature).weight }); });
    }

    var airspaceLayer = L.geoJSON(null, {
        style: airspaceStyle,
        onEachFeature: onEachAirspace
    });

    // Legend built from the class/colour pairs present in the current data
    var legendItems = {};
    var legendDiv = null;
    var legendVisible = false;

    function buildLegendHTML() {
        var html = '<h6>Airspace Classes</h6>';
        Object.keys(legendItems).sort(function (a, b) { return a.localeCompare(b); }).forEach(function (cls) {
            html += '<div class="legend-item"><div class="legend-color" style="background:'
                + safeColor(legendItems[cls]) + '"></div><span>Class ' + escapeHtml(cls) + '</span></div>';
        });
        return html;
    }

    var legend = L.control({ position: 'bottomright' });
    legend.onAdd = function () {
        legendDiv = L.DomUtil.create('div', 'legend airspace-legend');
        legendDiv.innerHTML = buildLegendHTML();
        return legendDiv;
    };

    function renderLegend() {
        if (legendVisible && legendDiv) legendDiv.innerHTML = buildLegendHTML();
    }
    function showLegend() {
        if (!legendVisible) { legend.addTo(map); legendVisible = true; }
        else { renderLegend(); }
    }
    function hideLegend() {
        if (legendVisible) { legend.remove(); legendVisible = false; }
    }

    // Upload control: swap the active airspace dataset with a custom OpenAir
    // file, the xcontest COMP CH layer, or reset to the bundled default.
    var statusEl, fileInput, resetBtn, compBtn;
    var uploadControl = L.control({ position: 'topleft' });
    uploadControl.onAdd = function () {
        var div = L.DomUtil.create('div', 'airspace-upload leaflet-bar');
        div.innerHTML =
            '<label class="au-title">Custom airspace</label>'
            + '<input type="file" class="au-file" accept=".txt,.air,.openair">'
            + '<button type="button" class="au-comp">Load COMP CH (xcontest)</button>'
            + '<button type="button" class="au-reset">Reset to Switzerland</button>'
            + '<div class="au-status"></div>';
        L.DomEvent.disableClickPropagation(div);
        L.DomEvent.disableScrollPropagation(div);
        fileInput = div.querySelector('.au-file');
        compBtn = div.querySelector('.au-comp');
        resetBtn = div.querySelector('.au-reset');
        statusEl = div.querySelector('.au-status');
        return div;
    };
    uploadControl.addTo(map);

    function setStatus(msg, isError) {
        if (!statusEl) return;
        statusEl.textContent = msg || '';
        statusEl.classList.toggle('au-error', !!isError);
    }

    L.control.layers(null, { 'Airspace': airspaceLayer }, { collapsed: false }).addTo(map);
    var loaded = false;
    var airspaceData = null; // latest GeoJSON, used for point lookups

    // Fetch /api/airspaces and (re)render the layer + legend.
    // fit: when true, zoom the map to the airspace extent.
    function loadAirspaces(fit) {
        return fetch('/api/airspaces')
            .then(function (r) {
                if (!r.ok) throw new Error('HTTP ' + r.status);
                return r.json();
            })
            .then(function (data) {
                airspaceData = data;
                (data.features || []).forEach(function (f, i) { f._idx = i; });
                airspaceLayer.clearLayers();
                airspaceLayer.addData(data);
                legendItems = {};
                (data.features || []).forEach(function (f) {
                    var p = f.properties || {};
                    if (p.class && p.color) legendItems[p.class] = p.color;
                });
                loaded = true;
                renderLegend();
                if (fit && airspaceLayer.getBounds().isValid()) {
                    map.fitBounds(airspaceLayer.getBounds(), { padding: [20, 20] });
                }
            });
    }

    // Ensure the overlay is visible on the map (updates the layers-control checkbox)
    function ensureVisible() {
        if (!map.hasLayer(airspaceLayer)) map.addLayer(airspaceLayer);
        showLegend();
    }

    // Toggle from the layers control: lazy-load the first time it is switched on
    map.on('overlayadd', function (e) {
        if (e.layer !== airspaceLayer) return;
        showLegend();
        if (!loaded) loadAirspaces(false).catch(function (err) {
            console.error('Failed to load airspaces:', err);
        });
    });
    map.on('overlayremove', function (e) {
        if (e.layer === airspaceLayer) hideLegend();
    });

    // Handle a custom airspace file upload
    function onFileChosen() {
        var file = fileInput.files && fileInput.files[0];
        if (!file) return;
        var fd = new FormData();
        fd.append('file', file);
        setStatus('Uploading ' + file.name + '…');
        fetch('/api/airspaces/upload', { method: 'POST', body: fd })
            .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, body: j }; }); })
            .then(function (res) {
                if (!res.ok) { setStatus(res.body.error || 'Upload failed', true); return; }
                ensureVisible();
                return loadAirspaces(true).then(function () {
                    setStatus('Loaded ' + res.body.count + ' airspaces from ' + res.body.filename);
                });
            })
            .catch(function (err) {
                console.error('Upload error:', err);
                setStatus('Upload error', true);
            })
            .finally(function () { if (fileInput) fileInput.value = ''; });
    }

    // Reset back to the bundled Switzerland dataset
    function onReset() {
        setStatus('Resetting…');
        fetch('/api/airspaces/reset', { method: 'POST' })
            .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, body: j }; }); })
            .then(function (res) {
                if (!res.ok) { setStatus(res.body.error || 'Reset failed', true); return; }
                ensureVisible();
                return loadAirspaces(true).then(function () {
                    setStatus('Reset to ' + res.body.filename);
                });
            })
            .catch(function (err) {
                console.error('Reset error:', err);
                setStatus('Reset error', true);
            });
    }

    // Fetch the current COMP CH competition airspace from xcontest
    function onLoadCompCh() {
        if (compBtn) compBtn.disabled = true;
        setStatus('Fetching COMP CH from xcontest…');
        fetch('/api/airspaces/comp-ch', { method: 'POST' })
            .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, body: j }; }); })
            .then(function (res) {
                if (!res.ok) { setStatus(res.body.error || 'Fetch failed', true); return; }
                ensureVisible();
                return loadAirspaces(true).then(function () {
                    setStatus('Loaded ' + res.body.count + ' airspaces from ' + res.body.filename);
                });
            })
            .catch(function (err) {
                console.error('COMP CH fetch error:', err);
                setStatus('Fetch error', true);
            })
            .finally(function () { if (compBtn) compBtn.disabled = false; });
    }

    if (fileInput) fileInput.addEventListener('change', onFileChosen);
    if (compBtn) compBtn.addEventListener('click', onLoadCompCh);
    if (resetBtn) resetBtn.addEventListener('click', onReset);

    var handleSideViewClick = addAirspaceSideView(map, {
        getData: function () { return airspaceData; },
        ensureVisible: ensureVisible,
        load: loadAirspaces
    });

    // Zoom to an airspace feature from popup/side-view list markup
    window.zoomToAirspaceFeature = function (idx) {
        var feature = airspaceData && airspaceData.features[idx];
        if (feature && feature._layer) {
            map.closePopup();
            map.fitBounds(feature._layer.getBounds());
        }
    };

    // Task-feature popups open on the layer click before the map click
    // fires; remember when, so the stacked popup does not replace them.
    var popupOpenedAt = 0;
    map.on('popupopen', function () { popupOpenedAt = Date.now(); });

    map.on('click', function (e) {
        if (handleSideViewClick(e)) return;
        if (!map.hasLayer(airspaceLayer)) return;
        if (Date.now() - popupOpenedAt < 100) return; // task popup wins
        var hits = findAirspacesAtPoint(airspaceData, e.latlng);
        if (!hits.length) return;
        L.popup({ maxWidth: 320, maxHeight: 340 })
            .setLatLng(e.latlng)
            .setContent(generateStackedListHTML(hits))
            .openOn(map);
    });
}
