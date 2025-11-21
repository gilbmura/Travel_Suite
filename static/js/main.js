// Travel Suite - Main JavaScript

const API_BASE_URL = '/api';

// Utility Functions
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const csrftoken = getCookie('csrftoken');
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
  };
  
  // Add CSRF token for POST/PUT/DELETE requests
  if (csrftoken && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method?.toUpperCase())) {
    defaultOptions.headers['X-CSRFToken'] = csrftoken;
  }
  
  const config = { ...defaultOptions, ...options };
  
  // Merge headers properly
  if (options.headers) {
    config.headers = { ...defaultOptions.headers, ...options.headers };
    if (csrftoken && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method?.toUpperCase())) {
      config.headers['X-CSRFToken'] = csrftoken;
    }
  }
  
  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body);
  }
  
  try {
    const response = await fetch(url, config);
    
    // Handle 204 No Content (empty response) - return immediately, don't try to read body
    if (response.status === 204) {
      return null;
    }
    
    // Check if response has content before trying to parse
    let data = null;
    
    // Check content length first to avoid reading empty responses
    const contentLength = response.headers.get('content-length');
    const contentType = response.headers.get('content-type');
    
    // Only try to parse if we have content
    if (contentType && contentType.includes('application/json') && 
        (contentLength === null || parseInt(contentLength) > 0)) {
      try {
        const text = await response.text();
        if (text && text.trim().length > 0) {
          data = JSON.parse(text);
        }
      } catch (parseError) {
        // If parsing fails and it's not a 204, log it
        if (response.status !== 204) {
          console.warn('Failed to parse JSON response:', parseError);
        }
        // For empty responses, data remains null which is fine
      }
    }
    
    if (!response.ok) {
      throw new Error(data?.error || data?.message || `Request failed with status ${response.status}`);
    }
    
    return data;
  } catch (error) {
    // Handle JSON parse errors for empty responses (might be from cached code)
    if (error.message && (
      error.message.includes('JSON') && error.message.includes('Unexpected end') ||
      error.message.includes('Unexpected end of JSON input')
    )) {
      // This is likely a 204 response, return null
      return null;
    }
    console.error('API Error:', error);
    throw error;
  }
}

function showAlert(message, type = 'info') {
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type}`;
  alertDiv.textContent = message;
  
  const container = document.querySelector('.container') || document.body;
  container.insertBefore(alertDiv, container.firstChild);
  
  setTimeout(() => {
    alertDiv.remove();
  }, 5000);
}

function showLoading(element) {
  element.innerHTML = '<div class="spinner"></div>';
}

function formatTime(minutes) {
  if (minutes === null || minutes === undefined) return 'N/A';
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
}

// Routes Functions
async function loadDistricts() {
  try {
    const data = await apiCall('/districts/');
    return data.results || data;
  } catch (error) {
    console.error('Failed to load districts:', error);
    return [];
  }
}

async function searchRoutes(fromLocation) {
  try {
    const params = fromLocation ? `?from=${encodeURIComponent(fromLocation)}` : '';
    const data = await apiCall(`/routes/${params}`);
    return data.results || data;
  } catch (error) {
    console.error('Failed to search routes:', error);
    throw error;
  }
}

// Schedules Functions
async function loadSchedules(routeId, date = null) {
  try {
    let params = `?route_id=${routeId}`;
    if (date) {
      params += `&date=${date}`;
    }
    const data = await apiCall(`/schedules/${params}`);
    return data.results || data;
  } catch (error) {
    console.error('Failed to load schedules:', error);
    throw error;
  }
}

function renderScheduleCard(schedule) {
  const seatsClass = schedule.remaining_seats <= 5 ? 'low' : 'available';
  const timeToDeparture = schedule.time_to_departure 
    ? formatTime(schedule.time_to_departure) 
    : 'Departed';
  
  // Check if schedule has departed or is not bookable
  const isDeparted = !schedule.time_to_departure || schedule.status === 'departed';
  const canBook = !isDeparted && schedule.remaining_seats > 0 && schedule.status === 'scheduled';
  
  // Format date for display
  const scheduleDate = new Date(schedule.date);
  const dateStr = scheduleDate.toLocaleDateString('en-US', { 
    weekday: 'short', 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  });
  const isToday = schedule.date === new Date().toISOString().split('T')[0];
  const isFuture = schedule.date > new Date().toISOString().split('T')[0];
  
  // Determine button text and state
  let buttonHtml = '';
  if (canBook) {
    buttonHtml = `<button class="btn btn-primary" onclick="selectSchedule(${schedule.id}, '${schedule.date}')">Book Now</button>`;
  } else if (isDeparted) {
    buttonHtml = `<button class="btn btn-secondary" disabled style="opacity: 0.6; cursor: not-allowed;">Departed</button>`;
  } else if (schedule.remaining_seats <= 0) {
    buttonHtml = `<button class="btn btn-secondary" disabled style="opacity: 0.6; cursor: not-allowed;">Sold Out</button>`;
  } else {
    buttonHtml = `<button class="btn btn-secondary" disabled style="opacity: 0.6; cursor: not-allowed;">Not Available</button>`;
  }
  
  return `
    <div class="card schedule-card" data-schedule-id="${schedule.id}">
      <div class="schedule-time">${schedule.departure_time}</div>
      <p style="font-size: 1.1rem; font-weight: bold; color: var(--color-primary); margin: 0.5rem 0;">
        📅 ${dateStr} ${isToday ? '(Today)' : isFuture ? '(Future)' : ''}
      </p>
      <p><strong>Route:</strong> ${schedule.route.name}</p>
      <p><strong>Arrival:</strong> ${schedule.arrival_time}</p>
      <p><strong>Time to Departure:</strong> ${timeToDeparture}</p>
      <span class="schedule-seats ${seatsClass}">
        ${schedule.remaining_seats} seats available
      </span>
      <div style="margin-top: 1rem;">
        ${buttonHtml}
      </div>
    </div>
  `;
}

function selectSchedule(scheduleId, scheduleDate = null) {
  localStorage.setItem('selectedScheduleId', scheduleId);
  if (scheduleDate) {
    localStorage.setItem('selectedScheduleDate', scheduleDate);
  }
  window.location.href = `/booking/?schedule_id=${scheduleId}`;
}

// Booking Functions
async function createBooking(bookingData) {
  try {
    const data = await apiCall('/bookings/', {
      method: 'POST',
      body: bookingData,
    });
    return data;
  } catch (error) {
    console.error('Failed to create booking:', error);
    throw error;
  }
}

async function cancelBooking(bookingId) {
  try {
    const data = await apiCall(`/bookings/${bookingId}/cancel/`, {
      method: 'POST',
    });
    return data;
  } catch (error) {
    console.error('Failed to cancel booking:', error);
    throw error;
  }
}

async function getBookingStatus(bookingId) {
  try {
    const data = await apiCall(`/bookings/${bookingId}/status/`);
    return data;
  } catch (error) {
    console.error('Failed to get booking status:', error);
    throw error;
  }
}

// Auto-refresh for schedules
let scheduleRefreshInterval = null;

function startScheduleRefresh(routeId, date, containerId) {
  if (scheduleRefreshInterval) {
    clearInterval(scheduleRefreshInterval);
  }
  
  scheduleRefreshInterval = setInterval(async () => {
    try {
      const schedules = await loadSchedules(routeId, date);
      const container = document.getElementById(containerId);
      if (container) {
        container.innerHTML = schedules.map(renderScheduleCard).join('');
      }
    } catch (error) {
      console.error('Failed to refresh schedules:', error);
    }
  }, 30000); // Refresh every 30 seconds
}

function stopScheduleRefresh() {
  if (scheduleRefreshInterval) {
    clearInterval(scheduleRefreshInterval);
    scheduleRefreshInterval = null;
  }
}

// Export for use in other scripts
window.TravelSuite = {
  apiCall,
  showAlert,
  showLoading,
  formatTime,
  loadDistricts,
  searchRoutes,
  loadSchedules,
  renderScheduleCard,
  selectSchedule,
  createBooking,
  cancelBooking,
  getBookingStatus,
  startScheduleRefresh,
  stopScheduleRefresh,
};

