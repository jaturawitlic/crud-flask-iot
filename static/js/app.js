// IoT Data Management System - JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // JSON textarea validation and formatting
    const jsonTextareas = document.querySelectorAll('textarea[name="sensor_data"]');
    jsonTextareas.forEach(function(textarea) {
        textarea.addEventListener('blur', function() {
            try {
                const jsonData = JSON.parse(this.value);
                // If valid JSON, format it nicely
                this.value = JSON.stringify(jsonData, null, 2);
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } catch (e) {
                // Invalid JSON
                if (this.value.trim() !== '' && this.value !== '{}') {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                    showToast('Invalid JSON format', 'error');
                }
            }
        });
    });

    // Form submission loading states
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
            }
        });
    });

    // Device ID suggestions based on existing devices
    const deviceIdInput = document.querySelector('#device_id');
    if (deviceIdInput) {
        // You could fetch existing device IDs via AJAX and provide autocomplete
        deviceIdInput.addEventListener('input', function() {
            // Basic validation for device ID format
            const value = this.value;
            const isValid = /^[a-zA-Z0-9_-]+$/.test(value);
            
            if (value && !isValid) {
                this.classList.add('is-invalid');
                showToast('Device ID should only contain letters, numbers, hyphens, and underscores', 'warning');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    }

    // Temperature and humidity validation
    const tempInput = document.querySelector('#temperature');
    const humidityInput = document.querySelector('#humidity');
    
    if (tempInput) {
        tempInput.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (!isNaN(value)) {
                // Color coding based on temperature ranges
                if (value > 35) {
                    this.style.color = '#dc3545'; // Hot - red
                } else if (value < 5) {
                    this.style.color = '#0dcaf0'; // Cold - cyan
                } else {
                    this.style.color = '#198754'; // Normal - green
                }
            }
        });
    }

    if (humidityInput) {
        humidityInput.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (!isNaN(value)) {
                // Validate humidity range
                if (value < 0 || value > 100) {
                    this.classList.add('is-invalid');
                    showToast('Humidity should be between 0% and 100%', 'warning');
                } else {
                    this.classList.remove('is-invalid');
                    // Color coding
                    if (value > 70) {
                        this.style.color = '#0d6efd'; // High - blue
                    } else if (value < 30) {
                        this.style.color = '#fd7e14'; // Low - orange
                    } else {
                        this.style.color = '#198754'; // Normal - green
                    }
                }
            }
        });
    }

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('form[action*="delete"] button[type="submit"]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this reading? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Auto-refresh device list every 30 seconds if on devices page
    if (window.location.pathname === '/devices') {
        setInterval(function() {
            // Only refresh if the page is visible
            if (!document.hidden) {
                window.location.reload();
            }
        }, 30000);
    }

    // Collapse sensor data sections with better UX
    const collapseElements = document.querySelectorAll('[data-bs-toggle="collapse"]');
    collapseElements.forEach(function(element) {
        element.addEventListener('click', function() {
            const target = document.querySelector(this.getAttribute('data-bs-target'));
            if (target) {
                const isExpanded = !target.classList.contains('show');
                this.textContent = isExpanded ? 'Hide Data' : 'View Data';
            }
        });
    });
});

// Utility function to show toast notifications
function showToast(message, type = 'info') {
    // Create toast element if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }

    const toastElement = document.createElement('div');
    toastElement.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'warning' ? 'warning' : 'primary'} border-0`;
    toastElement.setAttribute('role', 'alert');
    toastElement.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    toastContainer.appendChild(toastElement);
    const toast = new bootstrap.Toast(toastElement, { delay: 4000 });
    toast.show();

    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// API helper functions for AJAX operations
const API = {
    // Get device data
    getDeviceData: async function(deviceId) {
        try {
            const response = await fetch(`/api/data/${deviceId}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching device data:', error);
            showToast('Failed to fetch device data', 'error');
            return null;
        }
    },

    // Check API health
    checkHealth: async function() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            return data.status === 'healthy';
        } catch (error) {
            console.error('Health check failed:', error);
            return false;
        }
    }
};

// Export API for use in other scripts
window.IoTAPI = API;
