let originalData = {};

async function loadProfile() {
    try {
        const response = await fetch('/api/users/me', { credentials: 'include' });
        if (!response.ok) throw new Error('Failed to load profile');
        
        const user = await response.json();
        originalData = { ...user };
        
        document.getElementById('displayFullName').textContent = user.full_name;
        document.getElementById('displayRole').textContent = user.role === 'admin' ? 'Administrateur' : 'Utilisateur';
        document.getElementById('displayRole').className = `role-badge role-${user.role}`;
        
        document.getElementById('fullName').value = user.full_name;
        document.getElementById('username').value = user.username;
    } catch (error) {
        showNotification('Erreur lors du chargement du profil', 'error');
    }
}

document.getElementById('profileForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fullName = document.getElementById('fullName').value;
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    if (newPassword && newPassword !== confirmPassword) {
        showNotification('Les mots de passe ne correspondent pas', 'error');
        return;
    }
    
    if (newPassword && !currentPassword) {
        showNotification('Veuillez entrer votre mot de passe actuel', 'error');
        return;
    }
    
    const data = { full_name: fullName };
    if (newPassword) {
        data.current_password = currentPassword;
        data.new_password = newPassword;
    }
    
    try {
        const response = await fetch('/api/users/me', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
            credentials: 'include'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erreur lors de la mise à jour');
        }
        
        showNotification('Profil mis à jour avec succès', 'success');
        
        document.getElementById('currentPassword').value = '';
        document.getElementById('newPassword').value = '';
        document.getElementById('confirmPassword').value = '';
        
        await loadProfile();
    } catch (error) {
        showNotification(error.message, 'error');
    }
});

document.getElementById('cancelBtn').addEventListener('click', () => {
    document.getElementById('fullName').value = originalData.full_name;
    document.getElementById('currentPassword').value = '';
    document.getElementById('newPassword').value = '';
    document.getElementById('confirmPassword').value = '';
    showNotification('Modifications annulées', 'info');
});

document.getElementById('backBtn').addEventListener('click', () => {
    window.location.href = '/dashboard.html';
});

document.getElementById('logoutBtn').addEventListener('click', async () => {
    if (confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
        try {
            await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
            window.location.href = '/login.html';
        } catch (error) {
            showNotification('Erreur lors de la déconnexion', 'error');
        }
    }
});

function showNotification(message, type) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification notification-${type}`;
    notification.style.display = 'block';
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

loadProfile();
