// Global State
const state = {
    currentStep: 1,
    totalSteps: 8,
    items: [], // Array of completed items in the quote
    editingItemIndex: null, // Index of item being edited, null if adding new
    data: {
        chassisType: null,
        width: null,
        height: null,
        profileSeries: null,
        glazingType: null,
        finish: null,
        accessories: {}, // Format: {accessoryName: quantity}
        clientName: '',
        clientEmail: '',
        clientPhone: '',
        clientNotes: ''
    },
    catalog: {
        chassisTypes: [],
        profileSeries: [],
        glazingTypes: [],
        finishes: [],
        accessories: []
    },
    breakdown: null
};

// Utility: Format price in MAD
function formatMAD(amount) {
    if (amount === null || amount === undefined) return '0,00 MAD';
    return amount.toLocaleString('fr-MA', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }) + ' MAD';
}

// Authentication
async function checkAuth() {
    try {
        const response = await fetch('/api/auth/check', { credentials: 'include' });
        if (!response.ok) {
            window.location.href = '/login.html';
            return false;
        }
        return true;
    } catch (error) {
        window.location.href = '/login.html';
        return false;
    }
}

// Loading Indicator
function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'flex' : 'none';
}

// Load Catalog
async function loadCatalog() {
    try {
        const [chassisTypes, profileSeries, glazingTypes, finishes, accessories] = await Promise.all([
            fetch('/api/catalog/chassis-types', { credentials: 'include' }).then(r => r.json()),
            fetch('/api/catalog/profile-series', { credentials: 'include' }).then(r => r.json()),
            fetch('/api/catalog/glazing-types', { credentials: 'include' }).then(r => r.json()),
            fetch('/api/catalog/finishes', { credentials: 'include' }).then(r => r.json()),
            fetch('/api/catalog/accessories', { credentials: 'include' }).then(r => r.json())
        ]);
        
        state.catalog = { chassisTypes, profileSeries, glazingTypes, finishes, accessories };
        
        renderChassisTypes();
        renderProfileSeries();
        renderGlazingTypes();
        renderFinishes();
        renderAccessories();
        
    } catch (error) {
        console.error('Error loading catalog:', error);
        alert('Erreur lors du chargement du catalogue');
    }
}

// Step 1: Render Chassis Types
function renderChassisTypes() {
    const container = document.getElementById('chassisTypeOptions');
    container.innerHTML = state.catalog.chassisTypes.map(type => `
        <div class="product-card ${state.data.chassisType === type.name ? 'selected' : ''}" data-value="${type.name}">
            <h3>${type.name}</h3>
            <p>${type.description || ''}</p>
        </div>
    `).join('');
    
    container.querySelectorAll('.product-card').forEach(card => {
        card.addEventListener('click', () => {
            container.querySelectorAll('.product-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            state.data.chassisType = card.dataset.value;
            updateDimensionLimits();
            updateNavigation();
        });
    });
    
    // Update dimension limits if already selected
    if (state.data.chassisType) {
        updateDimensionLimits();
    }
}

function updateDimensionLimits() {
    const type = state.catalog.chassisTypes.find(t => t.name === state.data.chassisType);
    if (type) {
        const container = document.getElementById('dimensionLimits');
        container.innerHTML = `
            <strong>Limites pour ${type.name}:</strong><br>
            Largeur: ${type.min_width} - ${type.max_width} mm<br>
            Hauteur: ${type.min_height} - ${type.max_height} mm
        `;
        
        document.getElementById('width').min = type.min_width;
        document.getElementById('width').max = type.max_width;
        document.getElementById('height').min = type.min_height;
        document.getElementById('height').max = type.max_height;
        
        // Update dim-limits text
        document.querySelectorAll('.dim-limits')[0].textContent = `Min: ${type.min_height}mm, Max: ${type.max_height}mm`;
        document.querySelectorAll('.dim-limits')[1].textContent = `Min: ${type.min_width}mm, Max: ${type.max_width}mm`;
    }
}

// Step 3: Render Profile Series
function renderProfileSeries() {
    const container = document.getElementById('seriesOptions');
    container.innerHTML = state.catalog.profileSeries.map(series => `
        <div class="option-item ${state.data.profileSeries === series.name ? 'selected' : ''}" data-value="${series.name}">
            <h4>${series.name}</h4>
            <p>${series.description}</p>
            <p style="color: var(--primary); font-weight: 600; margin-top: 0.5rem;">${formatMAD(series.price_per_meter)}/ml</p>
        </div>
    `).join('');
    
    container.querySelectorAll('.option-item').forEach(item => {
        item.addEventListener('click', () => {
            container.querySelectorAll('.option-item').forEach(i => i.classList.remove('selected'));
            item.classList.add('selected');
            state.data.profileSeries = item.dataset.value;
            checkAccessoryCompatibility();
            updateNavigation();
        });
    });
}

// Step 4: Render Glazing Types with MAD prices
function renderGlazingTypes() {
    const container = document.getElementById('glazingOptions');
    
    // Group glazing by type
    const typeGroups = {};
    state.catalog.glazingTypes.forEach(glaze => {
        const mainType = glaze.name.includes('mm') ? 'Type de verre' : 'Teinte du verre';
        if (!typeGroups[mainType]) typeGroups[mainType] = [];
        typeGroups[mainType].push(glaze);
    });
    
    let html = '<h3 style="font-size: 1rem; font-weight: 600; margin-bottom: 1rem;">Type de verre</h3>';
    html += '<div class="glazing-grid">';
    
    const glassTypes = state.catalog.glazingTypes.filter(g => g.name.includes('mm') || g.name.includes('Feuilleté') || g.name.includes('Sécurité'));
    glassTypes.forEach(glaze => {
        const pricePerM2 = glaze.price_per_m2 || 0;
        html += `
            <div class="glazing-card" data-value="${glaze.name}">
                <h4>${glaze.name}</h4>
                <p class="description">${glaze.description || ''}</p>
                <div class="price-info">
                    <span class="price-primary">${formatMAD(pricePerM2)}/m²</span>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    // Glazing tints
    const tints = state.catalog.glazingTypes.filter(g => !g.name.includes('mm') && !g.name.includes('Feuilleté') && !g.name.includes('Sécurité'));
    if (tints.length > 0) {
        html += '<h3 style="font-size: 1rem; font-weight: 600; margin: 2rem 0 1rem;">Teinte du verre</h3>';
        html += '<div class="glazing-grid">';
        tints.forEach(tint => {
            const coefficient = tint.coefficient || 1;
            const badge = coefficient > 1 ? `+${((coefficient - 1) * 100).toFixed(0)}%` : 'Standard';
            html += `
                <div class="glazing-card" data-value="${tint.name}">
                    <h4>${tint.name}</h4>
                    <p class="finish-badge">${badge}</p>
                </div>
            `;
        });
        html += '</div>';
    }
    
    container.innerHTML = html;
    
    container.querySelectorAll('.glazing-card').forEach(card => {
        // Restore selected state if already chosen
        if (state.data.glazingType === card.dataset.value) {
            card.classList.add('selected');
        }
        
        card.addEventListener('click', () => {
            container.querySelectorAll('.glazing-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            state.data.glazingType = card.dataset.value;
            updateNavigation();
        });
    });
}

// Step 5: Render Accessories with Quantities
function renderAccessories() {
    const container = document.getElementById('accessoriesOptions');
    
    // Group accessories by category
    const categories = {
        'Charnières': [],
        'Crémones': [],
        'Gonds': [],
        'Joints': [],
        'Poignées': [],
        'Rails': [],
        'Serrures': []
    };
    
    state.catalog.accessories.forEach(acc => {
        const name = acc.name;
        if (name.includes('Charnière')) categories['Charnières'].push(acc);
        else if (name.includes('Crémone')) categories['Crémones'].push(acc);
        else if (name.includes('Gond')) categories['Gonds'].push(acc);
        else if (name.includes('Joint') || name.includes('étanchéité')) categories['Joints'].push(acc);
        else if (name.includes('Poignée')) categories['Poignées'].push(acc);
        else if (name.includes('Rail')) categories['Rails'].push(acc);
        else if (name.includes('Serrure')) categories['Serrures'].push(acc);
    });
    
    let html = '<div class="accessories-container">';
    
    Object.keys(categories).forEach(category => {
        if (categories[category].length > 0) {
            html += `
                <div class="accessory-category">
                    <div class="accessory-category-title">${category}</div>
            `;
            
            categories[category].forEach(acc => {
                const qty = state.data.accessories[acc.name] || 0;
                html += `
                    <div class="accessory-item-new" data-name="${acc.name}" data-price="${acc.unit_price}" data-incompatible="${acc.incompatible_series || ''}">
                        <div class="accessory-details">
                            <div class="accessory-name">${acc.name}</div>
                            <div class="accessory-price">${formatMAD(acc.unit_price)}</div>
                        </div>
                        <div class="quantity-controls">
                            <button class="qty-btn qty-minus" data-name="${acc.name}">−</button>
                            <span class="qty-display" data-name="${acc.name}">${qty}</span>
                            <button class="qty-btn qty-plus" data-name="${acc.name}">+</button>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
        }
    });
    
    html += '<div class="accessory-total"><span class="accessory-total-label">Total accessoires:</span><span class="accessory-total-price" id="accessoryTotalPrice">' + formatMAD(0) + '</span></div>';
    html += '</div>';
    
    container.innerHTML = html;
    
    // Add event listeners for quantity buttons
    container.querySelectorAll('.qty-minus').forEach(btn => {
        btn.addEventListener('click', () => {
            const name = btn.dataset.name;
            if (state.data.accessories[name] && state.data.accessories[name] > 0) {
                state.data.accessories[name]--;
                if (state.data.accessories[name] === 0) {
                    delete state.data.accessories[name];
                }
                updateAccessoryDisplay(name);
                updateAccessoryTotal();
            }
        });
    });
    
    container.querySelectorAll('.qty-plus').forEach(btn => {
        btn.addEventListener('click', () => {
            const name = btn.dataset.name;
            const item = btn.closest('.accessory-item-new');
            if (!item.classList.contains('disabled')) {
                state.data.accessories[name] = (state.data.accessories[name] || 0) + 1;
                updateAccessoryDisplay(name);
                updateAccessoryTotal();
            }
        });
    });
}

function updateAccessoryDisplay(name) {
    const qty = state.data.accessories[name] || 0;
    const displays = document.querySelectorAll(`.qty-display[data-name="${name}"]`);
    displays.forEach(display => {
        display.textContent = qty;
    });
}

function updateAccessoryTotal() {
    let total = 0;
    Object.keys(state.data.accessories).forEach(name => {
        const acc = state.catalog.accessories.find(a => a.name === name);
        if (acc) {
            total += acc.unit_price * state.data.accessories[name];
        }
    });
    
    const totalElement = document.getElementById('accessoryTotalPrice');
    if (totalElement) {
        totalElement.textContent = formatMAD(total);
    }
}

function checkAccessoryCompatibility() {
    const container = document.getElementById('accessoriesOptions');
    const warning = document.getElementById('incompatibilityWarning');
    let hasIncompatibility = false;
    
    container.querySelectorAll('.accessory-item-new').forEach(item => {
        const incompatible = item.dataset.incompatible;
        
        if (incompatible && incompatible === state.data.profileSeries) {
            item.classList.add('disabled');
            const name = item.dataset.name;
            delete state.data.accessories[name];
            updateAccessoryDisplay(name);
            hasIncompatibility = true;
        } else {
            item.classList.remove('disabled');
        }
    });
    
    if (hasIncompatibility) {
        warning.textContent = `Certains accessoires ne sont pas compatibles avec ${state.data.profileSeries}`;
        warning.classList.add('show');
    } else {
        warning.classList.remove('show');
    }
    
    updateAccessoryTotal();
}

// Step 6: Render Finishes grouped
function renderFinishes() {
    const container = document.getElementById('finishOptions');
    
    // Group finishes by category
    const groups = {
        'Anodisé': [],
        'Aluminium Brut': [],
        'Imitation Bois': [],
        'Thermolaqué': []
    };
    
    state.catalog.finishes.forEach(finish => {
        const name = finish.name;
        if (name.includes('Anodisé')) groups['Anodisé'].push(finish);
        else if (name.includes('Aluminium brut')) groups['Aluminium Brut'].push(finish);
        else if (name.includes('Imitation bois')) groups['Imitation Bois'].push(finish);
        else if (name.includes('Thermolaqué') || name.includes('RAL')) groups['Thermolaqué'].push(finish);
    });
    
    let html = '<div class="finish-groups">';
    
    Object.keys(groups).forEach(groupName => {
        if (groups[groupName].length > 0) {
            html += `
                <div class="finish-group">
                    <div class="finish-group-title">${groupName}</div>
                    <div class="finish-grid">
            `;
            
            groups[groupName].forEach(finish => {
                const coefficient = finish.coefficient || 1;
                const badge = coefficient > 1 ? `+${((coefficient - 1) * 100).toFixed(0)}%` : 'Standard';
                html += `
                    <div class="finish-card" data-value="${finish.name}">
                        <div class="finish-card-header">
                            <div class="finish-name">${finish.name}</div>
                            <div class="finish-badge">${badge}</div>
                        </div>
                        <div class="finish-description">${finish.description || ''}</div>
                    </div>
                `;
            });
            
            html += '</div></div>';
        }
    });
    
    html += '</div>';
    container.innerHTML = html;
    
    container.querySelectorAll('.finish-card').forEach(card => {
        // Restore selected state if already chosen
        if (state.data.finish === card.dataset.value) {
            card.classList.add('selected');
        }
        
        card.addEventListener('click', () => {
            container.querySelectorAll('.finish-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            state.data.finish = card.dataset.value;
            updateNavigation();
        });
    });
}

// Dimension validation
function validateDimensions() {
    const type = state.catalog.chassisTypes.find(t => t.name === state.data.chassisType);
    if (!type) return false;
    
    const width = parseInt(document.getElementById('width').value);
    const height = parseInt(document.getElementById('height').value);
    
    const widthError = document.getElementById('widthError');
    const heightError = document.getElementById('heightError');
    const widthInput = document.getElementById('width');
    const heightInput = document.getElementById('height');
    
    let valid = true;
    
    if (!height || height < type.min_height || height > type.max_height) {
        heightError.textContent = `Hauteur invalide (${type.min_height}-${type.max_height} mm)`;
        heightInput.classList.add('error');
        valid = false;
    } else {
        heightError.textContent = '';
        heightInput.classList.remove('error');
    }
    
    if (!width || width < type.min_width || width > type.max_width) {
        widthError.textContent = `Largeur invalide (${type.min_width}-${type.max_width} mm)`;
        widthInput.classList.add('error');
        valid = false;
    } else {
        widthError.textContent = '';
        widthInput.classList.remove('error');
    }
    
    if (valid) {
        state.data.width = width;
        state.data.height = height;
    }
    
    return valid;
}

function updateCalculatedValues() {
    if (!state.data.width || !state.data.height) return;
    
    const container = document.getElementById('calculatedValues');
    const surface = (state.data.width * state.data.height) / 1000000;
    
    container.innerHTML = `
        <p style="font-weight: 600; color: var(--primary);"><strong>Surface:</strong> ${surface.toFixed(2)} m²</p>
    `;
}

// Progress & Navigation
function updateProgress() {
    document.querySelectorAll('.step-item').forEach((item, index) => {
        const stepNum = index + 1;
        if (stepNum < state.currentStep) {
            item.classList.add('completed');
            item.classList.remove('active');
        } else if (stepNum === state.currentStep) {
            item.classList.add('active');
            item.classList.remove('completed');
        } else {
            item.classList.remove('active', 'completed');
        }
    });
}

function showStep(stepNumber) {
    document.querySelectorAll('.step').forEach(step => step.classList.remove('active'));
    document.getElementById(`step${stepNumber}`).classList.add('active');
    
    state.currentStep = stepNumber;
    updateProgress();
    updateNavigation();
}

function updateNavigation() {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const viewSummaryBtn = document.getElementById('viewSummaryBtn');
    const addItemBtn = document.getElementById('addItemBtn');
    const addAnotherBtn = document.getElementById('addAnotherBtn');
    const saveQuoteBtn = document.getElementById('saveQuoteBtn');
    
    prevBtn.style.display = state.currentStep === 1 ? 'none' : 'block';
    nextBtn.style.display = state.currentStep < 7 ? 'block' : 'none';
    viewSummaryBtn.style.display = state.currentStep === 7 ? 'block' : 'none';
    
    // Step 8: Show appropriate buttons
    if (state.currentStep === 8) {
        // Show current item section
        document.getElementById('currentItem').style.display = 'block';
        document.getElementById('quantitySection').style.display = 'block';
        addItemBtn.style.display = 'block';
        addAnotherBtn.style.display = 'none';
        saveQuoteBtn.style.display = state.items.length > 0 ? 'block' : 'none';
    } else {
        addItemBtn.style.display = 'none';
        addAnotherBtn.style.display = 'none';
        saveQuoteBtn.style.display = 'none';
        if (document.getElementById('quantitySection')) {
            document.getElementById('quantitySection').style.display = 'none';
        }
    }
    
    const canProgress = canProgressToNextStep();
    nextBtn.disabled = !canProgress;
    viewSummaryBtn.disabled = !canProgressToNextStep();
}

function canProgressToNextStep() {
    switch(state.currentStep) {
        case 1:
            return state.data.chassisType !== null;
        case 2:
            return state.data.width !== null && state.data.height !== null;
        case 3:
            return state.data.profileSeries !== null;
        case 4:
            return state.data.glazingType !== null;
        case 5:
            return true; // Accessories optional
        case 6:
            return state.data.finish !== null;
        case 7:
            return state.data.clientName.trim() !== '';
        default:
            return false;
    }
}

function getValidationMessage() {
    switch(state.currentStep) {
        case 1:
            return 'Veuillez sélectionner un type de châssis';
        case 2:
            return 'Veuillez entrer les dimensions (largeur et hauteur)';
        case 3:
            return 'Veuillez sélectionner une série de profilés';
        case 4:
            return 'Veuillez sélectionner un type de vitrage';
        case 6:
            return 'Veuillez sélectionner une finition';
        case 7:
            return 'Veuillez entrer le nom du client';
        default:
            return 'Veuillez compléter cette étape';
    }
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: #ef4444; color: white; padding: 1rem 1.5rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 9999; animation: slideDown 0.3s ease-out;';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.style.animation = 'slideUp 0.3s ease-in';
        setTimeout(() => errorDiv.remove(), 300);
    }, 3000);
}

function showToast(message, type = 'info') {
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        info: '#3b82f6',
        warning: '#f59e0b'
    };
    
    const toastDiv = document.createElement('div');
    toastDiv.style.cssText = `position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: ${colors[type] || colors.info}; color: white; padding: 1rem 1.5rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 9999; animation: slideDown 0.3s ease-out;`;
    toastDiv.textContent = message;
    document.body.appendChild(toastDiv);
    
    setTimeout(() => {
        toastDiv.style.animation = 'slideUp 0.3s ease-in';
        setTimeout(() => toastDiv.remove(), 300);
    }, 3000);
}

// Calculate Price
async function calculateAndShowSummary() {
    // Collect client data
    state.data.clientName = document.getElementById('clientName').value;
    state.data.clientEmail = document.getElementById('clientEmail').value;
    state.data.clientPhone = document.getElementById('clientPhone').value;
    state.data.clientNotes = document.getElementById('clientNotes').value;
    
    if (!state.data.clientName.trim()) {
        showError('Veuillez renseigner le nom du client');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/quotes/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(state.data),
            credentials: 'include'
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.error || 'Erreur lors du calcul');
        }
        
        state.breakdown = await response.json();
        renderSummary();
        showStep(8);
        
    } catch (error) {
        console.error('Error calculating price:', error);
        showError(error.message || 'Erreur lors du calcul du prix. Vérifiez toutes les données.');
    } finally {
        showLoading(false);
    }
}

// Render Summary
function renderSummary() {
    const summaryContent = document.getElementById('summaryContent');
    const priceBreakdown = document.getElementById('priceBreakdown');
    
    // Summary sections
    let summaryHTML = '';
    
    // Product info
    summaryHTML += `
        <div class="summary-section">
            <div class="summary-section-title">PRODUIT</div>
            <div class="summary-item">
                <div class="summary-value">${state.data.chassisType}</div>
            </div>
        </div>
    `;
    
    // Dimensions
    const surface = (state.data.width * state.data.height) / 1000000;
    summaryHTML += `
        <div class="summary-section">
            <div class="summary-section-title">DIMENSIONS</div>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="summary-value">${state.data.width} x ${state.data.height} mm</div>
                    <div class="summary-label">${surface.toFixed(2)} m²</div>
                </div>
            </div>
        </div>
    `;
    
    // Profile & Glazing
    summaryHTML += `
        <div class="summary-section">
            <div class="summary-section-title">PROFILÉ</div>
            <div class="summary-value">${state.data.profileSeries}</div>
        </div>
        <div class="summary-section">
            <div class="summary-section-title">VITRAGE</div>
            <div class="summary-value">${state.data.glazingType}</div>
        </div>
    `;
    
    // Finish
    summaryHTML += `
        <div class="summary-section">
            <div class="summary-section-title">FINITION</div>
            <div class="summary-value">${state.data.finish}</div>
        </div>
    `;
    
    // Accessories
    const accList = Object.keys(state.data.accessories).map(name => 
        `${name} (unité) x ${state.data.accessories[name]}`
    ).join('<br>');
    
    if (accList) {
        summaryHTML += `
            <div class="summary-section">
                <div class="summary-section-title">ACCESSOIRES</div>
                <div class="summary-value" style="font-size: 0.9375rem; line-height: 1.6;">${accList}</div>
            </div>
        `;
    }
    
    // Client
    summaryHTML += `
        <div class="summary-section">
            <div class="summary-section-title">CLIENT</div>
            <div class="summary-value">${state.data.clientName}</div>
            ${state.data.clientEmail ? `<div class="summary-label">${state.data.clientEmail}</div>` : ''}
            ${state.data.clientPhone ? `<div class="summary-label">${state.data.clientPhone}</div>` : ''}
            ${state.data.clientNotes ? `<div class="summary-label" style="margin-top: 0.5rem; font-style: italic;">${state.data.clientNotes}</div>` : ''}
        </div>
    `;
    
    summaryContent.innerHTML = summaryHTML;
    
    // Price breakdown
    if (state.breakdown) {
        let priceHTML = `
            <div class="price-breakdown-title">Détail des prix</div>
            <div class="price-line">
                <span class="price-line-label">Prix de base</span>
                <span class="price-line-value">${formatMAD(state.breakdown.base_price)}</span>
            </div>
            <div class="price-line">
                <span class="price-line-label">Vitrage</span>
                <span class="price-line-value">${formatMAD(state.breakdown.glazing_cost)}</span>
            </div>
            <div class="price-line">
                <span class="price-line-label">Accessoires</span>
                <span class="price-line-value">${formatMAD(state.breakdown.accessories_cost)}</span>
            </div>
            <div class="price-line">
                <span class="price-line-label">Supplément finition</span>
                <span class="price-line-value">${formatMAD(state.breakdown.finish_supplement)}</span>
            </div>
            <div class="price-total">
                <span class="price-total-label">Total TTC</span>
                <span class="price-total-value">${formatMAD(state.breakdown.total_price)}</span>
            </div>
        `;
        
        priceBreakdown.innerHTML = priceHTML;
    }
}

// Add current item to items list
function addItemToQuote() {
    const quantity = parseInt(document.getElementById('itemQuantity').value) || 1;
    
    const item = {
        ...state.data,
        breakdown: state.breakdown,
        quantity: quantity
    };
    
    if (state.editingItemIndex !== null) {
        // Update existing item
        state.items[state.editingItemIndex] = item;
        state.editingItemIndex = null;
    } else {
        // Add new item
        state.items.push(item);
    }
    
    // Show items list and update display
    updateItemsList();
    
    // Hide current item section and show "add another" button
    document.getElementById('currentItem').style.display = 'none';
    document.getElementById('quantitySection').style.display = 'none';
    document.getElementById('addItemBtn').style.display = 'none';
    document.getElementById('addAnotherBtn').style.display = 'inline-flex';
    document.getElementById('saveQuoteBtn').style.display = 'inline-flex';
}

// Start new item (reset workflow)
function addAnotherItem() {
    // Reset current item data (except client info which stays the same)
    const clientInfo = {
        clientName: state.data.clientName,
        clientEmail: state.data.clientEmail,
        clientPhone: state.data.clientPhone,
        clientNotes: state.data.clientNotes
    };
    
    state.data = {
        chassisType: null,
        width: null,
        height: null,
        profileSeries: null,
        glazingType: null,
        finish: null,
        accessories: {},
        ...clientInfo
    };
    state.breakdown = null;
    state.editingItemIndex = null;
    
    // Reset all form fields
    document.getElementById('width').value = '';
    document.getElementById('height').value = '';
    document.getElementById('itemQuantity').value = '1';
    
    // Clear selected options (remove active classes)
    document.querySelectorAll('.product-option.active, .option-card.active').forEach(el => {
        el.classList.remove('active');
    });
    
    // Clear accessory checkboxes
    document.querySelectorAll('#accessoriesOptions input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
    });
    
    // Clear calculated values
    const calculatedValues = document.getElementById('calculatedValues');
    if (calculatedValues) {
        calculatedValues.innerHTML = '';
    }
    
    // Go back to step 1
    showStep(1);
}

// Edit an existing item
function editItem(index) {
    const item = state.items[index];
    state.data = { ...item };
    state.breakdown = item.breakdown;
    state.editingItemIndex = index;
    
    // Go to step 1 to edit
    showStep(1);
}

// Delete an item
function deleteItem(index) {
    if (confirm('Supprimer cet article du devis ?')) {
        state.items.splice(index, 1);
        updateItemsList();
        
        // If no items left, hide the save button
        if (state.items.length === 0) {
            document.getElementById('saveQuoteBtn').style.display = 'none';
        }
    }
}

// Update items list display
function updateItemsList() {
    const itemsList = document.getElementById('itemsList');
    const itemsContainer = document.getElementById('itemsContainer');
    const itemsCount = document.getElementById('itemsCount');
    
    if (state.items.length === 0) {
        itemsList.style.display = 'none';
        return;
    }
    
    itemsList.style.display = 'block';
    itemsCount.textContent = state.items.length;
    
    let totalGlobal = 0;
    let itemsHTML = '';
    
    state.items.forEach((item, index) => {
        const surface = (item.width * item.height) / 1000000;
        const accList = Object.keys(item.accessories).length > 0 ? 
            Object.keys(item.accessories).map(name => `${name} x${item.accessories[name]}`).join(', ') : 
            'Aucun';
        
        const quantity = item.quantity || 1;
        const itemTotal = item.breakdown.total_price * quantity;
        totalGlobal += itemTotal;
        
        itemsHTML += `
            <div class="item-card">
                <div class="item-card-header">
                    <h4>Article ${index + 1}: ${item.chassisType}</h4>
                    <div class="item-card-actions">
                        <button class="btn-icon" onclick="editItem(${index})" title="Modifier">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                            </svg>
                        </button>
                        <button class="btn-icon btn-icon-danger" onclick="deleteItem(${index})" title="Supprimer">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="item-card-body">
                    <div class="item-info-row">
                        <span class="item-info-label">Dimensions:</span>
                        <span class="item-info-value">${item.width} x ${item.height} mm (${surface.toFixed(2)} m²)</span>
                    </div>
                    <div class="item-info-row">
                        <span class="item-info-label">Profilé:</span>
                        <span class="item-info-value">${item.profileSeries}</span>
                    </div>
                    <div class="item-info-row">
                        <span class="item-info-label">Vitrage:</span>
                        <span class="item-info-value">${item.glazingType}</span>
                    </div>
                    <div class="item-info-row">
                        <span class="item-info-label">Finition:</span>
                        <span class="item-info-value">${item.finish}</span>
                    </div>
                    <div class="item-info-row">
                        <span class="item-info-label">Accessoires:</span>
                        <span class="item-info-value">${accList}</span>
                    </div>
                    <div class="item-info-row">
                        <span class="item-info-label">Quantité:</span>
                        <span class="item-info-value">${quantity}</span>
                    </div>
                    <div class="item-price">
                        ${formatMAD(item.breakdown.total_price)} × ${quantity} = ${formatMAD(itemTotal)}
                    </div>
                </div>
            </div>
        `;
    });
    
    // Add total
    itemsHTML += `
        <div class="items-total">
            <span class="items-total-label">Total du devis</span>
            <span class="items-total-value">${formatMAD(totalGlobal)}</span>
        </div>
    `;
    
    itemsContainer.innerHTML = itemsHTML;
}

// Save Quote (with all items)
async function saveQuote() {
    if (state.items.length === 0) {
        alert('Ajoutez au moins un article au devis avant d\'enregistrer');
        return;
    }
    
    showLoading(true);
    
    try {
        // Use the first item's client info and calculate total
        const firstItem = state.items[0];
        const totalPrice = state.items.reduce((sum, item) => {
            const quantity = item.quantity || 1;
            return sum + (item.breakdown.total_price * quantity);
        }, 0);
        
        const response = await fetch('/api/quotes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chassisType: `Devis multiple (${state.items.length} articles)`,
                width: 0,
                height: 0,
                profileSeries: 'Multiple',
                glazingType: 'Multiple',
                finish: 'Multiple',
                accessories: {},
                clientName: firstItem.clientName,
                clientEmail: firstItem.clientEmail,
                clientPhone: firstItem.clientPhone,
                clientNotes: firstItem.clientNotes,
                breakdown: {
                    items: state.items,
                    total_price: totalPrice
                }
            }),
            credentials: 'include'
        });
        
        if (!response.ok) throw new Error('Save failed');
        
        const result = await response.json();
        alert('Devis enregistré avec succès !');
        
        // Generate PDF
        await generatePDF(result.quote_id);
        
    } catch (error) {
        console.error('Error saving quote:', error);
        alert('Erreur lors de l\'enregistrement du devis');
    } finally {
        showLoading(false);
    }
}

// Generate PDF
async function generatePDF(quoteId) {
    try {
        const response = await fetch(`/api/quotes/${quoteId}/pdf`, { credentials: 'include' });
        
        if (!response.ok) throw new Error('PDF generation failed');
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `devis_${quoteId}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        // Redirect to dashboard after short delay
        setTimeout(() => {
            window.location.href = '/dashboard.html';
        }, 2000);
        
    } catch (error) {
        console.error('Error generating PDF:', error);
        alert('Erreur lors de la génération du PDF');
    }
}

// Event Listeners
document.getElementById('cancelBtn').addEventListener('click', () => {
    if (confirm('Voulez-vous vraiment annuler ? Toutes les données seront perdues.')) {
        window.location.href = '/dashboard.html';
    }
});

document.getElementById('prevBtn').addEventListener('click', () => {
    if (state.currentStep > 1) {
        showStep(state.currentStep - 1);
    }
});

document.getElementById('nextBtn').addEventListener('click', () => {
    // Check if button is disabled
    if (document.getElementById('nextBtn').disabled) {
        showError(getValidationMessage());
        return;
    }
    
    if (state.currentStep === 2) {
        if (!validateDimensions()) return;
    }
    
    if (state.currentStep < 7) {
        if (canProgressToNextStep()) {
            showStep(state.currentStep + 1);
        } else {
            showError(getValidationMessage());
        }
    }
});

document.getElementById('viewSummaryBtn').addEventListener('click', calculateAndShowSummary);
document.getElementById('addItemBtn').addEventListener('click', addItemToQuote);
document.getElementById('addAnotherBtn').addEventListener('click', addAnotherItem);
document.getElementById('saveQuoteBtn').addEventListener('click', saveQuote);

document.getElementById('width').addEventListener('input', () => {
    state.data.width = parseInt(document.getElementById('width').value) || null;
    if (state.currentStep === 2) {
        updateCalculatedValues();
        updateNavigation();
    }
});

document.getElementById('height').addEventListener('input', () => {
    state.data.height = parseInt(document.getElementById('height').value) || null;
    if (state.currentStep === 2) {
        updateCalculatedValues();
        updateNavigation();
    }
});

document.getElementById('clientName').addEventListener('input', () => {
    state.data.clientName = document.getElementById('clientName').value;
    updateNavigation();
});

document.getElementById('dashboardBtn').addEventListener('click', () => {
    window.location.href = '/dashboard.html';
});

document.getElementById('profileBtn').addEventListener('click', () => {
    window.location.href = '/profile.html';
});

document.getElementById('settingsBtn').addEventListener('click', () => {
    window.location.href = '/settings.html';
});

document.getElementById('logoutBtn').addEventListener('click', async () => {
    try {
        await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
        window.location.href = '/login.html';
    } catch (error) {
        console.error('Logout failed:', error);
        window.location.href = '/login.html';
    }
});

// Quantity controls
document.getElementById('decreaseQty').addEventListener('click', () => {
    const qtyInput = document.getElementById('itemQuantity');
    const currentQty = parseInt(qtyInput.value) || 1;
    if (currentQty > 1) {
        qtyInput.value = currentQty - 1;
    }
});

document.getElementById('increaseQty').addEventListener('click', () => {
    const qtyInput = document.getElementById('itemQuantity');
    const currentQty = parseInt(qtyInput.value) || 1;
    qtyInput.value = currentQty + 1;
});

// Service Worker (disabled during development)
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').then(() => {
        console.log('Service Worker registered');
    }).catch(err => {
        console.log('Service Worker registration failed:', err);
    });
}

// Initialize
async function init() {
    if (await checkAuth()) {
        await loadCatalog();
        
        // Check if we're in edit mode
        const urlParams = new URLSearchParams(window.location.search);
        const editId = urlParams.get('edit');
        
        if (editId) {
            await loadQuoteForEdit(editId);
        }
        
        updateProgress();
        updateNavigation();
    }
}

async function loadQuoteForEdit(quoteId) {
    try {
        const response = await fetch(`/api/quotes/${quoteId}`, { credentials: 'include' });
        if (!response.ok) throw new Error('Failed to load quote');
        
        const quote = await response.json();
        const details = typeof quote.details === 'string' ? JSON.parse(quote.details) : quote.details;
        const items = details.items || [];
        
        // If multi-item quote, load all items
        if (items.length > 0) {
            state.items = items;
            state.editingItemIndex = null;
            
            // Load first item for editing
            const firstItem = items[0];
            state.data = {
                chassisType: firstItem.chassisType,
                width: firstItem.width,
                height: firstItem.height,
                profileSeries: firstItem.profileSeries,
                glazingType: firstItem.glazingType,
                finish: firstItem.finish,
                accessories: firstItem.accessories || {},
                clientName: details.client_name || '',
                clientEmail: details.client_email || '',
                clientPhone: details.client_phone || '',
                clientNotes: details.client_notes || ''
            };
            state.breakdown = firstItem.breakdown;
        } else {
            // Single item quote
            const accessories = typeof quote.accessories === 'string' ? JSON.parse(quote.accessories) : quote.accessories;
            state.data = {
                chassisType: quote.chassis_type,
                width: quote.width,
                height: quote.height,
                profileSeries: quote.profile_series,
                glazingType: quote.glazing_type,
                finish: quote.finish,
                accessories: accessories || {},
                clientName: details.client_name || '',
                clientEmail: details.client_email || '',
                clientPhone: details.client_phone || '',
                clientNotes: details.client_notes || ''
            };
        }
        
        // Pre-fill form fields for client info
        if (state.data.clientName) document.getElementById('clientName').value = state.data.clientName;
        if (state.data.clientEmail) document.getElementById('clientEmail').value = state.data.clientEmail;
        if (state.data.clientPhone) document.getElementById('clientPhone').value = state.data.clientPhone;
        if (state.data.clientNotes) document.getElementById('clientNotes').value = state.data.clientNotes;
        
        // Pre-fill dimensions
        if (state.data.width) document.getElementById('width').value = state.data.width;
        if (state.data.height) document.getElementById('height').value = state.data.height;
        
        // Re-render all steps to show selected items
        renderChassisTypes();
        renderProfileSeries();
        renderGlazingTypes();
        renderFinishes();
        renderAccessories();
        
        showToast('Devis chargé pour modification', 'success');
    } catch (error) {
        console.error('Error loading quote for edit:', error);
        showToast('Erreur lors du chargement du devis', 'error');
    }
}

init();
