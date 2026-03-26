// Custom Admin JavaScript for Municipal Helpdesk

document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh functionality
    let autoRefreshInterval;
    let isAutoRefreshEnabled = false;
    
    // Add auto-refresh toggle to admin interface
    addAutoRefreshToggle();
    
    // Add real-time status indicators
    addStatusIndicators();
    
    // Add keyboard shortcuts
    addKeyboardShortcuts();
    
    // Add bulk actions
    addBulkActions();
    
    // Add notification system
    addNotificationSystem();
});

function addAutoRefreshToggle() {
    const toolbar = document.querySelector('.object-tools');
    if (toolbar) {
        const toggleBtn = document.createElement('button');
        toggleBtn.innerHTML = '<i class="fas fa-sync"></i> Auto-Refresh: OFF';
        toggleBtn.className = 'button';
        toggleBtn.style.marginLeft = '10px';
        toggleBtn.onclick = toggleAutoRefresh;
        toolbar.appendChild(toggleBtn);
    }
}

function toggleAutoRefresh() {
    const btn = event.target;
    isAutoRefreshEnabled = !isAutoRefreshEnabled;
    
    if (isAutoRefreshEnabled) {
        btn.innerHTML = '<i class="fas fa-sync"></i> Auto-Refresh: ON';
        btn.style.background = 'var(--success-color)';
        startAutoRefresh();
    } else {
        btn.innerHTML = '<i class="fas fa-sync"></i> Auto-Refresh: OFF';
        btn.style.background = 'var(--primary-color)';
        stopAutoRefresh();
    }
}

function startAutoRefresh() {
    autoRefreshInterval = setInterval(function() {
        // Refresh the current page
        window.location.reload();
    }, 30000); // Refresh every 30 seconds
    
    showNotification('Auto-refresh enabled', 'Page will refresh every 30 seconds', 'info');
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
    showNotification('Auto-refresh disabled', 'Manual refresh only', 'warning');
}

function addStatusIndicators() {
    // Add real-time status indicators to issue rows
    const rows = document.querySelectorAll('#result_list tbody tr');
    
    rows.forEach(row => {
        const statusCell = row.querySelector('td.field-status');
        if (statusCell) {
            const status = statusCell.textContent.trim();
            const indicator = document.createElement('span');
            indicator.className = `status-indicator status-${status.toLowerCase().replace(' ', '-')}`;
            indicator.innerHTML = getStatusIcon(status);
            statusCell.appendChild(indicator);
        }
    });
}

function getStatusIcon(status) {
    const icons = {
        'submitted': '<i class="fas fa-clock" title="Waiting for review"></i>',
        'in_progress': '<i class="fas fa-spinner fa-spin" title="Currently being worked on"></i>',
        'resolved': '<i class="fas fa-check-circle" title="Completed"></i>'
    };
    return icons[status] || '<i class="fas fa-question-circle" title="Unknown status"></i>';
}

function addKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + R: Refresh
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            window.location.reload();
        }
        
        // Ctrl/Cmd + A: Assign all
        if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
            e.preventDefault();
            assignAllIssues();
        }
        
        // Ctrl/Cmd + S: Save/Update
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            saveAllChanges();
        }
    });
}

function addBulkActions() {
    const changelistTable = document.querySelector('#result_list');
    if (changelistTable) {
        // Add bulk action buttons
        const toolbar = document.querySelector('.object-tools');
        if (toolbar) {
            const bulkActions = document.createElement('div');
            bulkActions.innerHTML = `
                <button class="button" onclick="bulkAssign()">
                    <i class="fas fa-user-plus"></i> Bulk Assign
                </button>
                <button class="button" onclick="bulkResolve()">
                    <i class="fas fa-check"></i> Bulk Resolve
                </button>
                <button class="button" onclick="bulkNotify()">
                    <i class="fas fa-envelope"></i> Bulk Notify
                </button>
            `;
            bulkActions.style.marginTop = '10px';
            toolbar.appendChild(bulkActions);
        }
    }
}

function assignAllIssues() {
    const checkboxes = document.querySelectorAll('input[name="_selected_action"]');
    const selectedIds = [];
    
    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            selectedIds.push(checkbox.value);
        }
    });
    
    if (selectedIds.length === 0) {
        showNotification('No Selection', 'Please select issues to assign', 'warning');
        return;
    }
    
    // Send AJAX request to bulk assign
    bulkUpdateIssues(selectedIds, 'in_progress', 'Issues assigned and marked as in progress');
}

function bulkResolveIssues() {
    const checkboxes = document.querySelectorAll('input[name="_selected_action"]');
    const selectedIds = [];
    
    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            selectedIds.push(checkbox.value);
        }
    });
    
    if (selectedIds.length === 0) {
        showNotification('No Selection', 'Please select issues to resolve', 'warning');
        return;
    }
    
    // Send AJAX request to bulk resolve
    bulkUpdateIssues(selectedIds, 'resolved', 'Issues marked as resolved');
}

function bulkNotifyUsers() {
    const checkboxes = document.querySelectorAll('input[name="_selected_action"]');
    const selectedIds = [];
    
    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            selectedIds.push(checkbox.value);
        }
    });
    
    if (selectedIds.length === 0) {
        showNotification('No Selection', 'Please select issues to notify users', 'warning');
        return;
    }
    
    showNotification('Bulk Notification', `Sending notifications for ${selectedIds.length} issues...`, 'info');
}

function bulkUpdateIssues(issueIds, status, message) {
    // This would normally be an AJAX call to the server
    // For demo purposes, we'll just show the message
    showNotification('Bulk Update', message, 'success');
    
    // Uncheck all checkboxes
    const checkboxes = document.querySelectorAll('input[name="_selected_action"]');
    checkboxes.forEach(checkbox => checkbox.checked = false);
    
    // Refresh the page after a short delay
    setTimeout(() => {
        window.location.reload();
    }, 2000);
}

function saveAllChanges() {
    const form = document.querySelector('#changelist-form');
    if (form) {
        // Add loading state
        const submitBtn = form.querySelector('input[type="submit"]');
        if (submitBtn) {
            submitBtn.value = 'Saving...';
            submitBtn.disabled = true;
            
            // Simulate save
            setTimeout(() => {
                submitBtn.value = 'Save';
                submitBtn.disabled = false;
                showNotification('Saved', 'All changes have been saved', 'success');
            }, 1000);
        }
    }
}

function addNotificationSystem() {
    // Create notification container if it doesn't exist
    if (!document.getElementById('admin-notifications')) {
        const notificationContainer = document.createElement('div');
        notificationContainer.id = 'admin-notifications';
        notificationContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 400px;
        `;
        document.body.appendChild(notificationContainer);
    }
}

function showNotification(title, message, type = 'info') {
    const container = document.getElementById('admin-notifications');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `admin-notification ${type}`;
    notification.innerHTML = `
        <div class="notification-header">
            <strong>${title}</strong>
            <button onclick="this.parentElement.remove()" class="notification-close">&times;</button>
        </div>
        <div class="notification-body">
            ${message}
        </div>
    `;
    
    notification.style.cssText = `
        background: white;
        border-left: 4px solid ${type === 'success' ? 'var(--success-color)' : type === 'warning' ? 'var(--warning-color)' : 'var(--info-color)'};
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        animation: slideInRight 0.3s ease-out;
    `;
    
    container.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Add CSS for notifications
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    .admin-notification {
        animation: slideInRight 0.3s ease-out;
    }
    
    .notification-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        font-weight: 600;
    }
    
    .notification-close {
        background: none;
        border: none;
        font-size: 16px;
        cursor: pointer;
        color: var(--secondary-color);
        padding: 0;
        margin: 0;
    }
    
    .notification-close:hover {
        color: var(--error-color);
    }
    
    .notification-body {
        line-height: 1.4;
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .status-indicator {
        margin-left: 8px;
        padding: 2px 6px;
        border-radius: 10px;
        font-size: 10px;
    }
    
    .status-submitted {
        background: var(--warning-color);
        color: white;
    }
    
    .status-in_progress {
        background: var(--info-color);
        color: white;
    }
    
    .status-resolved {
        background: var(--success-color);
        color: white;
    }
`;

document.head.appendChild(notificationStyles);
