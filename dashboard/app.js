// ============================================
// CONFIGURATION -- CHANGEZ CECI AVANT DEPLOIEMENT
// ============================================
const API_URL = 'https://votre-app-sur-render.com'; // <-- METTEZ VOTRE URL RENDER ICI

// ============================================
// AUTHENTICATION
// ============================================

function doLogin() {
    const username = document.getElementById('login-user').value;
    const password = document.getElementById('login-pass').value;
    
    const form = new FormData();
    form.append('username', username);
    form.append('password', password);
    
    fetch(`${API_URL}/token`, {method: 'POST', body: form})
        .then(r => {
            if (!r.ok) throw new Error('Invalid credentials');
            return r.json();
        })
        .then(data => {
            localStorage.setItem('ai_token', data.access_token);
            document.getElementById('auth-wall').style.display = 'none';
            loadDashboard();
        })
        .catch(() => {
            document.getElementById('login-error').style.display = 'block';
        });
}

function logout() {
    localStorage.removeItem('ai_token');
    location.reload();
}

// Auto-login check on page load
if (localStorage.getItem('ai_token')) {
    document.getElementById('auth-wall').style.display = 'none';
    loadDashboard();
}

// ============================================
// API HELPER (with Bearer token)
// ============================================

function apiFetch(path, opts = {}) {
    const token = localStorage.getItem('ai_token');
    if (!token) {
        document.getElementById('auth-wall').style.display = 'flex';
        return Promise.reject('No token');
    }
    
    opts.headers = {
        ...opts.headers,
        'Authorization': `Bearer ${token}`,
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
            localStorage.removeItem('ai_token');
            document.getElementById('auth-wall').style.display = 'flex';
        }
    }
}

async function loadCalls() {
    const tbody = document.getElementById('calls-body');
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#94a3b8;">Loading...</td></tr>';
    
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
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#94a3b8;">No calls found</td></tr>';
            return;
        }
        
        tbody.innerHTML = calls.map(call => {
            const appt = call.appointment || {};
            const apptText = appt.date 
                ? `${appt.date} ${appt.time} (${appt.service || 'general'})`
                : '-';
            
            const emergencyBadge = call.is_emergency 
                ? '<span style="background:#ef4444;color:#fff;padding:0.2rem 0.5rem;border-radius:0.25rem;font-size:0.75rem;">EMERGENCY</span>' 
                : '-';
            
            const statusColor = {
                'completed': '#22c55e',
                'no-answer': '#ef4444',
                'transferred': '#f59e0b'
            }[call.status] || '#94a3b8';
            
            return `
                <tr>
                    <td>${call.created_at ? new Date(call.created_at).toLocaleString() : '-'}</td>
                    <td>${call.phone || 'Unknown'}</td>
                    <td><span style="color:${statusColor};font-weight:600;">${call.status || 'unknown'}</span></td>
                    <td>${call.duration_seconds ? call.duration_seconds + 's' : '-'}</td>
                    <td>${apptText}</td>
                    <td>${emergencyBadge}</td>
                </tr>
            `;
        }).join('');
        
    } catch (e) {
        console.error('Calls error:', e);
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#ef4444;">Error loading data</td></tr>';
        if (e.message === 'Auth failed') {
            localStorage.removeItem('ai_token');
            document.getElementById('auth-wall').style.display = 'flex';
        }
    }
}

// Refresh every 30 seconds
setInterval(() => {
    if (localStorage.getItem('ai_token')) {
        loadDashboard();
    }
}, 30000);