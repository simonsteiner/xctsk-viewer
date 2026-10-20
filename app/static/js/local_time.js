// For each .utc-time element, append the local time in user's browser time zone
function formatLocalTime(utcText) {
    // utcText is like "09:30 (UTC)"
    var match = utcText.match(/(\d{2}):(\d{2})/);
    if (!match) return '';
    var hour = parseInt(match[1], 10);
    var minute = parseInt(match[2], 10);
    // Create a Date object for today in UTC
    var now = new Date();
    var utcDate = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), hour, minute, 0));
    // Convert to local time string (HH:MM)
    var localHour = utcDate.getHours().toString().padStart(2, '0');
    var localMinute = utcDate.getMinutes().toString().padStart(2, '0');
    return localHour + ':' + localMinute;
}

document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    document.querySelectorAll('.utc-time').forEach(function(el) {
        var utcText = el.getAttribute('data-utc');
        var local = formatLocalTime(utcText);
        if (local) {
            var span = document.createElement('span');
            span.className = 'local-time';
            span.style.marginLeft = '0.5em';
            span.style.color = '#888';
            span.textContent = '(' + local + ' local)';
            el.appendChild(span);
        }
    });
});
