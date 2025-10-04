let currentUser = null;
let settings = {};

async function checkAuth() {
    try {
        const response = await fetch('/api/auth/check', { credentials: 'include' });
        const data = await response.json();
        
        if (!data.authenticated) {
            window.location.href = '/login.html';
            return false;
        }
        
        currentUser = data.user;
        return true;
    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.href = '/login.html';
        return false;
    }
}

async function loadSettings(section = null) {
    const url = section ? `/api/settings?section=${section}` : '/api/settings';
    const response = await fetch(url, { credentials: 'include' });
    const data = await response.json();
    
    data.forEach(item => {
        if (!settings[item.section]) settings[item.section] = {};
        settings[item.section][item.key] = item.value;
    });
    
    return settings;
}

async function saveSetting(section, key, value) {
    const response = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ section, key, value }),
        credentials: 'include'
    });
    
    if (response.ok) {
        if (!settings[section]) settings[section] = {};
        settings[section][key] = value;
        showToast('Paramètre sauvegardé', 'success');
    } else {
        showToast('Erreur de sauvegarde', 'error');
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    setTimeout(() => toast.classList.remove('show'), 3000);
}

function showSection(sectionName) {
    const content = document.getElementById('settingsContent');
    
    const sections = {
        company: renderCompanySection,
        quote: renderQuoteSection,
        pdf: renderPdfSection,
        currency: renderCurrencySection,
        tax: renderTaxSection,
        discount: renderDiscountSection,
        labor: renderLaborSection,
        coefficients: renderCoefficientsSection,
        catalog: renderCatalogSection,
        import: renderImportSection,
        users: renderUsersSection,
        theme: renderThemeSection,
        about: renderAboutSection
    };
    
    if (sections[sectionName]) {
        content.innerHTML = sections[sectionName]();
        attachSectionHandlers(sectionName);
    }
}

function renderCompanySection() {
    const company = settings.company || {};
    return `
        <div class="settings-section">
            <h2>Logo & Identité</h2>
            <p class="section-subtitle">Informations de votre entreprise affichées sur les devis</p>
            
            <div class="form-group">
                <label for="companyName">Raison sociale</label>
                <input type="text" id="companyName" value="${company.company_name || ''}" data-section="company" data-key="company_name">
            </div>
            
            <div class="form-group">
                <label for="companyAddress">Adresse</label>
                <textarea id="companyAddress" rows="3" data-section="company" data-key="company_address">${company.company_address || ''}</textarea>
            </div>
            
            <div class="form-group">
                <label for="companyPhone">Téléphone</label>
                <input type="tel" id="companyPhone" value="${company.company_phone || ''}" data-section="company" data-key="company_phone">
            </div>
            
            <div class="form-group">
                <label for="companyEmail">Email</label>
                <input type="email" id="companyEmail" value="${company.company_email || ''}" data-section="company" data-key="company_email">
            </div>
            
            <div class="form-group">
                <label for="companyLogo">Logo (URL)</label>
                <input type="url" id="companyLogo" value="${company.company_logo || ''}" data-section="company" data-key="company_logo">
                <small>URL d'une image pour le logo de l'entreprise</small>
            </div>
            
            <h3 style="margin-top: 2rem; margin-bottom: 1rem; color: #3B82F6;">📏 Dimensions Châssis</h3>
            <p class="section-subtitle">Limites de dimensions pour les châssis (en mm)</p>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                    <label for="minWidth">Largeur minimale (mm)</label>
                    <input type="number" id="minWidth" value="${company.min_width || 300}" data-section="company" data-key="min_width" min="100" max="5000">
                </div>
                
                <div class="form-group">
                    <label for="maxWidth">Largeur maximale (mm)</label>
                    <input type="number" id="maxWidth" value="${company.max_width || 3000}" data-section="company" data-key="max_width" min="100" max="10000">
                </div>
                
                <div class="form-group">
                    <label for="minHeight">Hauteur minimale (mm)</label>
                    <input type="number" id="minHeight" value="${company.min_height || 300}" data-section="company" data-key="min_height" min="100" max="5000">
                </div>
                
                <div class="form-group">
                    <label for="maxHeight">Hauteur maximale (mm)</label>
                    <input type="number" id="maxHeight" value="${company.max_height || 3000}" data-section="company" data-key="max_height" min="100" max="10000">
                </div>
            </div>
        </div>
    `;
}

function renderQuoteSection() {
    const quote = settings.quote || {};
    return `
        <div class="settings-section">
            <h2>Numérotation des Devis</h2>
            <p class="section-subtitle">Configuration du format de numérotation automatique</p>
            
            <div class="form-group">
                <label for="quotePrefix">Préfixe</label>
                <input type="text" id="quotePrefix" value="${quote.prefix || 'DEV'}" data-section="quote" data-key="prefix">
                <small>Exemple : DEV, DEVIS, Q</small>
            </div>
            
            <div class="form-group">
                <label for="quoteFormat">Format</label>
                <input type="text" id="quoteFormat" value="${quote.format || '{PREFIX}-{YEAR}-{NUMBER}'}" data-section="quote" data-key="format">
                <small>Variables : {PREFIX}, {YEAR}, {MONTH}, {NUMBER}</small>
            </div>
            
            <div class="form-group">
                <label for="quoteCounter">Compteur actuel</label>
                <input type="number" id="quoteCounter" value="${quote.counter || '1'}" data-section="quote" data-key="counter">
            </div>
            
            <div class="form-group">
                <label for="quoteValidity">Validité (jours)</label>
                <input type="number" id="quoteValidity" value="${quote.validity_days || '30'}" data-section="quote" data-key="validity_days">
            </div>
        </div>
    `;
}

function renderPdfSection() {
    const pdf = settings.pdf || {};
    return `
        <div class="settings-section">
            <h2>Modèle PDF</h2>
            <p class="section-subtitle">Personnalisation de l'en-tête et pied de page des PDF</p>
            
            <div class="form-group">
                <label for="pdfHeader">En-tête personnalisé</label>
                <textarea id="pdfHeader" rows="3" data-section="pdf" data-key="header">${pdf.header || ''}</textarea>
                <small>Texte affiché en haut du PDF</small>
            </div>
            
            <div class="form-group">
                <label for="pdfFooter">Pied de page</label>
                <textarea id="pdfFooter" rows="3" data-section="pdf" data-key="footer">${pdf.footer || ''}</textarea>
                <small>Texte affiché en bas du PDF</small>
            </div>
            
            <div class="form-group">
                <label for="pdfLegal">Mentions légales</label>
                <textarea id="pdfLegal" rows="4" data-section="pdf" data-key="legal">${pdf.legal || ''}</textarea>
            </div>
        </div>
    `;
}

function renderCurrencySection() {
    const currency = settings.currency || {};
    return `
        <div class="settings-section">
            <h2>Devise & Formatage</h2>
            <p class="section-subtitle">Configuration de la devise et du formatage des montants</p>
            
            <div class="form-group">
                <label for="currencyCode">Code devise</label>
                <select id="currencyCode" data-section="currency" data-key="code">
                    <option value="MAD" ${currency.code === 'MAD' ? 'selected' : ''}>MAD (Dirham marocain)</option>
                    <option value="EUR" ${currency.code === 'EUR' ? 'selected' : ''}>EUR (Euro)</option>
                    <option value="USD" ${currency.code === 'USD' ? 'selected' : ''}>USD (Dollar)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="currencySymbol">Symbole</label>
                <input type="text" id="currencySymbol" value="${currency.symbol || 'DH'}" data-section="currency" data-key="symbol">
            </div>
            
            <div class="form-group">
                <label for="decimalSeparator">Séparateur décimal</label>
                <select id="decimalSeparator" data-section="currency" data-key="decimal_separator">
                    <option value="." ${currency.decimal_separator === '.' ? 'selected' : ''}>Point (.)</option>
                    <option value="," ${currency.decimal_separator === ',' ? 'selected' : ''}>Virgule (,)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="thousandSeparator">Séparateur de milliers</label>
                <select id="thousandSeparator" data-section="currency" data-key="thousand_separator">
                    <option value=" " ${currency.thousand_separator === ' ' ? 'selected' : ''}>Espace</option>
                    <option value="," ${currency.thousand_separator === ',' ? 'selected' : ''}>Virgule (,)</option>
                    <option value="." ${currency.thousand_separator === '.' ? 'selected' : ''}>Point (.)</option>
                </select>
            </div>
        </div>
    `;
}

function renderTaxSection() {
    return `
        <div class="settings-section">
            <h2>TVA & Fiscalité</h2>
            <p class="section-subtitle">Configuration des taux de TVA par zone</p>
            
            <div class="tax-rates-list" id="taxRatesList">
                <div class="tax-rate-item">
                    <div class="form-group">
                        <label>Zone / Pays</label>
                        <input type="text" value="Maroc" disabled>
                    </div>
                    <div class="form-group">
                        <label>Taux TVA (%)</label>
                        <input type="number" value="20" step="0.1">
                    </div>
                </div>
            </div>
            
            <button class="btn btn-secondary" onclick="addTaxRate()">+ Ajouter une zone</button>
        </div>
    `;
}

function renderDiscountSection() {
    const discount = settings.discount || {};
    return `
        <div class="settings-section">
            <h2>Remises</h2>
            <p class="section-subtitle">Configuration des remises autorisées</p>
            
            <div class="form-group">
                <label for="discountMax">Remise maximale (%)</label>
                <input type="number" id="discountMax" value="${discount.max_percent || '50'}" step="0.1" data-section="discount" data-key="max_percent">
            </div>
            
            <div class="form-group">
                <label for="discountDefault">Remise par défaut (%)</label>
                <input type="number" id="discountDefault" value="${discount.default_percent || '0'}" step="0.1" data-section="discount" data-key="default_percent">
            </div>
            
            <div class="form-group checkbox-group">
                <label>
                    <input type="checkbox" id="discountRequireAuth" ${discount.require_auth === 'true' ? 'checked' : ''} data-section="discount" data-key="require_auth">
                    Exiger une autorisation admin pour les remises > 10%
                </label>
            </div>
        </div>
    `;
}

function renderLaborSection() {
    const labor = settings.labor || {};
    return `
        <div class="settings-section">
            <h2>Main d'œuvre</h2>
            <p class="section-subtitle">Configuration des tarifs de main d'œuvre</p>
            
            <div class="form-group">
                <label for="laborHourlyRate">Tarif horaire (DH)</label>
                <input type="number" id="laborHourlyRate" value="${labor.hourly_rate || '80'}" step="0.01" data-section="labor" data-key="hourly_rate">
            </div>
            
            <div class="form-group">
                <label for="laborFlatRate">Forfait installation (DH)</label>
                <input type="number" id="laborFlatRate" value="${labor.flat_rate || '0'}" step="0.01" data-section="labor" data-key="flat_rate">
            </div>
        </div>
    `;
}

function renderCoefficientsSection() {
    return `
        <div class="settings-section">
            <h2>Coefficients de Finition</h2>
            <p class="section-subtitle">Coefficients multiplicateurs par type de finition</p>
            
            <div id="finishCoefficientsList" class="coefficients-list">
                <p>Chargement...</p>
            </div>
        </div>
    `;
}

function renderCatalogSection() {
    return `
        <div class="settings-section">
            <h2>Catalogue Produits</h2>
            <p class="section-subtitle">Gestion des types de châssis, séries, vitrages, accessoires et finitions</p>
            
            <div class="catalog-tabs">
                <button class="tab-button active" data-tab="chassis">Types de châssis</button>
                <button class="tab-button" data-tab="series">Séries de profilés</button>
                <button class="tab-button" data-tab="glazing">Vitrages</button>
                <button class="tab-button" data-tab="accessories">Accessoires</button>
                <button class="tab-button" data-tab="finishes">Finitions</button>
            </div>
            
            <div id="catalogContent" class="catalog-content">
                <p>Chargement...</p>
            </div>
        </div>
    `;
}

function renderImportSection() {
    return `
        <div class="settings-section">
            <h2>Import / Export CSV</h2>
            <p class="section-subtitle">Importer ou exporter les barèmes de prix</p>
            
            <div class="import-export-box">
                <h3>Importer un barème</h3>
                <p>Format attendu : category, subcategory, unit, price, coefficient</p>
                <input type="file" id="csvFileImport" accept=".csv">
                <button class="btn btn-primary" onclick="importCSV()">Importer</button>
            </div>
            
            <div class="import-export-box">
                <h3>Exporter le barème actuel</h3>
                <button class="btn btn-secondary" onclick="exportCSV()">Télécharger CSV</button>
            </div>
        </div>
    `;
}

function renderUsersSection() {
    return `
        <div class="settings-section">
            <h2>Utilisateurs & Accès</h2>
            <p class="section-subtitle">Gestion des comptes utilisateurs et des rôles</p>
            
            <button class="btn btn-primary" onclick="showUserModal()">+ Nouvel utilisateur</button>
            
            <div id="usersList" class="users-list">
                <p>Chargement...</p>
            </div>
        </div>
    `;
}

function renderThemeSection() {
    const theme = settings.theme || {};
    return `
        <div class="settings-section">
            <h2>Apparence</h2>
            <p class="section-subtitle">Configuration de l'interface utilisateur</p>
            
            <div class="form-group">
                <label>Thème</label>
                <div class="radio-group">
                    <label>
                        <input type="radio" name="theme" value="light" ${theme.mode !== 'dark' ? 'checked' : ''} data-section="theme" data-key="mode">
                        Clair
                    </label>
                    <label>
                        <input type="radio" name="theme" value="dark" ${theme.mode === 'dark' ? 'checked' : ''} data-section="theme" data-key="mode">
                        Sombre
                    </label>
                </div>
            </div>
        </div>
    `;
}

function renderAboutSection() {
    return `
        <div class="settings-section">
            <h2>À propos</h2>
            <p class="section-subtitle">Informations sur l'application</p>
            
            <div class="about-info">
                <p><strong>Application:</strong> Devis Châssis Aluminium</p>
                <p><strong>Version:</strong> 1.0.0</p>
                <p><strong>Description:</strong> Application de gestion de devis pour menuiserie aluminium</p>
                <p><strong>Support:</strong> contact@entreprise.ma</p>
            </div>
        </div>
    `;
}

function attachSectionHandlers(sectionName) {
    const inputs = document.querySelectorAll('input[data-section], textarea[data-section], select[data-section]');
    
    inputs.forEach(input => {
        const handler = () => {
            const section = input.dataset.section;
            const key = input.dataset.key;
            const value = input.type === 'checkbox' ? input.checked.toString() : input.value;
            saveSetting(section, key, value);
        };
        
        if (input.type === 'checkbox' || input.type === 'radio') {
            input.addEventListener('change', handler);
        } else {
            input.addEventListener('blur', handler);
        }
    });
    
    if (sectionName === 'users') {
        loadUsers();
    } else if (sectionName === 'catalog') {
        setupCatalogTabs();
        loadCatalogTab('chassis');
    }
}

async function loadUsers() {
    try {
        const response = await fetch('/api/users', { credentials: 'include' });
        const users = await response.json();
        
        const usersList = document.getElementById('usersList');
        usersList.innerHTML = users.map(user => `
            <div class="user-item">
                <div class="user-info">
                    <strong>${user.full_name || user.username}</strong>
                    <span class="user-role ${user.role}">${user.role === 'admin' ? 'Administrateur' : 'Utilisateur'}</span>
                    <small>${user.email || ''}</small>
                </div>
                <div class="user-actions">
                    ${user.id !== currentUser.id ? `<button class="btn-icon" onclick="deleteUser(${user.id})">🗑️</button>` : ''}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load users:', error);
    }
}

function showUserModal() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>Nouvel utilisateur</h3>
            <form id="newUserForm">
                <div class="form-group">
                    <label for="newUsername">Nom d'utilisateur</label>
                    <input type="text" id="newUsername" required>
                </div>
                <div class="form-group">
                    <label for="newFullName">Nom complet</label>
                    <input type="text" id="newFullName" required>
                </div>
                <div class="form-group">
                    <label for="newEmail">Email</label>
                    <input type="email" id="newEmail" required>
                </div>
                <div class="form-group">
                    <label for="newPassword">Mot de passe</label>
                    <input type="password" id="newPassword" required>
                </div>
                <div class="form-group">
                    <label for="newRole">Rôle</label>
                    <select id="newRole" required>
                        <option value="user">Utilisateur</option>
                        <option value="admin">Administrateur</option>
                    </select>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeUserModal()">Annuler</button>
                    <button type="submit" class="btn btn-primary">Créer</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    document.getElementById('newUserForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('newUsername').value;
        const full_name = document.getElementById('newFullName').value;
        const email = document.getElementById('newEmail').value;
        const password = document.getElementById('newPassword').value;
        const role = document.getElementById('newRole').value;
        
        try {
            const response = await fetch('/api/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, full_name, email, password, role }),
                credentials: 'include'
            });
            
            if (response.ok) {
                showToast('Utilisateur créé avec succès', 'success');
                closeUserModal();
                loadUsers();
            } else {
                const error = await response.json();
                showToast(error.error || 'Erreur lors de la création', 'error');
            }
        } catch (error) {
            showToast('Erreur de connexion', 'error');
        }
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeUserModal();
    });
}

function closeUserModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) modal.remove();
}

async function deleteUser(userId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ?')) return;
    
    try {
        const response = await fetch(`/api/users/${userId}`, { method: 'DELETE', credentials: 'include' });
        
        if (response.ok) {
            showToast('Utilisateur supprimé', 'success');
            loadUsers();
        } else {
            const error = await response.json();
            showToast(error.error || 'Erreur lors de la suppression', 'error');
        }
    } catch (error) {
        showToast('Erreur de connexion', 'error');
    }
}

function setupCatalogTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadCatalogTab(btn.dataset.tab);
        });
    });
}

async function loadCatalogTab(tabName) {
    const content = document.getElementById('catalogContent');
    content.innerHTML = '<p>Chargement...</p>';
    
    const apiMap = {
        'chassis': '/api/catalog/chassis-types',
        'series': '/api/catalog/profile-series',
        'glazing': '/api/catalog/glazing-types',
        'accessories': '/api/catalog/accessories',
        'finishes': '/api/catalog/finishes'
    };
    
    const renderMap = {
        'chassis': renderChassisTab,
        'series': renderSeriesTab,
        'glazing': renderGlazingTab,
        'accessories': renderAccessoriesTab,
        'finishes': renderFinishesTab
    };
    
    try {
        const response = await fetch(apiMap[tabName], { credentials: 'include' });
        const data = await response.json();
        renderMap[tabName](data);
    } catch (error) {
        content.innerHTML = '<p>Erreur de chargement</p>';
        console.error('Failed to load catalog tab:', error);
    }
}

function renderChassisTab(items) {
    const content = document.getElementById('catalogContent');
    content.innerHTML = `
        <div class="catalog-header">
            <h3>Types de châssis (${items.length})</h3>
            <button class="btn btn-primary" onclick="showAddModal('chassis')">+ Ajouter</button>
        </div>
        <div class="catalog-list">
            ${items.map(item => `
                <div class="catalog-item">
                    <div class="catalog-item-info">
                        <h4>${item.name}</h4>
                        <p>${item.description || ''}</p>
                        <small>Dimensions: ${item.min_width}×${item.min_height} - ${item.max_width}×${item.max_height} mm</small>
                    </div>
                    <div class="catalog-item-actions">
                        <button class="btn-secondary" onclick="editCatalogItem('chassis', ${item.id})">Modifier</button>
                        <button class="btn-danger" onclick="deleteCatalogItem('chassis', ${item.id})">Supprimer</button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function renderSeriesTab(items) {
    const content = document.getElementById('catalogContent');
    content.innerHTML = `
        <div class="catalog-header">
            <h3>Séries de profilés (${items.length})</h3>
            <button class="btn btn-primary" onclick="showAddModal('series')">+ Ajouter</button>
        </div>
        <div class="catalog-list">
            ${items.map(item => `
                <div class="catalog-item">
                    <div class="catalog-item-info">
                        <h4>${item.name}</h4>
                        <p>${item.description || ''}</p>
                        <small>Prix: ${item.price_per_meter} DH/m</small>
                    </div>
                    <div class="catalog-item-actions">
                        <button class="btn-secondary" onclick="editCatalogItem('series', ${item.id})">Modifier</button>
                        <button class="btn-danger" onclick="deleteCatalogItem('series', ${item.id})">Supprimer</button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function renderGlazingTab(items) {
    const content = document.getElementById('catalogContent');
    content.innerHTML = `
        <div class="catalog-header">
            <h3>Types de vitrage (${items.length})</h3>
            <button class="btn btn-primary" onclick="showAddModal('glazing')">+ Ajouter</button>
        </div>
        <div class="catalog-list">
            ${items.map(item => `
                <div class="catalog-item">
                    <div class="catalog-item-info">
                        <h4>${item.name}</h4>
                        <p>${item.description || ''}</p>
                        <small>Prix: ${item.price_per_m2} DH/m²</small>
                    </div>
                    <div class="catalog-item-actions">
                        <button class="btn-secondary" onclick="editCatalogItem('glazing', ${item.id})">Modifier</button>
                        <button class="btn-danger" onclick="deleteCatalogItem('glazing', ${item.id})">Supprimer</button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function renderAccessoriesTab(items) {
    const content = document.getElementById('catalogContent');
    content.innerHTML = `
        <div class="catalog-header">
            <h3>Accessoires (${items.length})</h3>
            <button class="btn btn-primary" onclick="showAddModal('accessories')">+ Ajouter</button>
        </div>
        <div class="catalog-list">
            ${items.map(item => `
                <div class="catalog-item">
                    <div class="catalog-item-info">
                        <h4>${item.name}</h4>
                        <small>Prix: ${item.unit_price} DH</small>
                    </div>
                    <div class="catalog-item-actions">
                        <button class="btn-secondary" onclick="editCatalogItem('accessories', ${item.id})">Modifier</button>
                        <button class="btn-danger" onclick="deleteCatalogItem('accessories', ${item.id})">Supprimer</button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function renderFinishesTab(items) {
    const content = document.getElementById('catalogContent');
    content.innerHTML = `
        <div class="catalog-header">
            <h3>Finitions (${items.length})</h3>
            <button class="btn btn-primary" onclick="showAddModal('finishes')">+ Ajouter</button>
        </div>
        <div class="catalog-list">
            ${items.map(item => `
                <div class="catalog-item">
                    <div class="catalog-item-info">
                        <h4>${item.name}</h4>
                        <p>${item.description || ''}</p>
                        <small>Coefficient: ${item.price_coefficient}</small>
                    </div>
                    <div class="catalog-item-actions">
                        <button class="btn-secondary" onclick="editCatalogItem('finishes', ${item.id})">Modifier</button>
                        <button class="btn-danger" onclick="deleteCatalogItem('finishes', ${item.id})">Supprimer</button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

async function deleteCatalogItem(type, id) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) return;
    
    const apiMap = {
        'chassis': '/api/catalog/chassis-types',
        'series': '/api/catalog/profile-series',
        'glazing': '/api/catalog/glazing-types',
        'accessories': '/api/catalog/accessories',
        'finishes': '/api/catalog/finishes'
    };
    
    try {
        const response = await fetch(`${apiMap[type]}/${id}`, { method: 'DELETE', credentials: 'include' });
        
        if (response.ok) {
            showToast('Élément supprimé', 'success');
            loadCatalogTab(type);
        } else {
            const error = await response.json();
            showToast(error.error || 'Erreur lors de la suppression', 'error');
        }
    } catch (error) {
        showToast('Erreur de connexion', 'error');
    }
}

async function showAddModal(type) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'catalogModal';
    
    const forms = {
        chassis: `
            <div class="form-group">
                <label>Nom *</label>
                <input type="text" id="itemName" required>
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea id="itemDescription" rows="2"></textarea>
            </div>
            <div class="form-group">
                <label>Largeur min (mm) *</label>
                <input type="number" id="itemMinWidth" required>
            </div>
            <div class="form-group">
                <label>Largeur max (mm) *</label>
                <input type="number" id="itemMaxWidth" required>
            </div>
            <div class="form-group">
                <label>Hauteur min (mm) *</label>
                <input type="number" id="itemMinHeight" required>
            </div>
            <div class="form-group">
                <label>Hauteur max (mm) *</label>
                <input type="number" id="itemMaxHeight" required>
            </div>
        `,
        series: `
            <div class="form-group">
                <label>Nom *</label>
                <input type="text" id="itemName" required>
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea id="itemDescription" rows="2"></textarea>
            </div>
            <div class="form-group">
                <label>Prix par mètre (MAD) *</label>
                <input type="number" id="itemPricePerMeter" step="0.01" required>
            </div>
        `,
        glazing: `
            <div class="form-group">
                <label>Nom *</label>
                <input type="text" id="itemName" required>
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea id="itemDescription" rows="2"></textarea>
            </div>
            <div class="form-group">
                <label>Épaisseur (mm)</label>
                <input type="number" id="itemThickness">
            </div>
            <div class="form-group">
                <label>Prix par m² (MAD) *</label>
                <input type="number" id="itemPricePerM2" step="0.01" required>
            </div>
        `,
        accessories: `
            <div class="form-group">
                <label>Nom *</label>
                <input type="text" id="itemName" required>
            </div>
            <div class="form-group">
                <label>Prix unitaire (MAD) *</label>
                <input type="number" id="itemUnitPrice" step="0.01" required>
            </div>
            <div class="form-group">
                <label>Incompatible avec (série)</label>
                <input type="text" id="itemIncompatibleSeries" placeholder="Ex: Série Premium">
            </div>
        `,
        finishes: `
            <div class="form-group">
                <label>Nom *</label>
                <input type="text" id="itemName" required>
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea id="itemDescription" rows="2"></textarea>
            </div>
            <div class="form-group">
                <label>Coefficient de prix *</label>
                <input type="number" id="itemPriceCoefficient" step="0.01" value="1.0" required>
            </div>
        `
    };
    
    modal.innerHTML = `
        <div class="modal-content">
            <h3>Ajouter un élément</h3>
            <form id="catalogForm">
                ${forms[type]}
                <div class="modal-actions">
                    <button type="button" class="btn-secondary" onclick="closeModal()">Annuler</button>
                    <button type="submit" class="btn-primary">Ajouter</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    document.getElementById('catalogForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await saveCatalogItem(type, null);
    });
}

async function editCatalogItem(type, id) {
    const apiMap = {
        'chassis': '/api/catalog/chassis-types',
        'series': '/api/catalog/profile-series',
        'glazing': '/api/catalog/glazing-types',
        'accessories': '/api/catalog/accessories',
        'finishes': '/api/catalog/finishes'
    };
    
    try {
        const response = await fetch(`${apiMap[type]}/${id}`, { credentials: 'include' });
        if (!response.ok) {
            const items = await fetch(apiMap[type], { credentials: 'include' }).then(r => r.json());
            const item = items.find(i => i.id === id);
            if (!item) throw new Error('Item not found');
            showEditModal(type, item);
            return;
        }
        const item = await response.json();
        showEditModal(type, item);
    } catch (error) {
        showToast('Erreur de chargement', 'error');
    }
}

function showEditModal(type, item) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'catalogModal';
    
    const forms = {
        chassis: `
            <div class="form-group">
                <label>Nom *</label>
                <input type="text" id="itemName" value="${item.name || ''}" required>
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea id="itemDescription" rows="2">${item.description || ''}</textarea>
            </div>
            <div class="form-group">
                <label>Largeur min (mm) *</label>
                <input type="number" id="itemMinWidth" value="${item.min_width}" required>
            </div>
            <div class="form-group">
                <label>Largeur max (mm) *</label>
                <input type="number" id="itemMaxWidth" value="${item.max_width}" required>
            </div>
            <div class="form-group">
                <label>Hauteur min (mm) *</label>
                <input type="number" id="itemMinHeight" value="${item.min_height}" required>
            </div>
            <div class="form-group">
                <label>Hauteur max (mm) *</label>
                <input type="number" id="itemMaxHeight" value="${item.max_height}" required>
            </div>
        `,
        series: `
            <div class="form-group">
                <label>Nom *</label>
                <input type="text" id="itemName" value="${item.name || ''}" required>
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea id="itemDescription" rows="2">${item.description || ''}</textarea>
            </div>
            <div class="form-group">
                <label>Prix par mètre (MAD) *</label>
                <input type="number" id="itemPricePerMeter" value="${item.price_per_meter}" step="0.01" required>
            </div>
        `,
        glazing: `
            <div class="form-group">
                <label>Nom *</label>
                <input type="text" id="itemName" value="${item.name || ''}" required>
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea id="itemDescription" rows="2">${item.description || ''}</textarea>
            </div>
            <div class="form-group">
                <label>Épaisseur (mm)</label>
                <input type="number" id="itemThickness" value="${item.thickness_mm || ''}">
            </div>
            <div class="form-group">
                <label>Prix par m² (MAD) *</label>
                <input type="number" id="itemPricePerM2" value="${item.price_per_m2}" step="0.01" required>
            </div>
        `,
        accessories: `
            <div class="form-group">
                <label>Nom *</label>
                <input type="text" id="itemName" value="${item.name || ''}" required>
            </div>
            <div class="form-group">
                <label>Prix unitaire (MAD) *</label>
                <input type="number" id="itemUnitPrice" value="${item.unit_price}" step="0.01" required>
            </div>
            <div class="form-group">
                <label>Incompatible avec (série)</label>
                <input type="text" id="itemIncompatibleSeries" value="${item.incompatible_series || ''}" placeholder="Ex: Série Premium">
            </div>
        `,
        finishes: `
            <div class="form-group">
                <label>Nom *</label>
                <input type="text" id="itemName" value="${item.name || ''}" required>
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea id="itemDescription" rows="2">${item.description || ''}</textarea>
            </div>
            <div class="form-group">
                <label>Coefficient de prix *</label>
                <input type="number" id="itemPriceCoefficient" value="${item.price_coefficient}" step="0.01" required>
            </div>
        `
    };
    
    modal.innerHTML = `
        <div class="modal-content">
            <h3>Modifier l'élément</h3>
            <form id="catalogForm">
                ${forms[type]}
                <div class="modal-actions">
                    <button type="button" class="btn-secondary" onclick="closeModal()">Annuler</button>
                    <button type="submit" class="btn-primary">Enregistrer</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    document.getElementById('catalogForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await saveCatalogItem(type, item.id);
    });
}

async function saveCatalogItem(type, id) {
    const apiMap = {
        'chassis': '/api/catalog/chassis-types',
        'series': '/api/catalog/profile-series',
        'glazing': '/api/catalog/glazing-types',
        'accessories': '/api/catalog/accessories',
        'finishes': '/api/catalog/finishes'
    };
    
    const dataBuilders = {
        chassis: () => ({
            name: document.getElementById('itemName').value,
            description: document.getElementById('itemDescription').value,
            min_width: parseInt(document.getElementById('itemMinWidth').value),
            max_width: parseInt(document.getElementById('itemMaxWidth').value),
            min_height: parseInt(document.getElementById('itemMinHeight').value),
            max_height: parseInt(document.getElementById('itemMaxHeight').value)
        }),
        series: () => ({
            name: document.getElementById('itemName').value,
            description: document.getElementById('itemDescription').value,
            price_per_meter: parseFloat(document.getElementById('itemPricePerMeter').value)
        }),
        glazing: () => ({
            name: document.getElementById('itemName').value,
            description: document.getElementById('itemDescription').value,
            thickness_mm: parseInt(document.getElementById('itemThickness').value) || null,
            price_per_m2: parseFloat(document.getElementById('itemPricePerM2').value)
        }),
        accessories: () => ({
            name: document.getElementById('itemName').value,
            unit_price: parseFloat(document.getElementById('itemUnitPrice').value),
            incompatible_series: document.getElementById('itemIncompatibleSeries').value || null
        }),
        finishes: () => ({
            name: document.getElementById('itemName').value,
            description: document.getElementById('itemDescription').value,
            price_coefficient: parseFloat(document.getElementById('itemPriceCoefficient').value)
        })
    };
    
    const data = dataBuilders[type]();
    const url = id ? `${apiMap[type]}/${id}` : apiMap[type];
    const method = id ? 'PUT' : 'POST';
    
    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
            credentials: 'include'
        });
        
        if (response.ok) {
            showToast(id ? 'Élément modifié' : 'Élément ajouté', 'success');
            closeModal();
            loadCatalogTab(type);
        } else {
            const error = await response.json();
            showToast(error.error || 'Erreur lors de la sauvegarde', 'error');
        }
    } catch (error) {
        showToast('Erreur de connexion', 'error');
    }
}

function closeModal() {
    const modal = document.getElementById('catalogModal');
    if (modal) modal.remove();
}

document.addEventListener('DOMContentLoaded', async () => {
    if (!await checkAuth()) return;
    
    await loadSettings();
    showSection('company');
    
    document.querySelectorAll('.settings-menu-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.settings-menu-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            showSection(item.dataset.section);
        });
    });
    
    document.getElementById('backBtn').addEventListener('click', () => {
        window.location.href = '/';
    });
    
    document.getElementById('logoutBtn').addEventListener('click', async () => {
        await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
        window.location.href = '/login.html';
    });
});
