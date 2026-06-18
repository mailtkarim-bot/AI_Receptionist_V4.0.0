// ============================================
// CONFIGURATION — CHANGE BEFORE DEPLOYMENT
// ============================================
const API_URL = 'https://your-app.onrender.com'; // <-- SET YOUR RENDER URL HERE

// ============================================
// AUTHENTICATION (Cookie-based httpOnly)
// ============================================

async function doLogin() {
    const username = document.getElementById('login-user').value;
    const password = document.getElementById('login-pass').value;

    const form = new FormData();
    form.append('username', username);
    form.append('password', password);

    try {
        const r = await fetch(`${API_URL}/token`, {
            method: 'POST',
            body: form,
            credentials: 'include',
        });
        if (!r.ok) throw new Error('Invalid credentials');
        document.getElementById('auth-wall').style.display = 'none';
        loadDashboard();
    } catch (e) {
        document.getElementById('login-error').style.display = 'block';
    }
}

function logout() {
    fetch(`${API_URL}/logout`, {method: 'POST', credentials: 'include'})
        .finally(() => location.reload());
}

// Auto-refresh token before expiry (every 10 minutes)
setInterval(async () => {
    try {
        const r = await fetch(`${API_URL}/refresh`, {method: 'POST', credentials: 'include'});
        if (!r.ok) {
            // Refresh failed, force re-login
            document.getElementById('auth-wall').style.display = 'flex';
        }
    } catch (e) {
        console.error('Token refresh failed:', e);
    }
}, 10 * 60 * 1000); // 10 minutes

// Auto-login check on page load
(async function checkAuth() {
    try {
        const r = await fetch(`${API_URL}/calls?limit=1`, {credentials: 'include'});
        if (r.ok) {
            document.getElementById('auth-wall').style.display = 'none';
            loadDashboard();
        } else if (r.status === 401) {
            // Try refreshing token
            const refreshR = await fetch(`${API_URL}/refresh`, {method: 'POST', credentials: 'include'});
            if (refreshR.ok) {
                document.getElementById('auth-wall').style.display = 'none';
                loadDashboard();
            }
        }
    } catch (e) {
        // Stay on login wall
    }
})();

// ============================================
// API HELPER (Cookie-based)
// ============================================

function apiFetch(path, opts = {}) {
    opts.credentials = 'include';
    opts.headers = {
        ...opts.headers,
        'Content-Type': 'application/json'
    };
    return fetch(`${API_URL}${path}`, opts);
}

// ============================================
// DASHBOARD LOGIC
// ============================================

function loadDashboard() {
    loadStats();
    loadCalls();
}

async function loadStats() {
    try {
        const res = await apiFetch('/stats');
        if (!res.ok) throw new Error('Auth failed');
        const stats = await res.json();

        document.getElementById('stat-total').textContent = stats.total || 0;
        document.getElementById('stat-booked').textContent = stats.booked || 0;
        document.getElementById('stat-missed').textContent = stats.missed || 0;
        document.getElementById('stat-duration').textContent = (stats.avg_duration_seconds || 0) + 's';
        document.getElementById('last-updated').textContent = new Date().toLocaleString();
    } catch (e) {
        console.error('Stats error:', e);
        if (e.message === 'Auth failed') {
            document.getElementById('auth-wall').style.display = 'flex';
        }
    }
}

async function loadCalls() {
    const tbody = document.getElementById('calls-body');
    tbody.innerHTML = 'Loading...';

    try {
        const phoneFilter = document.getElementById('filter-phone').value;
        const statusFilter = document.getElementById('filter-status').value;

        let url = '/calls?limit=100';
        if (statusFilter) url += `&status=${encodeURIComponent(statusFilter)}`;
        if (phoneFilter) url += `&phone=${encodeURIComponent(phoneFilter)}`;

        const res = await apiFetch(url);
        if (!res.ok) throw new Error('Auth failed');
        const calls = await res.json();

        if (calls.length === 0) {
            tbody.innerHTML = 'No calls found';
            return;
        }

        tbody.innerHTML = calls.map(call => {
            const appt = call.appointment || {};
            const apptText = appt.date
                ? `${appt.date} ${appt.time} (${appt.service || 'general'})`
                : '-';

            const emergencyBadge = call.is_emergency ? 'EMERGENCY' : '-';

            const statusColor = {
                'completed': '#22c55e',
                'no-answer': '#ef4444',
                'transferred': '#f59e0b'
            }[call.status] || '#94a3b8';

            return `
                <tr>
                    <td>${call.created_at ? new Date(call.created_at).toLocaleString() : '-'}</td>
                    <td>${call.phone || 'Unknown'}</td>
                    <td style="color:${statusColor}">${call.status || 'unknown'}</td>
                    <td>${call.duration_seconds ? call.duration_seconds + 's' : '-'}</td>
                    <td>${apptText}</td>
                    <td>${emergencyBadge}</td>
                </tr>
            `;
        }).join('');

    } catch (e) {
        console.error('Calls error:', e);
        tbody.innerHTML = 'Error loading data';
        if (e.message === 'Auth failed') {
            document.getElementById('auth-wall').style.display = 'flex';
        }
    }
}

// Refresh every 30 seconds
setInterval(() => {
    if (document.getElementById('auth-wall').style.display === 'none') {
        loadDashboard();
    }
}, 30000);
