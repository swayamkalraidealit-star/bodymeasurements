/**
 * Size Recommendations Extension for Body Measurement App
 */

// Load garment categories from API
async function loadGarmentCategories() {
    try {
        console.log('Loading garment categories...');
        const response = await fetch('/api/size-recommendations/categories');
        if (!response.ok) {
            console.error('Failed to load garment categories');
            return;
        }
        
        const allCategories = await response.json();
        console.log('Loaded categories:', allCategories);
        
        // Filter categories based on selected gender
        const selectedGender = elements.genderSelect.value;
        const categories = allCategories.filter(category => {
            if (selectedGender === 'male') {
                return category.key.startsWith('MENS_');
            } else if (selectedGender === 'female') {
                return category.key.startsWith('WOMENS_') || category.key === 'DRESS';
            }
            return true; // Show all if no gender selected
        });
        
        console.log(`Filtered categories for ${selectedGender}:`, categories);
        state.garmentCategories = categories;
        
        // Populate select element
        const select = elements.garmentCategorySelect;
        select.innerHTML = '';
        
        if (categories.length === 0) {
            select.innerHTML = '<option value="">No categories available for this gender</option>';
            return;
        }
        
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.key;
            option.textContent = category.name;
            select.appendChild(option);
        });
        
        // Select first category by default
        if (categories.length > 0) {
            select.value = categories[0].key;
        }
        
    } catch (error) {
        console.error('Error loading garment categories:', error);
        elements.garmentCategorySelect.innerHTML = '<option value="">Error loading categories</option>';
    }
}

// Handle category change
async function handleCategoryChange() {
    const category = elements.garmentCategorySelect.value;
    if (!category || !state.measurements) {
        return;
    }
    
    await getSizeRecommendations(category);
}

// Get size recommendations for selected category
async function getSizeRecommendations(category) {
    if (!state.measurements) {
        console.error('No measurements available');
        return;
    }
    
    try {
        const requestData = {
            garment_category: category,
            measurements: state.measurements
        };
        
        const response = await fetch('/api/size-recommendations/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to get size recommendations');
        }
        
        const data = await response.json();
        console.log('Size recommendations received:', data);
        
        if (data.success && data.recommendations && data.recommendations.length > 0) {
            displaySizeRecommendations(data);
            // Show the best recommended size under pose detection
            displayBestSizeUnderPoseDetection(data);
        } else {
            console.warn('No recommendations in response');
            elements.sizeRecGrid.innerHTML = '<p style="color: var(--text-secondary); padding: var(--spacing-md);">No size recommendations available for this category.</p>';
        }
        
        // Show size recommendation section
        elements.sizeRecommendationSection.style.display = 'block';
        
    } catch (error) {
        console.error('Error getting size recommendations:', error);
        elements.sizeRecGrid.innerHTML = '<p style="color: var(--error); padding: var(--spacing-md);">Error: ' + error.message + '</p>';
    }
}

// Display size recommendations in the grid
function displaySizeRecommendations(data) {
    const grid = elements.sizeRecGrid;
    grid.innerHTML = '';
    
    data.recommendations.forEach((rec, index) => {
        const card = createSizeCard(rec, index === 0); // First one is best fit
        grid.appendChild(card);
    });
}

// Create a size recommendation card
function createSizeCard(recommendation, isBestFit) {
    const card = document.createElement('div');
    card.className = 'size-card' + (isBestFit ? ' best-fit' : '');
    
    // fit_score is now 0-1, convert to percentage
    const fitScorePercent = (recommendation.fit_score * 100).toFixed(0);
    
    let fitAnalysisHTML = '';
    if (recommendation.fit_analysis && recommendation.fit_analysis.length > 0) {
        fitAnalysisHTML = `
            <div class="fit-details">
                <h4>Fit Analysis</h4>
                ${recommendation.fit_analysis.map(item => `
                    <div class="fit-detail-item">
                        <span class="fit-detail-label">${item.measurement.replace('_', ' ')}</span>
                        <span class="fit-detail-value">${item.analysis}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    card.innerHTML = `
        <div class="size-badge">${recommendation.size}</div>
        <div class="fit-score-container">
            <div class="fit-category">${recommendation.fit_category || 'Good Fit'}</div>
            <div class="fit-score">Fit Score: ${fitScorePercent}%</div>
            <div class="fit-score-bar">
                <div class="fit-score-fill" style="width: ${fitScorePercent}%"></div>
            </div>
        </div>
        ${fitAnalysisHTML}
    `;
    
    return card;
}

// Display the best recommended size under pose detection section
function displayBestSizeUnderPoseDetection(data) {
    const recommendedSizeDisplay = document.getElementById('recommendedSizeDisplay');
    const recommendedSizeContent = document.getElementById('recommendedSizeContent');
    
    if (!data.recommendations || data.recommendations.length === 0) {
        recommendedSizeDisplay.style.display = 'none';
        return;
    }
    
    const bestFit = data.recommendations[0];
    // fit_score is 0-1, convert to percentage
    const fitScorePercent = (bestFit.fit_score * 100).toFixed(0);
    
    recommendedSizeContent.innerHTML = `
        <div class="size-badge-small">${bestFit.size}</div>
        <div class="size-info">
            <p class="size-category">${data.garment_name}</p>
            <p class="size-fit-category">${bestFit.fit_category || 'Good Fit'} (${fitScorePercent}% match)</p>
        </div>
    `;
    
    recommendedSizeDisplay.style.display = 'block';
}
