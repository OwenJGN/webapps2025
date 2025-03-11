// Main JavaScript file for PayApp

document.addEventListener('DOMContentLoaded', function() {
    // Only auto-dismiss notification alerts, not information alerts
    const temporaryAlerts = document.querySelectorAll('.alert.alert-success, .alert.alert-danger, .alert.alert-warning:not(.alert-permanent)');
    temporaryAlerts.forEach(function(alert) {
        setTimeout(function() {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {
                // Fallback if Bootstrap Alert isn't available
                if (alert && alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }
        }, 5000); // 5 seconds
    });

    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
});