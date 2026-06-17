/* AI Receptionist Dashboard — Frontend Logic */

const API_URL = "https://votre-backend.onrender.com"; // CHANGE THIS

// DOM Elements
const els = {
    total: document.getElementById("total"),
    booked: document.getElementById("booked"),
    missed: document.getElementById("missed"),
    avgDuration: document.getElementById("avg-duration"),
    searchPhone: document.getElementById("search-phone"),
    filterStatus: document.getElementById("filter-status"),
    tbody: document.querySelector("#calls-table tbody"),
    lastUpdate: document.getElementById("last-update"),
};

/**
 * Load calls from backend API
 */
async function loadCalls() {
    try {
        const res = await fetch(`${API_URL}/calls`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const calls = await res.json();
        renderCalls(calls);
        updateLastUpdate();
    } catch (e) {
        console.error("[Dashboard] Error loading calls:", e);
        els.tbody.innerHTML = `
            <tr><td colspan="6" class="error">
                <strong>Connection Error</strong><br>
                Unable to reach backend. Check API_URL in app.js.<br>
                <small>${e.message}</small>
            </td></tr>`;
    }
}

/**
 * Load statistics from /stats endpoint
 */
async function loadStats() {
    try {
        const res = await fetch(`${API_URL}/stats`);
        if (!res.ok) return;
        const stats = await res.json();
        els.total.textContent = stats.total || 0;
        els.booked.textContent = stats.booked || 0;
        els.missed.textContent = stats.missed || 0;
        els.avgDuration.textContent = stats.avg_duration_seconds
            ? `${stats.avg_duration_seconds}s`
            : "0s";
    } catch (e) {
        console.error("[Dashboard] Error loading stats:", e);
    }
}

/**
 * Render calls table with filters
 */
function renderCalls(calls) {
    const search = els.searchPhone.value.trim().toLowerCase();
    const statusFilter = els.filterStatus.value;

    const filtered = calls.filter(c => {
        const matchPhone = !search || (c.phone || "").toLowerCase().includes(search);
        const matchStatus = statusFilter === "all" || c.status === statusFilter;
        return matchPhone && matchStatus;
    }).reverse();

    // Update stats from filtered data (fallback if /stats fails)
    if (!els.total.textContent || els.total.textContent === "0") {
        els.total.textContent = calls.length;
        els.booked.textContent = calls.filter(c => c.appointment).length;
        els.missed.textContent = calls.filter(c => c.status === "no-answer").length;
        const durations = calls.filter(c => c.duration_seconds).map(c => c.duration_seconds);
        const avg = durations.length ? Math.round(durations.reduce((a,b) => a+b, 0) / durations.length) : 0;
        els.avgDuration.textContent = `${avg}s`;
    }

    // Render table
    if (!filtered.length) {
        els.tbody.innerHTML = `<tr><td colspan="6" class="empty">No calls found</td></tr>`;
        return;
    }

    els.tbody.innerHTML = filtered.map(c => {
        const time = c.timestamp ? new Date(c.timestamp).toLocaleTimeString() : "—";
        const phone = c.phone || "Anonymous";
        const statusClass = c.status === "completed" ? "status-ok" : c.status === "no-answer" ? "status-ko" : "status-warn";
        const appt = c.appointment
            ? `✅ ${c.appointment.date} ${c.appointment.time}`
            : "—";
        const transcript = c.transcript
            ? `<details><summary>View</summary><p>${escapeHtml(c.transcript.substring(0, 200))}...</p></details>`
            : "—";

        return `<tr>
            <td>${time}</td>
            <td>${escapeHtml(phone)}</td>
            <td><span class="badge ${statusClass}">${c.status || "unknown"}</span></td>
            <td>${c.duration_seconds || "—"}s</td>
            <td>${appt}</td>
            <td>${transcript}</td>
        </tr>`;
    }).join("");
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Update last refresh timestamp
 */
function updateLastUpdate() {
    if (els.lastUpdate) {
        els.lastUpdate.textContent = `Last update: ${new Date().toLocaleTimeString()}`;
    }
}

// Event Listeners
els.searchPhone.addEventListener("input", loadCalls);
els.filterStatus.addEventListener("change", loadCalls);

// Auto-refresh every 30 seconds
loadCalls();
loadStats();
setInterval(() => {
    loadCalls();
    loadStats();
}, 30000);

console.log("[AI Receptionist Dashboard] Loaded. API:", API_URL);
