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
    loadCustomerStats();
    loadCustomerChart();
});

// ============================================
// LOAD CUSTOMER STATISTICS
// ============================================
async function loadCustomerStats() {
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/customer/stats`);
       
        if (!response.ok) throw new Error('Failed to fetch stats');
       
        const data = await response.json();
       
        document.getElementById('totalTrips').textContent = data.total_trips || 0;
        document.getElementById('avgFare').textContent = `$${(data.avg_fare || 0).toFixed(2)}`;
        document.getElementById('avgDistance').textContent = `${(data.avg_distance || 0).toFixed(2)} km`;
        document.getElementById('totalTips').textContent = `$${(data.total_tips || 0).toFixed(2)}`;
       
        hideLoading();
    } catch (error) {
        console.error('Failed to load customer stats:', error);
        hideLoading();
        // Load sample data
        document.getElementById('totalTrips').textContent = '45';
        document.getElementById('avgFare').textContent = '$12.60';
        document.getElementById('avgDistance').textContent = '5.2 km';
        document.getElementById('totalTips').textContent = '$191.25';
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
