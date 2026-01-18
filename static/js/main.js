/**
 * EDA Application - Main JavaScript
 */

// Global state
window.EDA = {
    darkMode: false,
    datasets: [],
    selectedDataset: null,
    loading: false
};

// ============== INITIALIZATION ==============
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initTooltips();
    initSidebarAutoHide();
});

// ============== SIDEBAR AUTO-HIDE ==============
function initSidebarAutoHide() {
    const sidebar = document.getElementById('sidebar');
    const sidebarTrigger = document.getElementById('sidebarTrigger');
    const mainContent = document.querySelector('.main-content');

    if (!sidebar) return;

    // Hide sidebar when clicking on nav items (with page transition)
    const navItems = sidebar.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            // Add ripple effect
            item.classList.add('clicked');
            item.classList.add('transitioning');

            // Check if this is the same page (prevent transition for current page)
            if (item.classList.contains('active')) {
                setTimeout(() => {
                    item.classList.remove('clicked');
                    item.classList.remove('transitioning');
                }, 400);
                return;
            }

            // Trigger page transition
            e.preventDefault();
            const targetUrl = item.getAttribute('href');

            startPageTransition(targetUrl);
            hideSidebar();

            setTimeout(() => {
                item.classList.remove('clicked');
                item.classList.remove('transitioning');
            }, 400);
        });
    });

    // Show sidebar when mouse enters the trigger zone (right edge)
    if (sidebarTrigger) {
        sidebarTrigger.addEventListener('mouseenter', () => {
            showSidebar();
        });
    }

    // Also show sidebar when mouse enters the sidebar itself (for when partially visible)
    sidebar.addEventListener('mouseenter', () => {
        showSidebar();
    });

    // Hide sidebar when mouse leaves sidebar area completely
    sidebar.addEventListener('mouseleave', (e) => {
        // Only hide if not moving to the trigger zone
        const rect = sidebar.getBoundingClientRect();
        if (e.clientX > rect.right - 5) {
            // Mouse moved outside to the right, keep it visible
            return;
        }
        hideSidebar();
    });
}

function hideSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');

    if (sidebar) {
        sidebar.classList.add('hidden');
    }
    if (mainContent) {
        mainContent.classList.add('sidebar-hidden');
    }
}

function showSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');

    if (sidebar) {
        sidebar.classList.remove('hidden');
    }
    if (mainContent) {
        mainContent.classList.remove('sidebar-hidden');
    }
}

// Export sidebar functions
window.hideSidebar = hideSidebar;
window.showSidebar = showSidebar;

// ============== THEME MANAGEMENT ==============
function initTheme() {
    const savedTheme = localStorage.getItem('eda-theme') || 'light';
    setTheme(savedTheme);
}

function toggleTheme() {
    const newTheme = window.EDA.darkMode ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('eda-theme', newTheme);
}

function setTheme(theme) {
    window.EDA.darkMode = theme === 'dark';
    document.documentElement.setAttribute('data-theme', theme);

    // Update theme icons
    const lightIcon = document.getElementById('theme-icon-light');
    const darkIcon = document.getElementById('theme-icon-dark');
    const themeText = document.getElementById('theme-text');

    if (lightIcon && darkIcon) {
        if (theme === 'dark') {
            lightIcon.style.display = 'none';
            darkIcon.style.display = 'block';
            if (themeText) themeText.textContent = 'Light Mode';
        } else {
            lightIcon.style.display = 'block';
            darkIcon.style.display = 'none';
            if (themeText) themeText.textContent = 'Dark Mode';
        }
    }

    // Trigger chart theme updates
    if (typeof updateChartsTheme === 'function') {
        updateChartsTheme(theme === 'dark');
    }
}

// ============== LOADING OVERLAY ==============
function showLoading(message = 'Loading...') {
    window.EDA.loading = true;
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('active');
    }
}

function hideLoading() {
    window.EDA.loading = false;
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

// ============== TOAST NOTIFICATIONS ==============
function showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
            ${getToastIcon(type)}
        </svg>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

function getToastIcon(type) {
    switch (type) {
        case 'success':
            return '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>';
        case 'error':
            return '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>';
        case 'warning':
            return '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>';
        default:
            return '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>';
    }
}

// ============== API HELPERS ==============
async function apiGet(endpoint) {
    try {
        const response = await fetch(endpoint);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'API request failed');
        }
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message, 'error');
        throw error;
    }
}

async function apiPost(endpoint, body = {}) {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'API request failed');
        }
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message, 'error');
        throw error;
    }
}

async function apiDelete(endpoint) {
    try {
        const response = await fetch(endpoint, {
            method: 'DELETE'
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'API request failed');
        }
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message, 'error');
        throw error;
    }
}

async function apiUpload(endpoint, file) {
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Upload failed');
        }
        return data;
    } catch (error) {
        console.error('Upload Error:', error);
        showToast(error.message, 'error');
        throw error;
    }
}

// ============== FILE UPLOAD ==============
function initFileUpload(dropzoneId, callback) {
    const dropzone = document.getElementById(dropzoneId);
    if (!dropzone) return;

    // Click to upload
    dropzone.addEventListener('click', () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.csv,.xlsx,.xls';
        input.multiple = true;
        input.onchange = (e) => handleFiles(e.target.files, callback);
        input.click();
    });

    // Drag and drop
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files, callback);
    });
}

async function handleFiles(files, callback) {
    for (const file of files) {
        if (!file.name.match(/\.(csv|xlsx|xls)$/i)) {
            showToast(`Invalid file type: ${file.name}`, 'error');
            continue;
        }

        showLoading(`Uploading ${file.name}...`);
        try {
            const result = await apiUpload('/api/upload', file);
            showToast(`${file.name} uploaded successfully!`, 'success');
            if (callback) callback(result);
        } catch (error) {
            // Error already shown by apiUpload
        }
    }
    hideLoading();
}

// ============== TABLE RENDERING ==============
function renderDataTable(containerId, columns, data, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const maxRows = options.maxRows || 100;
    const displayData = data.slice(0, maxRows);

    let html = `
        <div class="table-container" style="max-height: ${options.maxHeight || '400px'}; overflow: auto;">
            <table class="data-table">
                <thead>
                    <tr>
                        ${columns.map(col => `<th>${col}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
    `;

    displayData.forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
            const value = row[col];
            html += `<td>${value !== null && value !== undefined ? value : '<span class="text-muted">null</span>'}</td>`;
        });
        html += '</tr>';
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    if (data.length > maxRows) {
        html += `<p class="text-muted mt-2" style="font-size: 0.875rem;">Showing ${maxRows} of ${data.length} rows</p>`;
    }

    container.innerHTML = html;
}

// ============== FORMATTING ==============
function formatNumber(num) {
    if (num === null || num === undefined) return 'N/A';
    if (typeof num === 'number') {
        return num.toLocaleString(undefined, { maximumFractionDigits: 2 });
    }
    return num;
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatPercentage(value) {
    if (value === null || value === undefined) return 'N/A';
    return value.toFixed(1) + '%';
}

// ============== UTILITIES ==============
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function initTooltips() {
    // Simple tooltip initialization if needed
}

// ============== DATASET MANAGEMENT ==============
async function loadDatasets() {
    try {
        const data = await apiGet('/api/datasets');
        window.EDA.datasets = data.datasets || [];
        return window.EDA.datasets;
    } catch (error) {
        return [];
    }
}

async function loadDatasetDetails(datasetId) {
    try {
        const data = await apiGet(`/api/datasets/${datasetId}`);
        return data;
    } catch (error) {
        return null;
    }
}

async function deleteDataset(datasetId) {
    try {
        await apiDelete(`/api/datasets/${datasetId}`);
        showToast('Dataset deleted', 'success');
        return true;
    } catch (error) {
        return false;
    }
}

// ============== SELECT RENDERING ==============
function populateSelect(selectId, options, valueKey = 'value', labelKey = 'label', placeholder = 'Select...') {
    const select = document.getElementById(selectId);
    if (!select) return;

    select.innerHTML = `<option value="">${placeholder}</option>`;
    options.forEach(opt => {
        const value = typeof opt === 'object' ? opt[valueKey] : opt;
        const label = typeof opt === 'object' ? opt[labelKey] : opt;
        select.innerHTML += `<option value="${value}">${label}</option>`;
    });
}

// ============== EXPORTS ==============
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.showToast = showToast;
window.apiGet = apiGet;
window.apiPost = apiPost;
window.apiDelete = apiDelete;
window.apiUpload = apiUpload;
window.initFileUpload = initFileUpload;
window.renderDataTable = renderDataTable;
window.formatNumber = formatNumber;
window.formatBytes = formatBytes;
window.formatPercentage = formatPercentage;
window.loadDatasets = loadDatasets;
window.loadDatasetDetails = loadDatasetDetails;
window.deleteDataset = deleteDataset;
window.populateSelect = populateSelect;
window.toggleTheme = toggleTheme;

// ============== PAGE TRANSITIONS ==============
function initPageTransitions() {
    // Create loading bar if it doesn't exist
    if (!document.querySelector('.page-loading-bar')) {
        const loadingBar = document.createElement('div');
        loadingBar.className = 'page-loading-bar';
        loadingBar.id = 'pageLoadingBar';
        document.body.appendChild(loadingBar);
    }

    // Create transition overlay if it doesn't exist
    if (!document.querySelector('.page-transition-overlay')) {
        const overlay = document.createElement('div');
        overlay.className = 'page-transition-overlay';
        overlay.id = 'pageTransitionOverlay';
        document.body.appendChild(overlay);
    }
}

function startPageTransition(targetUrl) {
    const mainContent = document.querySelector('.main-content');
    const loadingBar = document.getElementById('pageLoadingBar');
    const overlay = document.getElementById('pageTransitionOverlay');

    // Start loading bar animation
    if (loadingBar) {
        loadingBar.classList.add('active');
    }

    // Add exit animation to main content
    if (mainContent) {
        mainContent.classList.add('page-exit');
    }

    // Show overlay briefly
    if (overlay) {
        setTimeout(() => {
            overlay.classList.add('active');
        }, 200);
    }

    // Navigate to the new page after animation completes
    setTimeout(() => {
        window.location.href = targetUrl;
    }, 350);
}

// Initialize page transitions on load
document.addEventListener('DOMContentLoaded', () => {
    initPageTransitions();
});

// Export page transition functions
window.startPageTransition = startPageTransition;
window.initPageTransitions = initPageTransitions;
