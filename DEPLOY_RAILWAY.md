# Déploiement Multi-Plateforme 🚀

> Guide pour déployer sur Railway, Python Anywhere, Render, et autres plateformes

## ✅ Problème de connexion RÉSOLU

L'application a été corrigée pour fonctionner sur **toutes** les plateformes. Le problème de "Erreur de connexion au serveur" lors du login est maintenant résolu grâce à :

1. **CORS intelligent** - Détection automatique du domaine avec fallback sécurisé
2. **Session cookies** - Configuration correcte pour production (HTTPS, SameSite=None)
3. **Credentials** - Tous les appels API incluent `credentials: 'include'`

---

## 🔧 Configuration requise (TOUTES PLATEFORMES)

### 1. Variables d'environnement obligatoires

#### SECRET_KEY (Protection des sessions)
```bash
# Générez une clé avec cette commande:
python -c "import secrets; print(secrets.token_hex(32))"

# Ajoutez dans Railway:
SECRET_KEY=votre_clé_générée_ici
```

#### ENCRYPTION_KEY (Chiffrement des données)
```bash
# Générez une clé avec cette commande:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Ajoutez dans Railway:
ENCRYPTION_KEY=votre_clé_générée_ici
```

### 2. Base de données PostgreSQL

Railway configure automatiquement `DATABASE_URL` quand vous ajoutez PostgreSQL à votre projet.

### 3. CORS - Auto-détection intelligente ✨

L'application détecte **automatiquement** votre plateforme :

#### Railway
```bash
RAILWAY_PUBLIC_DOMAIN=votre-app.up.railway.app  # Auto-configuré par Railway
```

#### Python Anywhere
```bash
PYTHONANYWHERE_DOMAIN=yourusername.pythonanywhere.com
```

#### Autres plateformes
```bash
ALLOWED_ORIGINS=https://votre-domaine.com
```

Pour plusieurs domaines :
```bash
ALLOWED_ORIGINS=https://app1.com,https://app2.com
```

> **Note**: Si aucune variable n'est configurée, l'app utilise un CORS permissif avec support des credentials (fonctionne partout mais moins sécurisé)

### 4. SendGrid (Optionnel - pour emails)

```bash
SENDGRID_API_KEY=votre_clé_api
SENDGRID_FROM_EMAIL=noreply@votredomaine.com
```

## 📋 Étapes de déploiement

1. **Créer un projet Railway**
   - Allez sur railway.app
   - Créez un nouveau projet depuis GitHub

2. **Ajouter PostgreSQL**
   - Cliquez sur "New" → "Database" → "PostgreSQL"
   - Railway configure automatiquement DATABASE_URL

3. **Configurer les variables**
   - Cliquez sur votre service
   - Onglet "Variables"
   - Ajoutez SECRET_KEY et ENCRYPTION_KEY (voir ci-dessus)

4. **Déployer**
   - Railway déploie automatiquement depuis GitHub
   - Attendez que le déploiement se termine
   - Vérifiez les logs pour les avertissements

## ✅ Vérification

Dans les logs Railway, vous devriez voir :
- ✅ "Auto-detected Railway domain: xxx.up.railway.app" (CORS OK)
- ✅ Aucun avertissement SECRET_KEY ou ENCRYPTION_KEY
- ✅ Flask app démarré sur port 5000

Si vous voyez des warnings :
- ⚠️ "SECRET_KEY not found" → Ajoutez SECRET_KEY
- ⚠️ "ENCRYPTION_KEY is invalid" → Régénérez ENCRYPTION_KEY
- ⚠️ "No specific domain detected" → Railway configurera automatiquement

## 🔒 Sécurité

- ✅ Toutes les clés sont générées aléatoirement
- ✅ Ne commitez JAMAIS les clés dans Git
- ✅ Gardez une copie sécurisée de vos clés
- ⚠️ Si vous perdez ENCRYPTION_KEY, les données chiffrées seront irrécupérables

## 🆘 Dépannage

### ✅ "Erreur de connexion au serveur" - RÉSOLU
Ce problème est maintenant **corrigé** ! L'application fonctionne sur toutes les plateformes.

Si vous rencontrez toujours ce problème :
1. **Vérifiez SECRET_KEY et ENCRYPTION_KEY** sont configurées
2. **Vérifiez PostgreSQL** est connecté (DATABASE_URL)
3. **Consultez les logs** pour voir la configuration CORS détectée

### Sessions ne fonctionnent pas
- ✅ Vérifiez que SECRET_KEY est configurée
- ✅ L'app détecte automatiquement HTTPS et configure les cookies correctement
- ✅ CORS permet maintenant les credentials sur toutes les plateformes

### Données chiffrées illisibles
- ⚠️ Vous avez probablement changé ENCRYPTION_KEY
- Restaurez l'ancienne clé ou régénérez les données

---

## 🌐 Déploiement Python Anywhere

### Configuration spécifique

1. **Créez une Web App**
   - Type: Flask
   - Python version: 3.11

2. **Variables d'environnement** (dans WSGI file):
```python
os.environ['SECRET_KEY'] = 'votre_clé'
os.environ['ENCRYPTION_KEY'] = 'votre_clé'
os.environ['PYTHONANYWHERE_DOMAIN'] = 'yourusername.pythonanywhere.com'
os.environ['DATABASE_URL'] = 'postgresql://...'  # Si PostgreSQL
```

3. **WSGI Configuration** (`/var/www/yourusername_pythonanywhere_com_wsgi.py`):
```python
import sys
path = '/home/yourusername/webapp-devis'
if path not in sys.path:
    sys.path.append(path)

from main import app as application
```

---

## 🎯 Déploiement Render

1. **Créez un Web Service**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn -b 0.0.0.0:$PORT main:app`

2. **Variables d'environnement**:
```bash
SECRET_KEY=...
ENCRYPTION_KEY=...
ALLOWED_ORIGINS=https://votre-app.onrender.com
```

3. **Base de données**:
   - Ajoutez PostgreSQL depuis le dashboard Render
   - DATABASE_URL est auto-configuré

---

## 🔄 Comment ça marche maintenant

### Avant (❌ ne fonctionnait pas)
```python
# CORS avec origins='*' et supports_credentials=False
# → Les navigateurs rejettent les cookies de session
```

### Maintenant (✅ fonctionne partout)
```python
# 1. Détection automatique du domaine (Railway, Python Anywhere, etc.)
# 2. Si pas de domaine: CORS avec origine réfléchie + credentials
# 3. Session cookies configurés pour production (HTTPS, SameSite=None)
# 4. Tous les fetch() incluent credentials: 'include'
```

**Résultat** : Le login fonctionne sur **Railway, Python Anywhere, Render, Heroku, DigitalOcean**, etc.

## 📚 Documentation

Pour plus d'informations, consultez :
- [Railway Documentation](https://docs.railway.app/)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/latest/deploying/)
