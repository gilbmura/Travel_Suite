// ============================================
// CONFIGURATION
// ============================================
const API_BASE_URL = 'http://127.0.0.1:5000';

// State management
const state = {
    chart: null
};

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    if (!API_BASE_URL) {
        console.info('Customer analytics API disabled; skipping stat/chart loads.');
        return;
    }
    if (document.getElementById('totalTrips')) {
        loadCustomerStats();
    }
    if (document.getElementById('customerChart')) {
        loadCustomerChart();
    }
});

// ============================================
// LOAD CUSTOMER STATISTICS
// ============================================
async function loadCustomerStats() {
    try {
        const totalTripsEl = document.getElementById('totalTrips');
        if (!totalTripsEl) return;
        showLoading();
        const response = await fetch(`${API_BASE_URL}/customer/stats`);
       
        if (!response.ok) throw new Error('Failed to fetch stats');
       
        const data = await response.json();
       
        totalTripsEl.textContent = data.total_trips || 0;
        const avgFareEl = document.getElementById('avgFare');
        const avgDistanceEl = document.getElementById('avgDistance');
        const totalTipsEl = document.getElementById('totalTips');
        if (avgFareEl) avgFareEl.textContent = `$${(data.avg_fare || 0).toFixed(2)}`;
        if (avgDistanceEl) avgDistanceEl.textContent = `${(data.avg_distance || 0).toFixed(2)} km`;
        if (totalTipsEl) totalTipsEl.textContent = `$${(data.total_tips || 0).toFixed(2)}`;
       
        hideLoading();
    } catch (error) {
        console.error('Failed to load customer stats:', error);
        hideLoading();
        // Load sample data
        const totalTripsEl = document.getElementById('totalTrips');
        if (!totalTripsEl) return;
        totalTripsEl.textContent = '45';
        document.getElementById('avgFare')?.textContent = '$12.60';
        document.getElementById('avgDistance')?.textContent = '5.2 km';
        document.getElementById('totalTips')?.textContent = '$191.25';
    }
}

// ============================================
// LOAD CUSTOMER CHART
// ============================================
async function loadCustomerChart() {
    try {
        const response = await fetch(`${API_BASE_URL}/customer/trends`);
        const data = await response.json();
        createCustomerChart(data);
    } catch (error) {
        console.error('Failed to load chart:', error);
        createSampleChart();
    }
}

function createCustomerChart(data) {
    const ctx = document.getElementById('customerChart');
    if (!ctx) return;
   
    if (state.chart) {
        state.chart.destroy();
    }
   
    state.chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Trips',
                data: data.values || [5, 8, 12, 7, 10, 15],
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#f8fafc'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#f8fafc'
                    }
                }
            }
        }
    });
}

function createSampleChart() {
    createCustomerChart({
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        values: [5, 8, 12, 7, 10, 15]
    });
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
function showLoading() {
    document.getElementById('loadingOverlay')?.classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay')?.classList.add('hidden');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
   
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
   
    const icon = type === 'success' ? 'check-circle' :
                 type === 'error' ? 'exclamation-circle' :
                 type === 'warning' ? 'exclamation-triangle' : 'info-circle';
   
    toast.innerHTML = `
        <div class="toast-icon">
            <i class="fas fa-${icon}"></i>
        </div>
        <div class="toast-content">${message}</div>
        <div class="toast-close">
            <i class="fas fa-times"></i>
        </div>
    `;
   
    container.appendChild(toast);
   
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.remove();
    });
   
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// ============================================
// API HELPERS (used by admin pages)
// ============================================
const API_ROOT = 'http://127.0.0.1:8000/api';

async function apiFetch(endpoint, method = 'GET', body = null) {
    const token = localStorage.getItem('authToken');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_ROOT}${endpoint}`, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
    });

    if (res.status === 401) {
        // expired / unauthorized - force logout
        try { localStorage.removeItem('authToken'); } catch (e) {}
        window.location.href = '/Frontend/login-hub.html';
        throw new Error('Unauthorized');
    }

    if (res.status === 204) return null;

    const data = await res.json().catch(() => null);
    if (!res.ok) {
        const err = (data && data.detail) || (data && JSON.stringify(data)) || res.statusText;
        throw new Error(err);
    }
    return data;
}

// Fetch all users and return only operators (clients should filter further if needed)
async function getOperators() {
    const users = await apiFetch('/users/');
    if (!Array.isArray(users)) return [];
    return users.filter(u => u.is_operator === true);
}

// Fetch pending operators (operators waiting for approval)
async function getPendingOperators() {
    const pending = await apiFetch('/users/pending_operators/');
    if (!Array.isArray(pending)) return [];
    return pending.map(op => ({
        ...op.user,
        company_name: op.company_name,
        license_number: op.license_number,
        is_approved: op.is_approved,
        operator_profile_id: op.id
    }));
}

// Fetch approved operators (operators that have been approved)
async function getApprovedOperators() {
    const approved = await apiFetch('/users/approved_operators/');
    if (!Array.isArray(approved)) return [];
    return approved.map(op => ({
        ...op.user,
        company_name: op.company_name,
        license_number: op.license_number,
        is_approved: op.is_approved,
        operator_profile_id: op.id
    }));
}

// Approve or revoke operator access (uses the new approve_operator endpoint)
async function approveOperator(userId, approve) {
    const payload = { is_approved: !!approve };
    const updated = await apiFetch(`/users/${userId}/approve_operator/`, 'POST', payload);
    return updated;
}

// Toggle operator access by setting is_active flag. Returns updated user object.
async function toggleOperatorAccess(userId, allow) {
    // For operators, use the approve_operator endpoint instead
    // First check if user is an operator
    try {
        const user = await apiFetch(`/users/${userId}/`);
        if (user.is_operator) {
            // Use approve_operator endpoint for operators
            return await approveOperator(userId, allow);
        } else {
            // For non-operators, use set_active
            const payload = { is_active: !!allow };
            const updated = await apiFetch(`/users/${userId}/set_active/`, 'POST', payload);
            return updated;
        }
    } catch (error) {
        console.error('Error toggling access:', error);
        throw error;
    }
}

// Admin dashboard aggregates
async function getAdminDashboardStats() {
    return apiFetch('/bookings/admin/dashboard/');
}

// Operator scoped data helpers
async function getOperatorRoutes() {
    return apiFetch('/routes/operator/');
}

async function getOperatorVehicles() {
    return apiFetch('/vehicles/operator/');
}

async function getOperatorBookings() {
    return apiFetch('/bookings/operator/');
}

async function operatorCancelBooking(id) {
    return apiFetch(`/bookings/${id}/operator-cancel/`, 'POST');
}

// Public search + booking helpers (no auth required)
async function getRouteFilters() {
    // Public endpoint, no auth token needed
    const res = await fetch(`${API_ROOT}/routes/filters/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error('Failed to load route filters');
    return res.json();
}

async function searchVehicles(params) {
    const query = new URLSearchParams(params).toString();
    return apiFetch(`/vehicles/search/?${query}`, 'GET', null);
}

async function createPublicBooking(payload) {
    return apiFetch('/bookings/public/', 'POST', payload);
}

async function clientCancelBooking(bookingId) {
    return apiFetch('/bookings/client-cancel/', 'POST', { booking_id: bookingId });
}

async function getBookingStatus(bookingId) {
    const query = new URLSearchParams({ booking_id: bookingId }).toString();
    return apiFetch(`/bookings/client-status/?${query}`);
}

// expose helpers to global scope for inline pages that don't import modules
window.apiFetch = apiFetch;
window.getOperators = getOperators;
window.getPendingOperators = getPendingOperators;
window.getApprovedOperators = getApprovedOperators;
window.approveOperator = approveOperator;
window.toggleOperatorAccess = toggleOperatorAccess;
window.getAdminDashboardStats = getAdminDashboardStats;
window.getOperatorRoutes = getOperatorRoutes;
window.getOperatorVehicles = getOperatorVehicles;
window.getOperatorBookings = getOperatorBookings;
window.operatorCancelBooking = operatorCancelBooking;
window.getRouteFilters = getRouteFilters;
window.searchVehicles = searchVehicles;
window.createPublicBooking = createPublicBooking;
window.clientCancelBooking = clientCancelBooking;
window.getBookingStatus = getBookingStatus;
