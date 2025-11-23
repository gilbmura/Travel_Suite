// Admin Dashboard JavaScript

const ADMIN_API_BASE = '/admin';

// Tab Management
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
    
    // Load data for the tab
    loadTabData(tabName);
}

function loadTabData(tabName) {
    switch(tabName) {
        case 'districts':
            loadDistricts();
            break;
        case 'routes':
            loadRoutes();
            break;
        case 'buses':
            loadBuses();
            break;
        case 'schedules':
            loadSchedules();
            break;
        case 'bookings':
            loadBookings();
            break;
        case 'operators':
            loadOperators();
            break;
        case 'assignments':
            loadAssignments();
            break;
    }
}

// Modal Management
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
    if (modalId === 'routeModal') {
        // Load districts for both origin and destination
        loadDistrictsForSelect();
    }
    if (modalId === 'scheduleModal') {
        // Reset form for new schedule
        document.getElementById('scheduleId').value = '';
        document.getElementById('scheduleModalTitle').textContent = 'Add Schedule Recurrence';
        loadRoutesForSelect();
        loadBusesForSelect();
    }
    if (modalId === 'assignmentModal') {
        loadOperatorsForSelect();
        loadRoutesForSelect('assignmentRoute');
    }
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    const form = document.getElementById(modalId.replace('Modal', 'Form'));
    const idField = document.getElementById(modalId.replace('Modal', 'Id'));
    if (form) form.reset();
    if (idField) idField.value = '';
    
    // Reset schedule modal title
    if (modalId === 'scheduleModal') {
        const titleElement = document.getElementById('scheduleModalTitle');
        if (titleElement) {
            titleElement.textContent = 'Add Schedule Recurrence';
        }
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// Districts Management
async function loadDistricts() {
    try {
        const data = await TravelSuite.apiCall(`/admin/districts/`);
        const tbody = document.getElementById('districtsTableBody');
        tbody.innerHTML = data.map(d => `
            <tr>
                <td>${d.id}</td>
                <td>${d.name}</td>
                <td>${d.code || '-'}</td>
                <td>
                    <button class="btn btn-secondary btn-small" onclick="editDistrict(${d.id})">Edit</button>
                    <button class="btn btn-secondary btn-small" onclick="deleteDistrict(${d.id})">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        document.getElementById('districtsTableBody').innerHTML = 
            `<tr><td colspan="4" class="alert alert-error">Error: ${error.message}</td></tr>`;
    }
}

async function saveDistrict(e) {
    e.preventDefault();
    const formData = {
        name: document.getElementById('districtName').value,
        code: document.getElementById('districtCode').value || null,
    };
    
    const id = document.getElementById('districtId').value;
    const url = id ? `/admin/districts/${id}/` : `/admin/districts/`;
    const method = id ? 'PUT' : 'POST';
    
    try {
        await TravelSuite.apiCall(url, { method, body: formData });
        closeModal('districtModal');
        loadDistricts();
        TravelSuite.showAlert('District saved successfully', 'success');
    } catch (error) {
        TravelSuite.showAlert(`Error: ${error.message}`, 'error');
    }
}

async function editDistrict(id) {
    try {
        const data = await TravelSuite.apiCall(`/admin/districts/${id}/`);
        document.getElementById('districtId').value = data.id;
        document.getElementById('districtName').value = data.name;
        document.getElementById('districtCode').value = data.code || '';
        openModal('districtModal');
    } catch (error) {
        TravelSuite.showAlert(`Error: ${error.message}`, 'error');
    }
}

async function deleteDistrict(id) {
    if (!confirm('Are you sure you want to delete this district?')) return;
    
    try {
        await TravelSuite.apiCall(`/admin/districts/${id}/`, { method: 'DELETE' });
        loadDistricts();
        TravelSuite.showAlert('District deleted successfully', 'success');
    } catch (error) {
        TravelSuite.showAlert(`Error: ${error.message}`, 'error');
    }
}

// Routes Management
async function loadRoutes() {
    try {
        const data = await TravelSuite.apiCall(`/admin/routes/`);
        const tbody = document.getElementById('routesTableBody');
        tbody.innerHTML = data.map(r => `
            <tr>
                <td>${r.id}</td>
                <td>${r.name}</td>
                <td>${r.origin.name}</td>
                <td>${r.destination.name}</td>
                <td>${r.distance_km || '-'}</td>
                <td>${r.fare ? r.fare.toLocaleString() + ' RWF' : '5000 RWF'}</td>
                <td>${r.is_active ? 'Active' : 'Inactive'}</td>
                <td>
                    <button class="btn btn-secondary btn-small" onclick="editRoute(${r.id})">Edit</button>
                    <button class="btn btn-secondary btn-small" onclick="deleteRoute(${r.id})">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        document.getElementById('routesTableBody').innerHTML = 
            `<tr><td colspan="8" class="alert alert-error">Error: ${error.message}</td></tr>`;
    }
}

async function loadDistrictsForSelect(selectId = null) {
    try {
        // Use admin endpoint - apiCall will prepend /api, so this becomes /api/admin/districts/
        const districts = await TravelSuite.apiCall('/admin/districts/');
        const results = Array.isArray(districts) ? districts : (districts.results || []);
        const selects = selectId ? [document.getElementById(selectId)] : 
            [document.getElementById('routeOrigin'), document.getElementById('routeDestination')];
        
        selects.forEach(select => {
            if (select) {
                select.innerHTML = '<option value="">Select District</option>' +
                    results.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
            }
        });
    } catch (error) {
        console.error('Error loading districts:', error);
        // Show error in dropdown if it fails
        const selects = selectId ? [document.getElementById(selectId)] : 
            [document.getElementById('routeOrigin'), document.getElementById('routeDestination')];
        selects.forEach(select => {
            if (select) {
                select.innerHTML = '<option value="">Error loading districts</option>';
            }
        });
    }
}

async function saveRoute(e) {
    e.preventDefault();
    const formData = {
        name: document.getElementById('routeName').value,
        origin_id: parseInt(document.getElementById('routeOrigin').value),
        destination_id: parseInt(document.getElementById('routeDestination').value),
        distance_km: document.getElementById('routeDistance').value || null,
        estimated_duration_minutes: parseInt(document.getElementById('routeDuration').value) || null,
        fare: parseFloat(document.getElementById('routeFare').value) || 5000,
        is_active: document.getElementById('routeActive').checked,
    };
    
    const id = document.getElementById('routeId').value;
    const url = id ? `/admin/routes/${id}/` : `/admin/routes/`;
    const method = id ? 'PUT' : 'POST';
    
    try {
        await TravelSuite.apiCall(url, { method, body: formData });
        closeModal('routeModal');
        loadRoutes();
        TravelSuite.showAlert('Route saved successfully', 'success');
    } catch (error) {
        TravelSuite.showAlert(`Error: ${error.message}`, 'error');
    }
}

async function editRoute(id) {
    try {
        const data = await TravelSuite.apiCall(`/admin/routes/${id}/`);
        document.getElementById('routeId').value = data.id;
        document.getElementById('routeName').value = data.name;
        await loadDistrictsForSelect();
        document.getElementById('routeOrigin').value = data.origin.id;
        document.getElementById('routeDestination').value = data.destination.id;
        document.getElementById('routeDistance').value = data.distance_km || '';
        document.getElementById('routeDuration').value = data.estimated_duration_minutes || '';
        document.getElementById('routeFare').value = data.fare || 5000;
        document.getElementById('routeActive').checked = data.is_active;
        openModal('routeModal');
    } catch (error) {
        TravelSuite.showAlert(`Error: ${error.message}`, 'error');
    }
}

async function deleteRoute(id) {
    if (!confirm('Are you sure you want to delete this route?')) return;
    
    try {
        await TravelSuite.apiCall(`/admin/routes/${id}/`, { method: 'DELETE' });
        loadRoutes();
        TravelSuite.showAlert('Route deleted successfully', 'success');
    } catch (error) {
        TravelSuite.showAlert(`Error: ${error.message}`, 'error');
    }
}

// Buses Management
async function loadBuses() {
    try {
        const data = await TravelSuite.apiCall(`/admin/buses/`);
        const tbody = document.getElementById('busesTableBody');
        tbody.innerHTML = data.map(b => `
            <tr>
                <td>${b.id}</td>
                <td>${b.plate_number}</td>
                <td>${b.capacity}</td>
                <td>${b.company_name || '-'}</td>
                <td>${b.is_active ? 'Active' : 'Inactive'}</td>
                <td>
                    <button class="btn btn-secondary btn-small" onclick="editBus(${b.id})">Edit</button>
                    <button class="btn btn-secondary btn-small" onclick="deleteBus(${b.id})">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        document.getElementById('busesTableBody').innerHTML = 
            `<tr><td colspan="6" class="alert alert-error">Error: ${error.message}</td></tr>`;
    }
}

async function loadBusesForSelect() {
    try {
        const buses = await TravelSuite.apiCall(`/admin/buses/`);
        const select = document.getElementById('scheduleBus');
        select.innerHTML = '<option value="">Select Bus</option>' +
            buses.map(b => `<option value="${b.id}">${b.plate_number} (${b.capacity} seats)</option>`).join('');
    } catch (error) {
        console.error('Error loading buses:', error);
    }
}

async function saveBus(e) {
    e.preventDefault();
    const formData = {
        plate_number: document.getElementById('busPlate').value,
        capacity: parseInt(document.getElementById('busCapacity').value),
        company_name: document.getElementById('busCompany').value || null,
        is_active: document.getElementById('busActive').checked,
    };
    
    const id = document.getElementById('busId').value;
    const url = id ? `/admin/buses/${id}/` : `/admin/buses/`;
    const method = id ? 'PUT' : 'POST';
    
    try {
        await TravelSuite.apiCall(url, { method, body: formData });
        closeModal('busModal');
        loadBuses();
        TravelSuite.showAlert('Bus saved successfully', 'success');
    } catch (error) {
        TravelSuite.showAlert(`Error: ${error.message}`, 'error');
    }
}

async function editBus(id) {
    try {
        const data = await TravelSuite.apiCall(`/admin/buses/${id}/`);
        document.getElementById('busId').value = data.id;
        document.getElementById('busPlate').value = data.plate_number;
        document.getElementById('busCapacity').value = data.capacity;
        document.getElementById('busCompany').value = data.company_name || '';
        document.getElementById('busActive').checked = data.is_active;
        openModal('busModal');
    } catch (error) {
        TravelSuite.showAlert(`Error: ${error.message}`, 'error');
    }
}

async function deleteBus(id) {
    if (!confirm('Are you sure you want to delete this bus?')) return;
    
    try {
        await TravelSuite.apiCall(`/admin/buses/${id}/`, { method: 'DELETE' });
        loadBuses();
        TravelSuite.showAlert('Bus deleted successfully', 'success');
    } catch (error) {
        TravelSuite.showAlert(`Error: ${error.message}`, 'error');
    }
}

// Schedules Management
async function loadSchedules() {
    try {
        const data = await TravelSuite.apiCall(`/admin/schedule-recurrences/`);
        const tbody = document.getElementById('schedulesTableBody');
        tbody.innerHTML = data.map(s => `
            <tr>
                <td>${s.id}</td>
                <td>${s.route.name}</td>
                <td>${s.bus.plate_number}</td>
                <td>${s.recurrence_type}</td>
                <td>${s.departure_time}</td>
                <td>${s.arrival_time}</td>
                <td>${s.is_active ? 'Active' : 'Inactive'}</td>
                <td>
                    <button class="btn btn-secondary btn-small" onclick="editSchedule(${s.id})">Edit</button>
                    <button class="btn btn-danger btn-small" onclick="deleteSchedule(${s.id})" style="margin-left: 0.5rem;">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        document.getElementById('schedulesTableBody').innerHTML = 
            `<tr><td colspan="8" class="alert alert-error">Error: ${error.message}</td></tr>`;
    }
}

async function loadRoutesForSelect(selectId = 'scheduleRoute') {
    try {
        const routes = await TravelSuite.apiCall(`/admin/routes/`);
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">Select Route</option>' +
            routes.map(r => `<option value="${r.id}">${r.name}</option>`).join('');
    } catch (error) {
        console.error('Error loading routes:', error);
    }
}

async function editSchedule(id) {
    try {
        const schedule = await TravelSuite.apiCall(`/admin/schedule-recurrences/${id}/`);
        
        // Populate form
        document.getElementById('scheduleId').value = schedule.id;
        document.getElementById('scheduleRoute').value = schedule.route.id;
        document.getElementById('scheduleBus').value = schedule.bus.id;
        document.getElementById('scheduleType').value = schedule.recurrence_type;
        document.getElementById('scheduleDeparture').value = schedule.departure_time;
        document.getElementById('scheduleArrival').value = schedule.arrival_time;
        document.getElementById('scheduleActive').checked = schedule.is_active;
        
        // Update modal title
        document.getElementById('scheduleModalTitle').textContent = 'Edit Schedule Recurrence';
        
        // Load dropdowns if not already loaded
        await loadRoutesForSelect('scheduleRoute');
        await loadBusesForSelect('scheduleBus');
        
        // Set values again after dropdowns are loaded
        document.getElementById('scheduleRoute').value = schedule.route.id;
        document.getElementById('scheduleBus').value = schedule.bus.id;
        
        openModal('scheduleModal');
    } catch (error) {
        TravelSuite.showAlert(`Error loading schedule: ${error.message}`, 'error');
    }
}

async function deleteSchedule(id) {
    if (!confirm('Are you sure you want to delete this schedule recurrence? This will also delete all associated schedule occurrences.')) {
        return;
    }
    
    try {
        await TravelSuite.apiCall(`/admin/schedule-recurrences/${id}/`, { method: 'DELETE' });
        loadSchedules();
        TravelSuite.showAlert('Schedule deleted successfully', 'success');
    } catch (error) {
        TravelSuite.showAlert(`Error: ${error.message || 'Failed to delete schedule'}`, 'error');
    }
}

async function saveSchedule(e) {
    e.preventDefault();
    const scheduleId = document.getElementById('scheduleId').value;
    const formData = {
        route_id: parseInt(document.getElementById('scheduleRoute').value),
        bus_id: parseInt(document.getElementById('scheduleBus').value),
        recurrence_type: document.getElementById('scheduleType').value,
        departure_time: document.getElementById('scheduleDeparture').value,
        arrival_time: document.getElementById('scheduleArrival').value,
        is_active: document.getElementById('scheduleActive').checked,
    };
    
    try {
        if (scheduleId) {
            // Update existing schedule
            await TravelSuite.apiCall(`/admin/schedule-recurrences/${scheduleId}/`, { 
                method: 'PUT', 
                body: formData 
            });
            TravelSuite.showAlert('Schedule updated successfully', 'success');
        } else {
            // Create new schedule
            await TravelSuite.apiCall(`/admin/schedule-recurrences/`, { 
                method: 'POST', 
                body: formData 
            });
            TravelSuite.showAlert('Schedule created successfully', 'success');
        }
        closeModal('scheduleModal');
        loadSchedules();
    } catch (error) {
        TravelSuite.showAlert(`Error: ${error.message}`, 'error');
    }
}

// Bookings Management
async function loadBookings() {
    try {
        const data = await TravelSuite.apiCall(`/admin/bookings/`);
        const tbody = document.getElementById('bookingsTableBody');
        tbody.innerHTML = data.map(b => `
            <tr>
                <td>${b.id}</td>
                <td>${b.passenger_name}</td>
                <td>${b.phone_number}</td>
                <td>${b.schedule_occurrence.route.name}</td>
                <td>${b.schedule_occurrence.date} ${b.schedule_occurrence.departure_time}</td>
                <td>${b.payment_method}</td>
                <td>${b.status}</td>
                <td>${new Date(b.created_at).toLocaleString()}</td>
            </tr>
        `).join('');
    } catch (error) {
        document.getElementById('bookingsTableBody').innerHTML = 
            `<tr><td colspan="8" class="alert alert-error">Error: ${error.message}</td></tr>`;
    }
}

// Operators Management
async function loadOperators() {
    try {
        const data = await TravelSuite.apiCall(`/admin/operators/`);
        const tbody = document.getElementById('operatorsTableBody');
        tbody.innerHTML = data.map(o => `
            <tr>
                <td>${o.id}</td>
                <td>${o.username}</td>
                <td>${o.full_name}</td>
                <td>${o.phone_number}</td>
                <td>${o.email || '-'}</td>
                <td>${o.is_active ? 'Active' : 'Inactive'}</td>
                <td>
                    <button class="btn btn-secondary btn-small" onclick="deleteOperator(${o.id})">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        document.getElementById('operatorsTableBody').innerHTML = 
            `<tr><td colspan="7" class="alert alert-error">Error: ${error.message}</td></tr>`;
    }
}

async function loadOperatorsForSelect() {
    try {
        const operators = await TravelSuite.apiCall(`/admin/operators/`);
        const select = document.getElementById('assignmentOperator');
        select.innerHTML = '<option value="">Select Operator</option>' +
            operators.map(o => `<option value="${o.id}">${o.full_name} (${o.username})</option>`).join('');
    } catch (error) {
        console.error('Error loading operators:', error);
    }
}

async function saveOperator(e) {
    e.preventDefault();
    const formData = {
        username: document.getElementById('operatorUsername').value,
        password: document.getElementById('operatorPassword').value,
        full_name: document.getElementById('operatorFullName').value,
        phone_number: document.getElementById('operatorPhone').value,
        email: document.getElementById('operatorEmail').value || null,
    };
    
    try {
        await TravelSuite.apiCall(`/admin/operators/`, { 
            method: 'POST', 
            body: formData 
        });
        closeModal('operatorModal');
        loadOperators();
        TravelSuite.showAlert('Operator created successfully', 'success');
    } catch (error) {
        TravelSuite.showAlert(`Error: ${error.message}`, 'error');
    }
}

async function deleteOperator(id) {
    if (!confirm('Are you sure you want to delete this operator?')) return;
    
    try {
        const result = await TravelSuite.apiCall(`/admin/operators/${id}/`, { method: 'DELETE' });
        // 204 No Content returns null, which is expected
        loadOperators();
        TravelSuite.showAlert('Operator deleted successfully', 'success');
    } catch (error) {
        console.error('Delete operator error:', error);
        TravelSuite.showAlert(`Error: ${error.message || 'Failed to delete operator'}`, 'error');
    }
}

// Assignments Management
async function loadAssignments() {
    try {
        const data = await TravelSuite.apiCall(`/admin/operator-assignments/`);
        const tbody = document.getElementById('assignmentsTableBody');
        tbody.innerHTML = data.map(a => `
            <tr>
                <td>${a.id}</td>
                <td>${a.operator_name}</td>
                <td>${a.route_name}</td>
                <td>${a.is_active ? 'Active' : 'Inactive'}</td>
                <td>
                    <button class="btn btn-secondary btn-small" onclick="deleteAssignment(${a.id})">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        document.getElementById('assignmentsTableBody').innerHTML = 
            `<tr><td colspan="5" class="alert alert-error">Error: ${error.message}</td></tr>`;
    }
}

async function saveAssignment(e) {
    e.preventDefault();
    const formData = {
        operator_id: parseInt(document.getElementById('assignmentOperator').value),
        route_id: parseInt(document.getElementById('assignmentRoute').value),
    };
    
    try {
        await TravelSuite.apiCall(`/admin/operator-assignments/`, { 
            method: 'POST', 
            body: formData 
        });
        closeModal('assignmentModal');
        loadAssignments();
        TravelSuite.showAlert('Assignment created successfully', 'success');
    } catch (error) {
        TravelSuite.showAlert(`Error: ${error.message}`, 'error');
    }
}

async function deleteAssignment(id) {
    if (!confirm('Are you sure you want to delete this assignment?')) return;
    
    try {
        await TravelSuite.apiCall(`/admin/operator-assignments/${id}/`, { method: 'DELETE' });
        loadAssignments();
        TravelSuite.showAlert('Assignment deleted successfully', 'success');
    } catch (error) {
        TravelSuite.showAlert(`Error: ${error.message}`, 'error');
    }
}

// Form Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('districtForm').addEventListener('submit', saveDistrict);
    document.getElementById('routeForm').addEventListener('submit', saveRoute);
    document.getElementById('busForm').addEventListener('submit', saveBus);
    document.getElementById('scheduleForm').addEventListener('submit', saveSchedule);
    document.getElementById('operatorForm').addEventListener('submit', saveOperator);
    document.getElementById('assignmentForm').addEventListener('submit', saveAssignment);
    
    // Load initial data
    loadDistricts();
});

