# PWA Devis Menuiserie Aluminium

Une Progressive Web App (PWA) multi-tenant SaaS pour la génération de devis de menuiserie en aluminium avec calcul automatique des prix, génération PDF et envoi par email.

## 🎯 Fonctionnalités principales

### Pour les commerciaux
- ✅ **Création de devis en 8 étapes guidées** : sélection produit, dimensions, profilé, vitrage, accessoires, finitions, client et récapitulatif
- 📊 **Calcul automatique des prix** en temps réel avec prise en compte des coefficients, TVA et remises
- 📄 **Génération PDF instantanée** (<2s) avec en-tête personnalisé de l'entreprise
- 📧 **Envoi par email** via SendGrid avec template HTML professionnel
- 💾 **Mode hors ligne** pour continuer à travailler sans connexion
- 📱 **Interface mobile-first** optimisée pour smartphones et tablettes

### Pour les administrateurs d'entreprise
- 👥 **Gestion des utilisateurs** (admin/utilisateur) avec isolation par entreprise
- 🛠️ **Paramétrage complet** : logo, TVA, remises, main d'œuvre, catalogue produits
- 📈 **Statistiques détaillées** : nombre de devis, montants, évolution mensuelle
- 📋 **Historique des devis** avec recherche et filtres
- 🔐 **Sécurité renforcée** : chiffrement Fernet (AES-128) pour données sensibles

### Pour les super administrateurs
- 🏢 **Gestion multi-entreprises** avec workflow d'approbation
- 📊 **Tableau de bord global** avec statistiques consolidées (12 métriques)
- 👤 **Gestion des profils** et paramètres applicatifs
- 📝 **Logs d'activité** avec traçabilité complète des actions
- ⚙️ **Personnalisation des textes** de l'application (titres, messages)
- 📦 **Catalogue multi-tenant** : chaque entreprise a son propre catalogue isolé

## 🏗️ Architecture technique

### Backend
- **Framework** : Flask 3.1.2 (Python)
- **Base de données** : PostgreSQL avec SQLAlchemy ORM
- **API** : RESTful avec 7 blueprints modulaires
- **Sécurité** : 
  - PBKDF2-SHA256 pour les mots de passe
  - Fernet (AES-128) pour les données sensibles
  - RBAC (Role-Based Access Control) : user, admin, super_admin
- **PDF** : ReportLab avec formatage MAD (Dirham marocain)
- **Email** : SendGrid via Replit Connector

### Frontend
- **Technologies** : HTML5, CSS3, JavaScript vanilla
- **UI/UX** : 
  - Design moderne avec bords arrondis (12px)
  - Pattern diagonal subtil (2% opacité) pour profondeur visuelle
  - Menu hamburger latéral pour navigation
  - Cartes avec ombres et transitions fluides
- **PWA** : Service Worker pour mode hors ligne
- **Responsive** : Mobile-first avec grid layouts

### Multi-tenancy (SaaS)
- **Isolation complète** par `company_id` sur toutes les tables
- **Catalogue par entreprise** : copie automatique du template à la création
- **Utilisateurs isolés** : admins ne voient que leurs utilisateurs
- **Données chiffrées** : email, téléphone, ICE, adresses par entreprise

## 📋 Prérequis

- Python 3.11+ 
- Git
- SQLite (inclus avec Python) ou PostgreSQL 13+ (optionnel pour production)
- Compte SendGrid (optionnel - pour l'envoi d'emails)

## 🚀 Installation locale (Windows)

### Installation automatique en une commande

Ouvrez **PowerShell** et exécutez :

```powershell
# Installer Python 3.11
winget install --id Python.Python.3.11 -e

# Installer Git
winget install --id Git.Git -e

# Redémarrer le terminal pour charger les nouvelles variables d'environnement, puis :

# Cloner le projet
git clone https://github.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium
cd Webapp-Devis-Chassis-Aluminium

# Autoriser l'exécution de scripts PowerShell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force

# Créer un environnement virtuel
python -m venv .venv
# Si la commande ci-dessus ne fonctionne pas, essayez :
# py -3.11 -m venv .venv

# Activer l'environnement virtuel
.\.venv\Scripts\Activate.ps1

# Mettre à jour pip et installer les dépendances
python -m pip install -U pip wheel
python -m pip install -r requirements.txt

# Lancer l'application (la base de données sera créée automatiquement)
python .\main.py
```

### ✅ Accès à l'application

Une fois démarrée, l'application est accessible à : **http://localhost:5000**

**Compte super administrateur par défaut :**
- Nom d'utilisateur : `superadmin`
- Mot de passe : `admin123`

> ⚠️ **Important** : Changez ce mot de passe après votre première connexion pour des raisons de sécurité !

### 📝 Configuration optionnelle

Pour personnaliser la configuration (SendGrid, clé secrète, etc.), copiez `.env.example` vers `.env` :

```powershell
copy .env.example .env
```

Puis éditez `.env` avec vos valeurs :
```env
SECRET_KEY=votre-cle-secrete-personnalisee
SENDGRID_API_KEY=votre-cle-api-sendgrid
SENDGRID_FROM_EMAIL=noreply@votredomaine.com
```

### 🔄 Arrêt et redémarrage

Pour arrêter l'application : appuyez sur `Ctrl+C` dans le terminal.

Pour redémarrer l'application :
```powershell
cd Webapp-Devis-Chassis-Aluminium
.\.venv\Scripts\Activate.ps1
python .\main.py
```

## 🚀 Installation locale (Linux/Mac)

```bash
# Cloner le projet
git clone https://github.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium
cd Webapp-Devis-Chassis-Aluminium

# Créer un environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -U pip wheel
pip install -r requirements.txt

# Lancer l'application
python main.py
```

L'application sera accessible sur `http://localhost:5000`

### 📊 Base de données

**Par défaut :** L'application utilise **SQLite** (fichier `devis_menuiserie.db`) qui est créé automatiquement au premier lancement. Aucune configuration n'est nécessaire.

**Pour PostgreSQL (optionnel) :** 
1. Créer une base de données PostgreSQL
2. Définir `DATABASE_URL` dans le fichier `.env` :
```env
DATABASE_URL=postgresql://user:password@localhost/devis_menuiserie
```

## 🖥️ Déploiement sur serveur

### Avec Gunicorn (recommandé pour production)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --reuse-port main:app
```

### Configuration Nginx (reverse proxy)
```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Variables d'environnement production
```env
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@db-host/devis_prod
SECRET_KEY=clé-secrète-production
ENCRYPTION_KEY=clé-chiffrement-production
```

## 🔌 API Endpoints

### Authentification (`/api/auth`)
- `POST /login` - Connexion
- `POST /logout` - Déconnexion
- `GET /check` - Vérifier le statut de connexion

### Catalogue (`/api/catalog`)
- `GET /chassis-types` - Types de châssis
- `GET /profile-series` - Séries de profilés
- `GET /glazing-types` - Types de vitrage
- `GET /finishes` - Finitions
- `GET /accessories` - Accessoires
- `POST|PUT|DELETE /*` - CRUD (admin uniquement)

### Devis (`/api/quotes`)
- `POST /calculate` - Calculer un prix
- `POST /` - Créer un devis
- `GET /stats` - Statistiques
- `GET /recent` - Devis récents
- `GET /<id>` - Détails d'un devis
- `GET /<id>/pdf` - Générer PDF
- `DELETE /<id>` - Supprimer

### Utilisateurs (`/api/users`)
- `GET /` - Liste des utilisateurs (admin)
- `POST /` - Créer un utilisateur (admin)
- `DELETE /<id>` - Supprimer (admin)
- `GET /me` - Profil actuel
- `PUT /me` - Modifier profil

### Email (`/api/email`)
- `POST /send-quote` - Envoyer devis par email
- `GET /test-connection` - Tester SendGrid

### Super Admin (`/api/super-admin`)
- `GET /companies` - Liste entreprises
- `POST /companies/create` - Créer entreprise + admin
- `POST /companies/<id>/approve|reject|activate|deactivate`
- `GET /stats` - Statistiques globales
- `GET|PUT /profile` - Profil super admin
- `GET|PUT /app-settings` - Paramètres applicatifs
- `GET /activity-logs` - Logs d'activité

## 📊 Structure de la base de données

### Tables principales
- `companies` - Entreprises avec statut d'approbation
- `users` - Utilisateurs avec email obligatoire
- `quotes` - Devis avec breakdown JSON
- `settings` - Paramètres par entreprise (chiffrés)
- `app_settings` - Paramètres applicatifs globaux
- `activity_logs` - Traçabilité des actions

### Tables catalogue (multi-tenant)
- `chassis_types` - Types de châssis (avec company_id)
- `profile_series` - Séries de profilés (avec company_id)
- `glazing_types` - Types de vitrage (avec company_id)
- `finishes` - Finitions (avec company_id)
- `accessories` - Accessoires (avec company_id)

Chaque table catalogue a une contrainte unique composite `(company_id, name)`.
Le template (company_id=NULL) est copié automatiquement aux nouvelles entreprises.

## 🔐 Sécurité

### Authentification
- Hachage PBKDF2-SHA256 avec salt pour les mots de passe
- Sessions Flask avec cookie sécurisé
- Vérification de rôle sur chaque endpoint protégé

### Chiffrement
- Fernet (AES-128) pour : email, téléphone, ICE, adresses
- Clé de chiffrement stockée dans variable d'environnement
- Déchiffrement à la volée lors de l'accès

### Isolation multi-tenant
- Filtrage automatique par `company_id` sur tous les GET
- Vérification du `company_id` sur tous les PUT/DELETE
- Super admin exempté des restrictions

## 🎨 Personnalisation

### Thème couleurs (dans `styles.css`)
```css
:root {
    --primary: #3B82F6;
    --border-radius: 12px;
    --border-radius-sm: 8px;
    --border-radius-lg: 16px;
}
```

### Textes de l'application
Modifiables via l'interface super admin :
- Titre de l'application
- Titre du dashboard
- Titre des devis
- Message de bienvenue
- Nom expéditeur SendGrid

## 📝 Comptes de démonstration

- **Super Admin** : `superadmin` / `superadmin123`
- **Admin entreprise** : `admin` / `admin123`

## 🤝 Support

Pour toute question ou problème, contactez l'équipe de développement.

## 📄 Licence

Propriétaire - Tous droits réservés
