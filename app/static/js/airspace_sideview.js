// Side view: a map control that toggles side-view mode; in that mode a map
// click shows the vertical airspace profile of the clicked point in #sideview.
//
// overlay is the airspace overlay's handle: getData() returns the loaded
// GeoJSON (or null), ensureVisible() shows the layer, load(fit) fetches it.
// Returns handleClick(e), which the map click handler calls first; it returns
// true when side-view mode took the click.
function addAirspaceSideView(map, overlay) {
    var sideViewMode = false;
    var sideViewMarker = null;
    var sideviewPanel = document.getElementById('sideview');
    var ELEVATION_API = 'https://api.open-meteo.com/v1/elevation';

    var sideViewControl = L.control({ position: 'topleft' });
    sideViewControl.onAdd = function () {
        var container = L.DomUtil.create('div', 'leaflet-bar');
        var btn = L.DomUtil.create('a', 'side-view-toggle', container);
        btn.href = '#';
        btn.innerHTML = '⛰';
        btn.title = 'Toggle side view mode (click map to see the vertical airspace profile)';
        btn.setAttribute('role', 'button');
        btn.setAttribute('aria-label', 'Toggle side view mode');
        btn.setAttribute('aria-pressed', 'false');
        L.DomEvent.on(btn, 'click', function (ev) {
            L.DomEvent.stop(ev);
            setSideViewMode(!sideViewMode, btn);
        });
        return container;
    };
    sideViewControl.addTo(map);

    function setSideViewMode(active, btn) {
        sideViewMode = active;
        var toggleBtn = btn || document.querySelector('.side-view-toggle');
        if (toggleBtn) {
            toggleBtn.classList.toggle('active', active);
            toggleBtn.setAttribute('aria-pressed', String(active));
        }
        map.getContainer().classList.toggle('side-view-cursor', active);
        if (!active) closeSideView();
    }

    function closeSideView() {
        if (sideviewPanel) sideviewPanel.classList.add('hidden');
        if (sideViewMarker) {
            map.removeLayer(sideViewMarker);
            sideViewMarker = null;
        }
    }
    window.closeAirspaceSideView = closeSideView;

    function fetchGroundElevation(lat, lng) {
        var url = ELEVATION_API + '?latitude=' + lat.toFixed(5) + '&longitude=' + lng.toFixed(5);
        return fetch(url)
            .then(function (r) {
                if (!r.ok) throw new Error('Elevation API returned ' + r.status);
                return r.json();
            })
            .then(function (data) {
                if (!data.elevation || !data.elevation.length) throw new Error('No elevation data');
                return data.elevation[0];
            });
    }

    function onSideViewClick(e) {
        var latlng = e.latlng;
        map.closePopup(); // a task-feature popup may have opened on this click

        // The profile needs airspace data; load it (and show the overlay) first
        if (!overlay.getData()) {
            overlay.ensureVisible();
            overlay.load(false)
                .then(function () { showSideViewAt(latlng); })
                .catch(function (err) { console.error('Failed to load airspaces:', err); });
            return;
        }
        showSideViewAt(latlng);
    }

    function renderSideView(latlng, ground, features, note) {
        if (!sideviewPanel) return;
        sideviewPanel.innerHTML = buildSideViewHTML(latlng, ground, features, note);
        sideviewPanel.classList.remove('hidden');
    }

    function showSideViewAt(latlng) {
        if (sideViewMarker) map.removeLayer(sideViewMarker);
        sideViewMarker = L.marker(latlng).addTo(map);

        var hits = findAirspacesAtPoint(overlay.getData(), latlng);
        renderSideView(latlng, null, hits, 'Loading ground elevation…');

        fetchGroundElevation(latlng.lat, latlng.lng)
            .then(function (ground) {
                // Ignore stale responses if the user clicked elsewhere meanwhile
                if (!sideViewMode || !sideViewMarker || !sideViewMarker.getLatLng().equals(latlng)) return;
                renderSideView(latlng, ground, hits, '');
            })
            .catch(function (err) {
                console.warn('Ground elevation lookup failed:', err);
                if (!sideViewMode || !sideViewMarker || !sideViewMarker.getLatLng().equals(latlng)) return;
                renderSideView(latlng, null, hits,
                    'Ground elevation unavailable — AGL bounds shown relative to sea level.');
            });
    }

    return function handleClick(e) {
        if (!sideViewMode) return false;
        onSideViewClick(e);
        return true;
    };
}
