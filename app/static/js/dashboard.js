async function checkAuth() {
    try {
        const response = await fetch('/api/auth/check', { credentials: 'include' });
        const data = await response.json();
        
        if (!data.authenticated) {
            window.location.href = '/login.html';
            return false;
        }
        return true;
    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.href = '/login.html';
        return false;
    }
}

async function loadDashboardData() {
    try {
        const [statsResponse, quotesResponse] = await Promise.all([
            fetch('/api/quotes/stats', { credentials: 'include' }),
            fetch('/api/quotes/recent', { credentials: 'include' })
        ]);

        if (!statsResponse.ok || !quotesResponse.ok) {
            throw new Error('Failed to load dashboard data');
        }

        const stats = await statsResponse.json();
        const quotes = await quotesResponse.json();

        updateMetrics(stats);
        displayRecentQuotes(quotes);
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showError('Erreur lors du chargement des données');
    }
}

function updateMetrics(stats) {
    document.getElementById('totalQuotes').textContent = stats.total || 0;
    document.getElementById('totalAmount').textContent = formatCurrency(stats.totalAmount || 0);
    document.getElementById('monthQuotes').textContent = stats.thisMonth || 0;
    document.getElementById('monthAmount').textContent = formatCurrency(stats.thisMonthAmount || 0);
    document.getElementById('weekQuotes').textContent = stats.thisWeek || 0;
    document.getElementById('weekAmount').textContent = formatCurrency(stats.thisWeekAmount || 0);
    document.getElementById('totalItems').textContent = stats.totalItems || 0;
    document.getElementById('topClient').textContent = stats.topClient || '-';
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('fr-MA', {
        style: 'currency',
        currency: 'MAD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fr-FR', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    }).format(date);
}

function displayRecentQuotes(quotes) {
    const container = document.getElementById('quotesTable');
    
    if (!quotes || quotes.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <p>Aucun devis pour le moment</p>
                <button onclick="window.location.href='/quote.html'" class="btn-primary">Créer votre premier devis</button>
            </div>
        `;
        return;
    }

    const tableHTML = `
        <table>
            <thead>
                <tr>
                    <th>N° Devis</th>
                    <th>Client</th>
                    <th>Produit</th>
                    <th>Date</th>
                    <th>Montant TTC</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${quotes.map(quote => `
                    <tr>
                        <td><strong>${quote.quote_number}</strong></td>
                        <td>${quote.client_name || '-'}</td>
                        <td>${quote.chassis_type_name || '-'}</td>
                        <td>${formatDate(quote.created_at)}</td>
                        <td><strong>${formatCurrency(quote.total_price)}</strong></td>
                        <td>
                            <div style="display: flex; gap: 0.5rem; justify-content: center;">
                                <button onclick="viewQuote(${quote.id})" class="btn-icon" title="Voir">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                        <circle cx="12" cy="12" r="3"></circle>
                                    </svg>
                                </button>
                                <button onclick="sendQuoteByEmail(${quote.id})" class="btn-icon" title="Envoyer par Email" style="background: #10B981;">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                                        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                                        <polyline points="22,6 12,13 2,6"></polyline>
                                    </svg>
                                </button>
                                <button onclick="editQuote(${quote.id})" class="btn-icon" title="Modifier">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                                    </svg>
                                </button>
                                <button onclick="deleteQuote(${quote.id})" class="btn-icon btn-icon-danger" title="Supprimer">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <polyline points="3 6 5 6 21 6"></polyline>
                                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                    </svg>
                                </button>
                                <button onclick="downloadPDF(${quote.id})" class="btn-icon" title="Télécharger PDF">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                        <polyline points="7 10 12 15 17 10"></polyline>
                                        <line x1="12" y1="15" x2="12" y2="3"></line>
                                    </svg>
                                </button>
                            </div>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = tableHTML;
}

async function viewQuote(quoteId) {
    try {
        const response = await fetch(`/api/quotes/${quoteId}`, { credentials: 'include' });
        
        if (!response.ok) {
            throw new Error('Failed to fetch quote');
        }

        const quote = await response.json();
        showQuoteModal(quote);
    } catch (error) {
        console.error('Error viewing quote:', error);
        showToast('Erreur lors de la récupération du devis', 'error');
    }
}

function showQuoteModal(quote) {
    let details;
    try {
        details = typeof quote.details === 'string' ? JSON.parse(quote.details) : quote.details;
    } catch (e) {
        console.error('Error parsing quote details:', e);
        showToast('Erreur lors de l\'affichage des détails du devis', 'error');
        return;
    }
    
    const items = details.items || [];
    
    let itemsHTML = '';
    if (items.length > 0) {
        itemsHTML = `
            <h4 style="margin-top: 1.5rem; margin-bottom: 1rem; font-size: 1.125rem;">Articles (${items.length})</h4>
            ${items.map((item, idx) => {
                const breakdown = item.breakdown || {};
                const accessories = item.accessories || {};
                const accessoriesList = Object.entries(accessories)
                    .filter(([name, qty]) => qty > 0)
                    .map(([name, qty]) => `${name} (×${qty})`)
                    .join(', ') || 'Aucun';
                    
                const quantity = item.quantity || 1;
                const unitPrice = breakdown.total_price || 0;
                const itemTotal = unitPrice * quantity;
                
                return `
                <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <h5 style="margin-bottom: 0.75rem; color: #3B82F6;">Article ${idx + 1} - ${item.chassisType || item.chassis_type || ''}</h5>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.9rem;">
                        <div><strong>Dimensions:</strong> ${item.width} × ${item.height} mm</div>
                        <div><strong>Surface:</strong> ${breakdown.surface_m2 || 0} m²</div>
                        <div><strong>Périmètre:</strong> ${breakdown.perimeter_m || 0} m</div>
                        <div><strong>Série:</strong> ${item.profileSeries || item.profile_series || ''}</div>
                        <div><strong>Vitrage:</strong> ${item.glazingType || item.glazing_type || ''}</div>
                        <div><strong>Finition:</strong> ${item.finish || ''}</div>
                        <div style="grid-column: 1 / -1;"><strong>Accessoires:</strong> ${accessoriesList}</div>
                        <div><strong>Quantité:</strong> ${quantity}</div>
                    </div>
                    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.85rem;">
                            <div>Base: ${formatCurrency(breakdown.base_price || 0)}</div>
                            <div>Vitrage: ${formatCurrency(breakdown.glazing_cost || 0)}</div>
                            <div>Profilés: ${formatCurrency(breakdown.profile_cost || 0)}</div>
                            <div>Accessoires: ${formatCurrency(breakdown.accessories_cost || 0)}</div>
                            <div>Finition: ${formatCurrency(breakdown.finish_supplement || 0)}</div>
                            <div>Main d'œuvre: ${formatCurrency(breakdown.labor || 0)}</div>
                        </div>
                        <div style="margin-top: 0.5rem; text-align: right; font-size: 1rem; font-weight: bold; color: #3B82F6;">
                            Prix unitaire: ${formatCurrency(unitPrice)} × ${quantity} = ${formatCurrency(itemTotal)}
                        </div>
                    </div>
                </div>
            `;}).join('')}
            <div style="background: #3B82F6; color: white; padding: 1rem; border-radius: 8px; font-size: 1.25rem; font-weight: bold; text-align: right;">
                Total du devis: ${formatCurrency(items.reduce((sum, item) => {
                    const quantity = item.quantity || 1;
                    const unitPrice = (item.breakdown || {}).total_price || 0;
                    return sum + (unitPrice * quantity);
                }, 0))}
            </div>
        `;
    } else {
        const accessories = JSON.parse(quote.accessories || '{}');
        const accessoriesList = Object.entries(accessories)
            .filter(([name, qty]) => qty > 0)
            .map(([name, qty]) => `${name} (×${qty})`)
            .join(', ') || 'Aucun';
            
        itemsHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-top: 1rem;">
                <div><strong>Type:</strong> ${quote.chassis_type_name || quote.chassis_type || ''}</div>
                <div><strong>Dimensions:</strong> ${quote.width} × ${quote.height} mm</div>
                <div><strong>Série:</strong> ${quote.profile_series || ''}</div>
                <div><strong>Vitrage:</strong> ${quote.glazing_type || ''}</div>
                <div><strong>Finition:</strong> ${quote.finish || ''}</div>
                <div style="grid-column: 1 / -1;"><strong>Accessoires:</strong> ${accessoriesList}</div>
                <div style="grid-column: 1 / -1;"><strong>Prix Total:</strong> ${formatCurrency(quote.total_price || 0)}</div>
            </div>
        `;
    }
    
    const modalHTML = `
        <div class="modal-overlay" onclick="closeModal()">
            <div class="modal-content" onclick="event.stopPropagation()" style="max-width: 800px; max-height: 90vh; overflow-y: auto;">
                <div class="modal-header">
                    <h3>Devis ${quote.quote_number}</h3>
                    <button onclick="closeModal()" class="btn-icon">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
                <div class="modal-body">
                    <div style="margin-bottom: 1.5rem;">
                        <h4 style="margin-bottom: 0.5rem;">Informations client</h4>
                        <div><strong>Nom:</strong> ${details.client_name || '-'}</div>
                        <div><strong>Téléphone:</strong> ${details.client_phone || '-'}</div>
                        <div><strong>Email:</strong> ${details.client_email || '-'}</div>
                        ${details.client_notes ? `<div><strong>Notes:</strong> ${details.client_notes}</div>` : ''}
                    </div>
                    ${itemsHTML}
                </div>
                <div class="modal-footer">
                    <button onclick="closeModal()" class="btn-secondary">Fermer</button>
                    <button onclick="sendQuoteByEmail(${quote.id}); closeModal();" class="btn-primary" style="background: #10B981;">
                        📧 Envoyer par Email
                    </button>
                    <button onclick="downloadPDF(${quote.id}); closeModal();" class="btn-primary">📥 Télécharger PDF</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function closeModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) {
        modal.remove();
    }
}

async function editQuote(quoteId) {
    window.location.href = `/quote.html?edit=${quoteId}`;
}

async function deleteQuote(quoteId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce devis ? Cette action est irréversible.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/quotes/${quoteId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete quote');
        }
        
        showToast('Devis supprimé avec succès', 'success');
        loadDashboardData();
    } catch (error) {
        console.error('Error deleting quote:', error);
        showToast('Erreur lors de la suppression du devis', 'error');
    }
}

async function downloadPDF(quoteId) {
    try {
        const response = await fetch(`/api/quotes/${quoteId}/pdf`, { credentials: 'include' });
        
        if (!response.ok) {
            throw new Error('Failed to download PDF');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `devis_${quoteId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showToast('PDF téléchargé avec succès', 'success');
    } catch (error) {
        console.error('Error downloading PDF:', error);
        showToast('Erreur lors du téléchargement du PDF', 'error');
    }
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => document.body.removeChild(toast), 300);
    }, 3000);
}

function showError(message) {
    const container = document.getElementById('quotesTable');
    container.innerHTML = `
        <div class="error-state">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#f44336" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <p>${message}</p>
        </div>
    `;
}

async function sendQuoteByEmail(quoteId) {
    try {
        const quoteResponse = await fetch(`/api/quotes/${quoteId}`, { credentials: 'include' });
        if (!quoteResponse.ok) {
            throw new Error('Impossible de récupérer les informations du devis');
        }
        
        const quote = await quoteResponse.json();
        const details = JSON.parse(quote.details || '{}');
        
        let email = details.client_email || '';
        
        if (!email || email.trim() === '') {
            email = prompt('Le devis n\'a pas d\'email client.\nEntrez l\'adresse email du destinataire :');
            if (!email || email.trim() === '') {
                showToast('⚠️ Email requis pour l\'envoi', 'error');
                return;
            }
        }
        
        const message = prompt(`Envoi à: ${email}\n\nMessage personnalisé (optionnel) :`);
        
        const response = await fetch('/api/email/send-quote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                quote_id: quoteId,
                recipient_email: email,
                custom_message: message || ''
            }),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Erreur lors de l\'envoi');
        }
        
        showToast(`✅ Email envoyé avec succès à ${email}`, 'success');
    } catch (error) {
        console.error('Error sending email:', error);
        showToast('❌ Erreur lors de l\'envoi de l\'email: ' + error.message, 'error');
    }
}

// Sidebar Management
function openSidebar() {
    document.getElementById('sidebar').classList.add('active');
    document.getElementById('sidebarOverlay').classList.add('active');
}

function closeSidebar() {
    document.getElementById('sidebar').classList.remove('active');
    document.getElementById('sidebarOverlay').classList.remove('active');
}

function openSidebarSection(sectionId) {
    closeSidebar();
    document.querySelectorAll('.sidebar-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(`section-${sectionId}`).classList.add('active');
    document.getElementById('sidebarOverlay').classList.add('active');
}

function closeSidebarSection() {
    document.querySelectorAll('.sidebar-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById('sidebarOverlay').classList.remove('active');
}

// Load Profile Data
async function loadProfileData() {
    try {
        const response = await fetch('/api/users/me', { credentials: 'include' });
        if (response.ok) {
            const user = await response.json();
            document.getElementById('profileUsername').value = user.username || '';
            document.getElementById('profileFullName').value = user.full_name || '';
            document.getElementById('profileEmail').value = user.email || '';
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

// Save Profile
async function saveProfile() {
    const fullName = document.getElementById('profileFullName').value;
    const email = document.getElementById('profileEmail').value;
    const password = document.getElementById('profilePassword').value;
    
    const data = { full_name: fullName, email: email };
    if (password) {
        data.password = password;
    }
    
    try {
        const response = await fetch('/api/users/me', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
            credentials: 'include'
        });
        
        if (response.ok) {
            showToast('Profil mis à jour avec succès', 'success');
            document.getElementById('profilePassword').value = '';
        } else {
            const error = await response.json();
            showToast(error.error || 'Erreur lors de la mise à jour', 'error');
        }
    } catch (error) {
        console.error('Error saving profile:', error);
        showToast('Erreur lors de la mise à jour du profil', 'error');
    }
}

// Event Listeners
document.getElementById('newQuoteBtn').addEventListener('click', () => {
    window.location.href = '/quote.html';
});

document.getElementById('refreshBtn').addEventListener('click', () => {
    loadDashboardData();
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

// Hamburger Menu
document.getElementById('hamburgerBtn').addEventListener('click', openSidebar);
document.getElementById('closeSidebar').addEventListener('click', closeSidebar);
document.getElementById('sidebarOverlay').addEventListener('click', () => {
    closeSidebar();
    closeSidebarSection();
});

// Nav Items
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        const section = item.getAttribute('data-section');
        openSidebarSection(section);
        if (section === 'profile') {
            loadProfileData();
        }
    });
});

// Save Profile Button
document.getElementById('saveProfile').addEventListener('click', saveProfile);

async function init() {
    if (await checkAuth()) {
        await loadDashboardData();
    }
}

init();
