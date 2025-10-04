let companies = [];
let currentFilter = 'all';

async function checkAuth() {
    try {
        const response = await fetch('/api/auth/check', { credentials: 'include' });
        const data = await response.json();
        
        if (!data.authenticated || data.user.role !== 'super_admin') {
            window.location.href = '/login.html';
            return false;
        }
        
        document.getElementById('welcomeText').textContent = `Bienvenue, ${data.user.full_name || data.user.username}`;
        return true;
    } catch (error) {
        console.error('Auth check error:', error);
        window.location.href = '/login.html';
        return false;
    }
}

async function loadStats() {
    try {
        const response = await fetch('/api/super-admin/stats', { credentials: 'include' });
        const stats = await response.json();
        
        document.getElementById('totalCompanies').textContent = stats.total_companies;
        document.getElementById('activeCompanies').textContent = stats.active_companies;
        document.getElementById('pendingCompanies').textContent = stats.pending_companies;
        document.getElementById('suspendedCompanies').textContent = stats.suspended_companies;
        document.getElementById('totalUsers').textContent = stats.total_users;
        document.getElementById('totalAdmins').textContent = stats.total_admins;
        document.getElementById('totalQuotes').textContent = stats.total_quotes;
        document.getElementById('totalAmount').textContent = formatCurrency(stats.total_amount);
        document.getElementById('monthQuotes').textContent = stats.month_quotes;
        document.getElementById('monthAmount').textContent = formatCurrency(stats.month_amount);
        document.getElementById('weekQuotes').textContent = stats.week_quotes;
        document.getElementById('weekAmount').textContent = formatCurrency(stats.week_amount);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('fr-MA', {
        style: 'currency',
        currency: 'MAD'
    }).format(amount || 0);
}

async function loadCompanies() {
    try {
        const response = await fetch('/api/super-admin/companies', { credentials: 'include' });
        companies = await response.json();
        renderCompanies();
    } catch (error) {
        console.error('Error loading companies:', error);
        document.getElementById('companiesTableBody').innerHTML = '<tr><td colspan="8" style="text-align: center; color: red;">Erreur de chargement</td></tr>';
    }
}

function renderCompanies() {
    const tbody = document.getElementById('companiesTableBody');
    
    let filteredCompanies = companies;
    if (currentFilter !== 'all') {
        filteredCompanies = companies.filter(c => c.status === currentFilter);
    }
    
    if (filteredCompanies.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">Aucune entreprise trouvée</td></tr>';
        return;
    }
    
    tbody.innerHTML = filteredCompanies.map(company => {
        const statusColors = {
            'approved': 'green',
            'pending': 'orange',
            'suspended': 'red',
            'rejected': 'gray'
        };
        
        const statusLabels = {
            'approved': 'Actif',
            'pending': 'En attente',
            'suspended': 'Suspendu',
            'rejected': 'Rejeté'
        };
        
        const statusColor = statusColors[company.status] || 'black';
        const statusLabel = statusLabels[company.status] || company.status;
        
        let actions = '';
        if (company.status === 'pending') {
            actions = `
                <button class="btn-primary" onclick="approveCompany(${company.id})">Approuver</button>
                <button class="btn-danger" onclick="rejectCompany(${company.id})">Rejeter</button>
            `;
        } else if (company.status === 'approved') {
            actions = `<button class="btn-danger" onclick="suspendCompany(${company.id})">Suspendre</button>`;
        } else if (company.status === 'suspended') {
            actions = `<button class="btn-primary" onclick="activateCompany(${company.id})">Activer</button>`;
        }
        
        return `
            <tr>
                <td>${company.id}</td>
                <td><strong>${company.name}</strong></td>
                <td><span style="color: ${statusColor}; font-weight: bold;">${statusLabel}</span></td>
                <td>${company.admin_count || 0}</td>
                <td>${company.user_count || 0}</td>
                <td>${company.quote_count || 0}</td>
                <td>${new Date(company.created_at).toLocaleDateString('fr-FR')}</td>
                <td>${actions}</td>
            </tr>
        `;
    }).join('');
}

async function approveCompany(companyId) {
    if (!confirm('Voulez-vous vraiment approuver cette entreprise ?')) return;
    
    try {
        const response = await fetch(`/api/super-admin/companies/${companyId}/approve`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            alert('Entreprise approuvée avec succès');
            await loadCompanies();
            await loadStats();
        } else {
            const error = await response.json();
            alert('Erreur: ' + (error.error || 'Impossible d\'approuver l\'entreprise'));
        }
    } catch (error) {
        console.error('Error approving company:', error);
        alert('Erreur lors de l\'approbation');
    }
}

async function rejectCompany(companyId) {
    if (!confirm('Voulez-vous vraiment rejeter cette entreprise ?')) return;
    
    try {
        const response = await fetch(`/api/super-admin/companies/${companyId}/reject`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            alert('Entreprise rejetée');
            await loadCompanies();
            await loadStats();
        } else {
            alert('Erreur lors du rejet');
        }
    } catch (error) {
        console.error('Error rejecting company:', error);
        alert('Erreur lors du rejet');
    }
}

async function suspendCompany(companyId) {
    if (!confirm('Voulez-vous vraiment suspendre cette entreprise ? Tous les utilisateurs seront désactivés.')) return;
    
    try {
        const response = await fetch(`/api/super-admin/companies/${companyId}/deactivate`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            alert('Entreprise suspendue');
            await loadCompanies();
            await loadStats();
        } else {
            alert('Erreur lors de la suspension');
        }
    } catch (error) {
        console.error('Error suspending company:', error);
        alert('Erreur lors de la suspension');
    }
}

async function activateCompany(companyId) {
    if (!confirm('Voulez-vous vraiment réactiver cette entreprise ?')) return;
    
    try {
        const response = await fetch(`/api/super-admin/companies/${companyId}/activate`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            alert('Entreprise activée');
            await loadCompanies();
            await loadStats();
        } else {
            alert('Erreur lors de l\'activation');
        }
    } catch (error) {
        console.error('Error activating company:', error);
        alert('Erreur lors de l\'activation');
    }
}

document.getElementById('logoutBtn').addEventListener('click', async () => {
    try {
        await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
        window.location.href = '/login.html';
    } catch (error) {
        console.error('Logout error:', error);
    }
});

document.querySelectorAll('.filter-buttons button').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.filter-buttons button').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentFilter = e.target.dataset.filter;
        renderCompanies();
    });
});

// Add Company Modal
let currentStep = 1;

document.getElementById('addCompanyBtn').addEventListener('click', () => {
    document.getElementById('addCompanyForm').reset();
    showStep(1);
    document.getElementById('addCompanyModal').style.display = 'flex';
});

document.getElementById('closeAddCompanyModal').addEventListener('click', () => {
    document.getElementById('addCompanyModal').style.display = 'none';
});

document.getElementById('cancelAddCompanyBtn').addEventListener('click', () => {
    document.getElementById('addCompanyModal').style.display = 'none';
});

document.getElementById('nextToStep2').addEventListener('click', () => {
    const companyName = document.getElementById('companyName').value;
    if (!companyName.trim()) {
        alert('Veuillez saisir le nom de l\'entreprise');
        return;
    }
    showStep(2);
});

document.getElementById('backToStep1').addEventListener('click', () => {
    showStep(1);
});

function showStep(step) {
    currentStep = step;
    
    document.querySelectorAll('.form-step').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
    
    document.getElementById(`step${step}`).classList.add('active');
    document.querySelector(`.step[data-step="${step}"]`).classList.add('active');
}

document.getElementById('addCompanyForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const data = {
        company_name: document.getElementById('companyName').value,
        company_address: document.getElementById('companyAddress').value,
        company_phone: document.getElementById('companyPhone').value,
        company_email: document.getElementById('companyEmail').value,
        company_ice: document.getElementById('companyICE').value,
        admin_username: document.getElementById('adminUsername').value,
        admin_full_name: document.getElementById('adminFullName').value,
        admin_email: document.getElementById('adminEmail').value,
        admin_password: document.getElementById('adminPassword').value
    };
    
    try {
        const response = await fetch('/api/super-admin/companies/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
            credentials: 'include'
        });
        
        if (response.ok) {
            alert('Entreprise et administrateur créés avec succès');
            document.getElementById('addCompanyModal').style.display = 'none';
            await loadStats();
            await loadCompanies();
        } else {
            const error = await response.json();
            alert(error.error || 'Erreur lors de la création');
        }
    } catch (error) {
        console.error('Error creating company:', error);
        alert('Erreur lors de la création');
    }
});

// Close modals on outside click
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});

// App Settings
let appSettings = {};

async function loadAppSettings() {
    try {
        const response = await fetch('/api/super-admin/app-settings', { credentials: 'include' });
        const settings = await response.json();
        
        appSettings = {};
        settings.forEach(s => {
            appSettings[s.key] = s.value;
        });
        
        document.getElementById('appName').value = appSettings.app_name || '';
        document.getElementById('appVersion').value = appSettings.app_version || '';
        document.getElementById('appDescription').value = appSettings.app_description || '';
        document.getElementById('githubRepo').value = appSettings.github_repo || '';
        document.getElementById('autoUpdateEnabled').checked = appSettings.auto_update_enabled === 'true';
        document.getElementById('appTitle').value = appSettings.app_title || '';
        document.getElementById('dashboardTitle').value = appSettings.dashboard_title || '';
        document.getElementById('quoteTitle').value = appSettings.quote_title || '';
        document.getElementById('loginTitle').value = appSettings.login_title || '';
        document.getElementById('welcomeMessage').value = appSettings.welcome_message || '';
        document.getElementById('sendgridFromName').value = appSettings.sendgrid_from_name || '';
    } catch (error) {
        console.error('Error loading app settings:', error);
    }
}

const saveAppSettingsBtn = document.getElementById('saveAppSettings');
if (saveAppSettingsBtn) {
    saveAppSettingsBtn.addEventListener('click', async () => {
    const data = {
        app_name: document.getElementById('appName').value,
        app_version: document.getElementById('appVersion').value,
        app_description: document.getElementById('appDescription').value,
        github_repo: document.getElementById('githubRepo').value,
        auto_update_enabled: document.getElementById('autoUpdateEnabled').checked ? 'true' : 'false',
        app_title: document.getElementById('appTitle').value,
        dashboard_title: document.getElementById('dashboardTitle').value,
        quote_title: document.getElementById('quoteTitle').value,
        login_title: document.getElementById('loginTitle').value,
        welcome_message: document.getElementById('welcomeMessage').value,
        sendgrid_from_name: document.getElementById('sendgridFromName').value
    };
    
    try {
        const response = await fetch('/api/super-admin/app-settings', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
            credentials: 'include'
        });
        
        if (response.ok) {
            alert('✅ Tous les paramètres SAAS ont été sauvegardés avec succès');
            await loadAppSettings();
        } else {
            alert('❌ Erreur lors de la sauvegarde');
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        alert('❌ Erreur lors de la sauvegarde');
    }
    });
}

const checkUpdatesBtn = document.getElementById('checkUpdates');
if (checkUpdatesBtn) {
    checkUpdatesBtn.addEventListener('click', async () => {
        const repo = document.getElementById('githubRepo').value;
        if (!repo) {
            alert('⚠️ Veuillez d\'abord configurer le repository GitHub');
            return;
        }
        
        alert('🔄 Fonction de mise à jour en cours de développement. Vérifiez manuellement sur: ' + repo);
    });
}

// Activity Logs
let currentPage = 1;
let totalPages = 1;
let usersMap = {};

async function loadActivityLogs(page = 1) {
    try {
        const response = await fetch(`/api/super-admin/activity-logs?page=${page}&per_page=20`, { credentials: 'include' });
        const data = await response.json();
        
        currentPage = page;
        totalPages = data.pages;
        
        const companiesResponse = await fetch('/api/super-admin/companies', { credentials: 'include' });
        const companies = await companiesResponse.json();
        
        companies.forEach(company => {
            if (company.users) {
                company.users.forEach(user => {
                    usersMap[user.id] = user.full_name || user.username;
                });
            }
        });
        
        renderActivityLogs(data.logs);
        updatePagination();
    } catch (error) {
        console.error('Error loading logs:', error);
        document.getElementById('logsTableBody').innerHTML = '<tr><td colspan="5" style="text-align: center; color: red;">Erreur de chargement</td></tr>';
    }
}

function renderActivityLogs(logs) {
    const tbody = document.getElementById('logsTableBody');
    
    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Aucun log trouvé</td></tr>';
        return;
    }
    
    tbody.innerHTML = logs.map(log => {
        const date = new Date(log.created_at);
        const userName = log.user_id ? (usersMap[log.user_id] || 'Utilisateur #' + log.user_id) : 'Système';
        
        return `
            <tr>
                <td>${date.toLocaleString('fr-FR')}</td>
                <td>${userName}</td>
                <td><strong>${log.action}</strong></td>
                <td>${log.description || '-'}</td>
                <td>${log.ip_address || '-'}</td>
            </tr>
        `;
    }).join('');
}

function updatePagination() {
    const pageInfo = document.getElementById('pageInfo');
    const prevPage = document.getElementById('prevPage');
    const nextPage = document.getElementById('nextPage');
    
    if (pageInfo) pageInfo.textContent = `Page ${currentPage} / ${totalPages}`;
    if (prevPage) prevPage.disabled = currentPage <= 1;
    if (nextPage) nextPage.disabled = currentPage >= totalPages;
}

const prevPageBtn = document.getElementById('prevPage');
if (prevPageBtn) {
    prevPageBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            loadActivityLogs(currentPage - 1);
        }
    });
}

const nextPageBtn = document.getElementById('nextPage');
if (nextPageBtn) {
    nextPageBtn.addEventListener('click', () => {
        if (currentPage < totalPages) {
            loadActivityLogs(currentPage + 1);
        }
    });
}

// Sidebar Management
const sidebar = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebarOverlay');
const hamburgerBtn = document.getElementById('hamburgerBtn');
const closeSidebar = document.getElementById('closeSidebar');

function openSidebar() {
    sidebar.classList.add('active');
    sidebarOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeSidebarMenu() {
    sidebar.classList.remove('active');
    sidebarOverlay.classList.remove('active');
    document.body.style.overflow = '';
}

hamburgerBtn.addEventListener('click', openSidebar);
closeSidebar.addEventListener('click', closeSidebarMenu);
sidebarOverlay.addEventListener('click', closeSidebarMenu);

// Sidebar Navigation
const navItems = document.querySelectorAll('.nav-item');
const sidebarSections = document.querySelectorAll('.sidebar-section');

navItems.forEach(item => {
    item.addEventListener('click', () => {
        const sectionId = item.dataset.section;
        
        navItems.forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');
        
        sidebarSections.forEach(section => section.classList.remove('active'));
        document.getElementById(`section-${sectionId}`).classList.add('active');
        
        if (sectionId === 'activity-logs') {
            loadActivityLogs(1);
        }
    });
});

// Profile Management
async function loadProfile() {
    try {
        const response = await fetch('/api/super-admin/profile', { credentials: 'include' });
        const profile = await response.json();
        
        document.getElementById('profileUsername').value = profile.username;
        document.getElementById('profileFullName').value = profile.full_name;
        document.getElementById('profileEmail').value = profile.email || '';
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

const saveProfileBtn = document.getElementById('saveProfile');
if (saveProfileBtn) {
    saveProfileBtn.addEventListener('click', async () => {
        const data = {
            full_name: document.getElementById('profileFullName').value,
            email: document.getElementById('profileEmail').value,
            password: document.getElementById('profilePassword').value
        };
        
        try {
            const response = await fetch('/api/super-admin/profile', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
                credentials: 'include'
            });
            
            if (response.ok) {
                alert('✅ Profil mis à jour avec succès');
                document.getElementById('profilePassword').value = '';
            } else {
                alert('❌ Erreur lors de la mise à jour');
            }
        } catch (error) {
            console.error('Error updating profile:', error);
            alert('❌ Erreur lors de la mise à jour');
        }
    });
}

// Language Management
async function loadAvailableLanguages() {
    try {
        const response = await fetch('/api/languages/available', { credentials: 'include' });
        const languages = await response.json();
        
        const container = document.getElementById('availableLanguages');
        if (languages.length === 0) {
            container.innerHTML = '<p style="color: #666;">Aucune langue disponible</p>';
            return;
        }
        
        container.innerHTML = languages.map(lang => `
            <div style="display: inline-block; padding: 6px 12px; background: #f0f9ff; border: 1px solid #3B82F6; border-radius: 6px; margin-right: 8px; margin-bottom: 8px;">
                <span style="font-weight: 500;">${lang.name}</span>
                <span style="color: #666; margin-left: 4px;">(${lang.code})</span>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading languages:', error);
    }
}

const uploadLanguageBtn = document.getElementById('uploadLanguageBtn');
if (uploadLanguageBtn) {
    uploadLanguageBtn.addEventListener('click', async () => {
        const fileInput = document.getElementById('languageFileInput');
        const file = fileInput.files[0];
        
        if (!file) {
            alert('⚠️ Veuillez sélectionner un fichier JSON');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            uploadLanguageBtn.disabled = true;
            uploadLanguageBtn.textContent = '⏳ Upload...';
            
            const response = await fetch('/api/languages/upload', {
                method: 'POST',
                body: formData,
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                alert(`✅ ${data.message}`);
                fileInput.value = '';
                await loadAvailableLanguages();
            } else {
                alert(`❌ Erreur: ${data.error}`);
            }
        } catch (error) {
            console.error('Error uploading language:', error);
            alert('❌ Erreur lors de l\'upload du fichier');
        } finally {
            uploadLanguageBtn.disabled = false;
            uploadLanguageBtn.textContent = '📤 Uploader';
        }
    });
}

// ===== Backup Functions =====
async function loadBackups() {
    try {
        const response = await fetch('/api/super-admin/backup/list', { credentials: 'include' });
        const data = await response.json();
        
        if (data.success) {
            renderBackupStats(data.stats);
            renderBackupsTable(data.backups);
        }
    } catch (error) {
        console.error('Error loading backups:', error);
    }
}

function renderBackupStats(stats) {
    const statsDiv = document.getElementById('backupStats');
    statsDiv.innerHTML = `
        <p><strong>Total sauvegardes:</strong> ${stats.total_backups}</p>
        <p><strong>Réussies:</strong> <span style="color: #10B981;">${stats.successful}</span></p>
        <p><strong>Échouées:</strong> <span style="color: #EF4444;">${stats.failed}</span></p>
        <p><strong>Taille totale:</strong> ${stats.total_size_mb} MB</p>
        ${stats.latest_backup ? `<p><strong>Dernière sauvegarde:</strong> ${new Date(stats.latest_backup.datetime).toLocaleString()}</p>` : ''}
    `;
}

function renderBackupsTable(backups) {
    const tbody = document.getElementById('backupsTableBody');
    
    if (backups.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Aucune sauvegarde</td></tr>';
        return;
    }
    
    tbody.innerHTML = backups.map(backup => `
        <tr>
            <td>${new Date(backup.datetime).toLocaleString()}</td>
            <td>${backup.description || 'N/A'}</td>
            <td>${backup.database_type || 'N/A'}</td>
            <td>${backup.size ? (backup.size / 1024 / 1024).toFixed(2) + ' MB' : 'N/A'}</td>
            <td>${backup.success ? '<span style="color: #10B981;">✓ Réussie</span>' : '<span style="color: #EF4444;">✗ Échouée</span>'}</td>
            <td>
                ${backup.success ? `<button class="btn-secondary" onclick="restoreBackup('${backup.files[0]}')">♻️ Restaurer</button>` : ''}
            </td>
        </tr>
    `).join('');
}

async function createBackup() {
    const description = prompt('Description de cette sauvegarde (optionnel):', 'Backup manuel');
    if (description === null) return;
    
    try {
        const createBtn = document.getElementById('createBackupBtn');
        createBtn.disabled = true;
        createBtn.textContent = '⏳ Création...';
        
        const response = await fetch('/api/super-admin/backup/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ description }),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ Sauvegarde créée avec succès!');
            await loadBackups();
        } else {
            alert('❌ Erreur: ' + data.error);
        }
    } catch (error) {
        console.error('Error creating backup:', error);
        alert('❌ Erreur lors de la création de la sauvegarde');
    } finally {
        const createBtn = document.getElementById('createBackupBtn');
        createBtn.disabled = false;
        createBtn.textContent = '💾 Créer une sauvegarde';
    }
}

async function restoreBackup(backupFile) {
    if (!confirm('⚠️ ATTENTION: Cette opération va restaurer la base de données. Une sauvegarde sera créée avant. Continuer?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/super-admin/backup/restore', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ backup_file: backupFile }),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ Base de données restaurée avec succès! Rechargez la page.');
            location.reload();
        } else {
            alert('❌ Erreur: ' + data.error);
        }
    } catch (error) {
        console.error('Error restoring backup:', error);
        alert('❌ Erreur lors de la restauration');
    }
}

// ===== Update Functions =====
async function checkForUpdates() {
    try {
        const checkBtn = document.getElementById('checkUpdatesBtn');
        checkBtn.disabled = true;
        checkBtn.textContent = '⏳ Vérification...';
        
        const response = await fetch('/api/super-admin/update/check', { credentials: 'include' });
        const data = await response.json();
        
        const statusDiv = document.getElementById('updateStatus');
        const updateBtn = document.getElementById('performUpdateBtn');
        
        if (data.success) {
            const version = data.current_version;
            document.getElementById('currentVersion').innerHTML = `
                <p><strong>Commit:</strong> ${version.commit}</p>
                <p><strong>Date:</strong> ${version.date}</p>
                <p><strong>Message:</strong> ${version.message}</p>
                <p><strong>Branche:</strong> ${version.branch}</p>
            `;
            
            if (data.updates_available) {
                statusDiv.innerHTML = `
                    <p style="color: #F59E0B;"><strong>🆕 Mises à jour disponibles!</strong></p>
                    <p>Commits en retard: ${data.commits_behind}</p>
                    <p>Dernier commit: ${data.latest_commit}</p>
                `;
                updateBtn.style.display = 'inline-block';
            } else {
                statusDiv.innerHTML = `
                    <p style="color: #10B981;"><strong>✅ Vous êtes à jour!</strong></p>
                    <p>Aucune mise à jour disponible</p>
                `;
                updateBtn.style.display = 'none';
            }
        } else {
            statusDiv.innerHTML = `<p style="color: #EF4444;">❌ ${data.error}</p>`;
        }
    } catch (error) {
        console.error('Error checking updates:', error);
        document.getElementById('updateStatus').innerHTML = '<p style="color: #EF4444;">❌ Erreur de vérification</p>';
    } finally {
        const checkBtn = document.getElementById('checkUpdatesBtn');
        checkBtn.disabled = false;
        checkBtn.textContent = '🔍 Vérifier les mises à jour';
    }
}

async function performUpdate() {
    if (!confirm('⚠️ ATTENTION: Cette opération va mettre à jour l\'application. Une sauvegarde sera créée automatiquement. Continuer?')) {
        return;
    }
    
    try {
        const updateBtn = document.getElementById('performUpdateBtn');
        updateBtn.disabled = true;
        updateBtn.textContent = '⏳ Mise à jour en cours...';
        
        const response = await fetch('/api/super-admin/update/perform', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                auto_backup: true,
                auto_migrate: true
            }),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ Mise à jour réussie! L\'application va redémarrer.');
            location.reload();
        } else {
            alert('❌ Erreur: ' + data.error);
            updateBtn.disabled = false;
            updateBtn.textContent = '⬇️ Mettre à jour maintenant';
        }
    } catch (error) {
        console.error('Error performing update:', error);
        alert('❌ Erreur lors de la mise à jour');
    }
}

async function loadUpdateHistory() {
    try {
        const response = await fetch('/api/super-admin/update/history', { credentials: 'include' });
        const data = await response.json();
        
        if (data.success) {
            renderUpdateHistory(data.history);
        }
    } catch (error) {
        console.error('Error loading update history:', error);
    }
}

function renderUpdateHistory(history) {
    const tbody = document.getElementById('updateHistoryTableBody');
    
    if (history.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">Aucune mise à jour effectuée</td></tr>';
        return;
    }
    
    tbody.innerHTML = history.map(update => `
        <tr>
            <td>${new Date(update.timestamp).toLocaleString()}</td>
            <td>${update.success ? '<span style="color: #10B981;">✓ Réussie</span>' : '<span style="color: #EF4444;">✗ Échouée</span>'}</td>
            <td>${update.steps ? update.steps.length : 0} étapes</td>
            <td>${update.message || update.error || 'N/A'}</td>
        </tr>
    `).join('');
}

// Event listeners for backup and update
if (document.getElementById('createBackupBtn')) {
    document.getElementById('createBackupBtn').addEventListener('click', createBackup);
    document.getElementById('refreshBackupsBtn').addEventListener('click', loadBackups);
}

if (document.getElementById('checkUpdatesBtn')) {
    document.getElementById('checkUpdatesBtn').addEventListener('click', checkForUpdates);
    document.getElementById('performUpdateBtn').addEventListener('click', performUpdate);
}

// Override sidebar section opening to load data
const originalOpenSidebarSection = window.openSidebarSection;
window.openSidebarSection = function(sectionId) {
    originalOpenSidebarSection(sectionId);
    
    if (sectionId === 'backup') {
        loadBackups();
    } else if (sectionId === 'update') {
        checkForUpdates();
        loadUpdateHistory();
    }
};

async function init() {
    if (await checkAuth()) {
        await Promise.all([
            loadStats(),
            loadCompanies(),
            loadAppSettings(),
            loadProfile(),
            loadAvailableLanguages()
        ]);
    }
}

init();
