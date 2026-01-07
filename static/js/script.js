/**
 * Body Measurement App - Frontend Logic
 */

// ===============================
// Premium Page Loading Animation
// ===============================

// Add smooth fade-in on page load
document.addEventListener('DOMContentLoaded', () => {
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    }, 100);
});

// Authentication
const auth = {
    token: localStorage.getItem('auth_token'),
    user: JSON.parse(localStorage.getItem('user') || 'null')
};

// Check authentication
function checkAuth() {
    if (!auth.token || !auth.user) {
        window.location.href = '/';
        return false;
    }
    return true;
}

// Logout function
function logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    window.location.href = '/';
}

// State management
const state = {
    frontImage: null,
    sideImage: null,
    frontImageData: null,
    sideImageData: null,
    measurements: null,
    landmarks: null,
    garmentCategories: [],
    currentCategory: null
};

// DOM elements
const elements = {
    frontDropzone: document.getElementById('frontDropzone'),
    sideDropzone: document.getElementById('sideDropzone'),
    frontInput: document.getElementById('frontInput'),
    sideInput: document.getElementById('sideInput'),
    frontPlaceholder: document.getElementById('frontPlaceholder'),
    sidePlaceholder: document.getElementById('sidePlaceholder'),
    frontPreview: document.getElementById('frontPreview'),
    sidePreview: document.getElementById('sidePreview'),
    frontRemove: document.getElementById('frontRemove'),
    sideRemove: document.getElementById('sideRemove'),
    genderSelect: document.getElementById('genderSelect'),
    heightInput: document.getElementById('heightInput'),
    unitsSelect: document.getElementById('unitsSelect'),
    calculateBtn: document.getElementById('calculateBtn'),
    btnText: document.getElementById('btnText'),
    loadingSpinner: document.getElementById('loadingSpinner'),
    resultsSection: document.getElementById('resultsSection'),
    errorMessage: document.getElementById('errorMessage'),
    errorText: document.getElementById('errorText'),
    exportBtn: document.getElementById('exportBtn'),
    sizeRecommendationSection: document.getElementById('sizeRecommendationSection'),
    garmentCategorySelect: document.getElementById('garmentCategorySelect'),
    sizeRecGrid: document.getElementById('sizeRecGrid'),
    historySection: document.getElementById('historySection'),
    historyList: document.getElementById('historyList'),
    refreshHistoryBtn: document.getElementById('refreshHistoryBtn')
};

// Initialize event listeners
function initEventListeners() {
    // Front image upload
    elements.frontDropzone.addEventListener('click', () => elements.frontInput.click());
    elements.frontInput.addEventListener('change', (e) => handleFileSelect(e, 'front'));
    elements.frontDropzone.addEventListener('dragover', handleDragOver);
    elements.frontDropzone.addEventListener('dragleave', handleDragLeave);
    elements.frontDropzone.addEventListener('drop', (e) => handleDrop(e, 'front'));
    elements.frontRemove.addEventListener('click', (e) => removeImage(e, 'front'));

    // Side image upload
    elements.sideDropzone.addEventListener('click', () => elements.sideInput.click());
    elements.sideInput.addEventListener('change', (e) => handleFileSelect(e, 'side'));
    elements.sideDropzone.addEventListener('dragover', handleDragOver);
    elements.sideDropzone.addEventListener('dragleave', handleDragLeave);
    elements.sideDropzone.addEventListener('drop', (e) => handleDrop(e, 'side'));
    elements.sideRemove.addEventListener('click', (e) => removeImage(e, 'side'));

    // Gender selector
    elements.genderSelect.addEventListener('change', () => {
        loadGarmentCategories();
        validateForm();
    });

    // Height input validation
    elements.heightInput.addEventListener('input', validateForm);

    // Calculate button
    elements.calculateBtn.addEventListener('click', calculateMeasurements);

    // Export button
    elements.exportBtn.addEventListener('click', exportResults);

    // Garment category selector
    elements.garmentCategorySelect.addEventListener('change', handleCategoryChange);

    // Load garment categories
    loadGarmentCategories();

    // Refresh history button
    elements.refreshHistoryBtn.addEventListener('click', fetchHistory);

    // Initial history fetch
    fetchHistory();

    // Navbar active state handling
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
}

// File handling
function handleFileSelect(event, type) {
    const file = event.target.files[0];
    if (file) {
        processFile(file, type);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
}

function handleDragLeave(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
}

function handleDrop(event, type) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');

    const file = event.dataTransfer.files[0];
    if (file) {
        processFile(file, type);
    }
}

function processFile(file, type) {
    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!validTypes.includes(file.type)) {
        showError('Please upload a JPEG or PNG image');
        return;
    }

    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        showError('Image size must be less than 10MB');
        return;
    }

    // Read file
    const reader = new FileReader();
    reader.onload = (e) => {
        const imageData = e.target.result;

        if (type === 'front') {
            state.frontImage = file;
            state.frontImageData = imageData;
            elements.frontPreview.src = imageData;
            elements.frontPreview.style.display = 'block';
            elements.frontPlaceholder.style.display = 'none';
            elements.frontRemove.style.display = 'flex';
        } else {
            state.sideImage = file;
            state.sideImageData = imageData;
            elements.sidePreview.src = imageData;
            elements.sidePreview.style.display = 'block';
            elements.sidePlaceholder.style.display = 'none';
            elements.sideRemove.style.display = 'flex';
        }

        validateForm();
        hideError();
    };

    reader.readAsDataURL(file);
}

function removeImage(event, type) {
    event.stopPropagation();

    if (type === 'front') {
        state.frontImage = null;
        state.frontImageData = null;
        elements.frontInput.value = '';
        elements.frontPreview.style.display = 'none';
        elements.frontPlaceholder.style.display = 'flex';
        elements.frontRemove.style.display = 'none';
    } else {
        state.sideImage = null;
        state.sideImageData = null;
        elements.sideInput.value = '';
        elements.sidePreview.style.display = 'none';
        elements.sidePlaceholder.style.display = 'flex';
        elements.sideRemove.style.display = 'none';
    }

    validateForm();
}

// Form validation
function validateForm() {
    const hasFrontImage = state.frontImageData !== null;
    const hasHeight = elements.heightInput.value && parseFloat(elements.heightInput.value) > 0;

    elements.calculateBtn.disabled = !(hasFrontImage && hasHeight);
}

// Calculate measurements
async function calculateMeasurements() {
    try {
        // Show loading state
        elements.calculateBtn.disabled = true;
        elements.btnText.textContent = 'Processing...';
        elements.loadingSpinner.style.display = 'inline-block';
        hideError();

        // Prepare request data
        const requestData = {
            front_image: state.frontImageData,
            side_image: state.sideImageData || null,
            calibration_height: parseFloat(elements.heightInput.value),
            units: elements.unitsSelect.value
        };

        // Send request to API with auth token
        const response = await fetch('/api/measurements/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${auth.token}`
            },
            body: JSON.stringify(requestData)
        });

        // Check for unauthorized
        if (response.status === 401) {
            logout();
            return;
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to calculate measurements');
        }

        const data = await response.json();

        // Check if successful
        if (!data.success) {
            throw new Error(data.message || 'Failed to detect pose in image');
        }

        // Store results
        state.measurements = data.measurements;
        state.landmarks = {
            front: data.front_landmarks,
            side: data.side_landmarks
        };

        // Display results
        displayResults(data);

        // Refresh history after calculation
        fetchHistory();

    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
    } finally {
        // Reset button state
        elements.calculateBtn.disabled = false;
        elements.btnText.textContent = 'Calculate Measurements';
        elements.loadingSpinner.style.display = 'none';
    }
}

// Display results
function displayResults(data) {
    const measurements = data.measurements;
    const units = measurements.units;

    // Create measurement cards
    const measurementsGrid = document.querySelector('.measurements-grid');
    measurementsGrid.innerHTML = '';

    const measurementLabels = {
        shoulder_width: 'Shoulder Width',
        chest: 'Chest',
        waist: 'Waist',
        hip: 'Hip',
        height: 'Height',
        inseam: 'Inseam'
    };

    // Calculate max value for progress bars
    const values = Object.values(measurements).filter(v => typeof v === 'number');
    const maxValue = Math.max(...values);

    // Create cards for each measurement
    Object.entries(measurementLabels).forEach(([key, label]) => {
        const value = measurements[key];
        if (value !== null && value !== undefined) {
            const card = createMeasurementCard(label, value, units, maxValue);
            measurementsGrid.appendChild(card);
        }
    });

    // Draw skeleton if landmarks available
    if (data.front_landmarks) {
        drawSkeleton(data.front_landmarks);
    }

    // Show results section
    elements.resultsSection.style.display = 'block';

    // Scroll to results
    elements.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Auto-load size recommendations if categories available
    if (state.garmentCategories.length > 0 && elements.garmentCategorySelect.value) {
        setTimeout(() => {
            getSizeRecommendations(elements.garmentCategorySelect.value);
        }, 500);
    } else if (state.garmentCategories.length > 0) {
        // Select first category and load recommendations
        elements.garmentCategorySelect.value = state.garmentCategories[0].key;
        setTimeout(() => {
            handleCategoryChange();
        }, 500);
    }
}

// Create measurement card
function createMeasurementCard(label, value, units, maxValue) {
    const card = document.createElement('div');
    card.className = 'measurement-card glass-card';

    const progressPercent = (value / maxValue) * 100;

    card.innerHTML = `
        <div class="measurement-label">${label}</div>
        <div class="measurement-value">${value.toFixed(1)} <small style="font-size: 0.5em; opacity: 0.7;">${units}</small></div>
        <div class="measurement-bar">
            <div class="measurement-progress" style="width: ${progressPercent}%"></div>
        </div>
    `;

    return card;
}

// Draw skeleton on canvas
function drawSkeleton(landmarks) {
    const canvas = document.getElementById('skeletonCanvas');
    const ctx = canvas.getContext('2d');

    // Set canvas size
    canvas.width = 600;
    canvas.height = 800;

    // Clear canvas
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Scale landmarks to canvas size
    const scale = Math.min(canvas.width, canvas.height);

    // Draw connections (simplified skeleton)
    const connections = [
        [11, 12], // shoulders
        [11, 13], [13, 15], // left arm
        [12, 14], [14, 16], // right arm
        [11, 23], [12, 24], // torso
        [23, 24], // hips
        [23, 25], [25, 27], // left leg
        [24, 26], [26, 28]  // right leg
    ];

    ctx.strokeStyle = 'rgba(139, 92, 246, 0.8)';
    ctx.lineWidth = 3;

    connections.forEach(([start, end]) => {
        if (landmarks[start] && landmarks[end]) {
            const startLm = landmarks[start];
            const endLm = landmarks[end];

            if (startLm.visibility > 0.5 && endLm.visibility > 0.5) {
                ctx.beginPath();
                ctx.moveTo(startLm.x * canvas.width, startLm.y * canvas.height);
                ctx.lineTo(endLm.x * canvas.width, endLm.y * canvas.height);
                ctx.stroke();
            }
        }
    });

    // Draw landmarks
    ctx.fillStyle = 'rgba(236, 72, 153, 0.9)';
    landmarks.forEach(lm => {
        if (lm.visibility > 0.5) {
            ctx.beginPath();
            ctx.arc(lm.x * canvas.width, lm.y * canvas.height, 5, 0, 2 * Math.PI);
            ctx.fill();
        }
    });
}

// Export results
function exportResults() {
    if (!state.measurements) return;

    const exportData = {
        timestamp: new Date().toISOString(),
        calibration_height: parseFloat(elements.heightInput.value),
        units: elements.unitsSelect.value,
        measurements: state.measurements
    };

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });

    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `body-measurements-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Error handling
function showError(message) {
    elements.errorText.textContent = message;
    elements.errorMessage.style.display = 'flex';
}

function hideError() {
    elements.errorMessage.style.display = 'none';
}

// History fetching
async function fetchHistory() {
    if (!auth.token) return;

    try {
        const response = await fetch('/api/measurements/history', {
            headers: {
                'Authorization': `Bearer ${auth.token}`
            }
        });

        if (response.status === 401) {
            logout();
            return;
        }

        const data = await response.json();
        if (data.success) {
            displayHistory(data.history);
        }
    } catch (error) {
        console.error('Error fetching history:', error);
    }
}

function displayHistory(history) {
    if (!elements.historyList) return;

    if (!history || history.length === 0) {
        elements.historyList.innerHTML = '<div class="history-empty">No measurements yet.</div>';
        elements.historySection.style.display = 'block';
        return;
    }

    elements.historySection.style.display = 'block';
    elements.historyList.innerHTML = '';

    history.forEach(item => {
        const date = new Date(item.created_at).toLocaleString();
        const m = item.measurements;
        const units = item.units === 'imperial' ? 'in' : 'cm';

        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <div class="history-info">
                <div class="history-date">${date}</div>
                <div class="history-summary">${item.gender.charAt(0).toUpperCase() + item.gender.slice(1)}, ${item.height} ${units}</div>
            </div>
            <div class="history-measurements">
                <span>Chest: ${m.chest.toFixed(1)}${units}</span>
                <span>Waist: ${m.waist.toFixed(1)}${units}</span>
                <span>Hip: ${m.hip.toFixed(1)}${units}</span>
            </div>
        `;
        
        // Make history item clickable to reload results
        historyItem.style.cursor = 'pointer';
        historyItem.onclick = () => {
            displayResults({
                measurements: {
                    ...m,
                    units: item.units === 'imperial' ? 'inches' : 'cm'
                },
                front_landmarks: null // Landmarks not stored in history for now to save space
            });
            window.scrollTo({ top: elements.resultsSection.offsetTop - 100, behavior: 'smooth' });
        };

        elements.historyList.appendChild(historyItem);
    });
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    if (!checkAuth()) {
        return;
    }
    
    // Display user info
    displayUserInfo();
    
    initEventListeners();
    validateForm();
});

// Display user info in header
function displayUserInfo() {
    const userInfo = document.getElementById('userInfo');
    if (userInfo && auth.user) {
        userInfo.textContent = auth.user.username || auth.user.email;
    }
}
