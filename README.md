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

### Méthode rapide avec winget

Ouvrez **PowerShell** et exécutez :

```powershell
# Installer Python 3.11 et Git
winget install Python.Python.3.11 Git.Git

# Redémarrer le terminal, puis :
git clone https://github.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium-v2
cd Webapp-Devis-Chassis-Aluminium-v2
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip wheel setuptools
pip install -r requirements.txt
python main.py
```

### Méthode manuelle

1. **Installer Python 3.11+** : [python.org/downloads](https://www.python.org/downloads/)
2. **Installer Git** : [git-scm.com](https://git-scm.com/download/win)
3. **Cloner et démarrer** :

```powershell
git clone https://github.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium-v2
cd Webapp-Devis-Chassis-Aluminium-v2
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip wheel setuptools
pip install -r requirements.txt
python main.py
```

### ✅ Accès à l'application

Une fois démarrée, l'application est accessible à : **http://localhost:5000**

**Compte super administrateur par défaut :**
- Nom d'utilisateur : `superadmin`
- Mot de passe : `admin123`

> ⚠️ **Important** : Changez ce mot de passe après votre première connexion !

## 🚀 Installation locale (Linux)

### Ubuntu / Debian

```bash
# Installer les dépendances système
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git

# Si vous avez besoin de Python 3.11 spécifiquement (optionnel)
# sudo apt install software-properties-common -y
# sudo add-apt-repository ppa:deadsnakes/ppa -y
# sudo apt update
# sudo apt install python3.11 python3.11-venv -y

# Cloner le projet
git clone https://github.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium-v2
cd Webapp-Devis-Chassis-Aluminium-v2

# Créer l'environnement virtuel (utilisez python3.11 si installé, sinon python3)
python3 -m venv .venv
source .venv/bin/activate

# Mettre à jour pip et installer les outils de base
python -m pip install -U pip wheel setuptools

# Installer les dépendances Python
pip install -r requirements.txt

# Lancer l'application
python main.py
```

### CentOS / RHEL / Fedora

```bash
# Installer les dépendances système
sudo dnf install -y python3 python3-pip git

# Pour Python 3.11 sur RHEL 9/Fedora (optionnel)
# sudo dnf install python3.11 python3.11-pip -y

# Cloner le projet
git clone https://github.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium-v2
cd Webapp-Devis-Chassis-Aluminium-v2

# Créer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Mettre à jour pip et installer les outils de base
python -m pip install -U pip wheel setuptools

# Installer les dépendances Python
pip install -r requirements.txt

# Lancer l'application
python main.py
```

L'application sera accessible sur `http://localhost:5000`

## 🚀 Installation locale (macOS)

### Avec Homebrew (recommandé)

```bash
# Installer Python 3.11 et Git
brew install python@3.11 git

# Cloner le projet
git clone https://github.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium-v2
cd Webapp-Devis-Chassis-Aluminium-v2

# Créer l'environnement virtuel
python3.11 -m venv .venv
source .venv/bin/activate

# Mettre à jour pip et installer les outils de base
python -m pip install -U pip wheel setuptools

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python main.py
```

### Sans Homebrew

1. Installer Python 3.11+ depuis [python.org](https://www.python.org/downloads/macos/)
2. Suivre les mêmes étapes que ci-dessus

L'application sera accessible sur `http://localhost:5000`

### 📊 Base de données

**Par défaut :** L'application utilise **SQLite** (fichier `devis_menuiserie.db`) qui est créé automatiquement au premier lancement. Aucune configuration n'est nécessaire.

**Pour PostgreSQL (optionnel) :** 
1. Créer une base de données PostgreSQL
2. Définir `DATABASE_URL` dans le fichier `.env` :
```env
DATABASE_URL=postgresql://user:password@localhost/devis_menuiserie
```

## 🖥️ Déploiement VPS / Serveur Linux

### Installation complète (Ubuntu/Debian)

```bash
# 1. Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# 2. Installer Python 3.11 (si pas déjà installé)
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# 3. Installer les dépendances
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx postgresql postgresql-contrib

# 4. Créer un utilisateur pour l'application
sudo useradd -m -s /bin/bash devisapp
sudo su - devisapp

# 5. Cloner le projet
git clone https://github.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium-v2
cd Webapp-Devis-Chassis-Aluminium-v2

# 6. Créer l'environnement virtuel
python3.11 -m venv .venv
source .venv/bin/activate

# 7. Mettre à jour pip et installer les outils de base
python -m pip install -U pip wheel setuptools

# 8. Installer les dépendances
pip install -r requirements.txt
pip install gunicorn

# 9. Configurer PostgreSQL
sudo -u postgres psql
CREATE DATABASE devis_menuiserie;
CREATE USER devisuser WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE devis_menuiserie TO devisuser;
\q

# 10. Créer le fichier .env
cat > .env << EOF
DATABASE_URL=postgresql://devisuser:votre_mot_de_passe@localhost/devis_menuiserie
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
FLASK_ENV=production
EOF

# 11. Créer le service systemd
exit  # Revenir à l'utilisateur root

sudo nano /etc/systemd/system/devisapp.service
```

**Contenu du fichier devisapp.service :**

```ini
[Unit]
Description=PWA Devis Menuiserie Application
After=network.target

[Service]
User=devisapp
Group=devisapp
WorkingDirectory=/home/devisapp/Webapp-Devis-Chassis-Aluminium-v2
Environment="PATH=/home/devisapp/Webapp-Devis-Chassis-Aluminium-v2/.venv/bin"
ExecStart=/home/devisapp/Webapp-Devis-Chassis-Aluminium-v2/.venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 --reuse-port main:app

[Install]
WantedBy=multi-user.target
```

**Configuration Nginx :**

```bash
sudo nano /etc/nginx/sites-available/devisapp
```

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/devisapp/Webapp-Devis-Chassis-Aluminium-v2/app/static;
    }
}
```

**Activer et démarrer :**

```bash
# Activer le site Nginx
sudo ln -s /etc/nginx/sites-available/devisapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Démarrer l'application
sudo systemctl start devisapp
sudo systemctl enable devisapp
sudo systemctl status devisapp
```

### SSL avec Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com
```

## 🪟 Déploiement Windows Server

### Installation sur Windows Server 2016/2019/2022

```powershell
# 1. Installer Python 3.11
# Télécharger depuis python.org et installer

# 2. Installer Git
# Télécharger depuis git-scm.com et installer

# 3. Cloner le projet
cd C:\inetpub
git clone https://github.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium-v2
cd Webapp-Devis-Chassis-Aluminium-v2

# 4. Créer l'environnement virtuel
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 5. Mettre à jour pip et installer les outils de base
python -m pip install -U pip wheel setuptools

# 6. Installer les dépendances
pip install -r requirements.txt
pip install waitress

# 7. Créer le fichier .env
@"
SECRET_KEY=votre-cle-secrete-unique
DATABASE_URL=sqlite:///devis_menuiserie.db
FLASK_ENV=production
"@ | Out-File -FilePath .env -Encoding utf8

# 8. Créer un service Windows avec NSSM
# Télécharger NSSM depuis nssm.cc
nssm install DevisApp "C:\inetpub\Webapp-Devis-Chassis-Aluminium-v2\.venv\Scripts\python.exe"
nssm set DevisApp AppParameters "-m waitress --port=5000 main:app"
nssm set DevisApp AppDirectory "C:\inetpub\Webapp-Devis-Chassis-Aluminium-v2"
nssm set DevisApp DisplayName "PWA Devis Menuiserie"
nssm set DevisApp Description "Application de devis menuiserie aluminium"
nssm set DevisApp Start SERVICE_AUTO_START

# 9. Démarrer le service
nssm start DevisApp
```

### Configuration IIS comme reverse proxy

1. Installer le module **URL Rewrite** et **Application Request Routing**
2. Configurer le reverse proxy vers `http://localhost:5000`

## 🌐 Déploiement sur cPanel

### Prérequis
- Accès SSH au serveur
- Python 3.11+ installé (via Python Selector ou Setup Python App)
- Accès à la base de données MySQL ou PostgreSQL

### Installation via SSH

```bash
# 1. Se connecter en SSH
ssh votre_user@votre-serveur.com

# 2. Aller dans le répertoire public_html ou créer un sous-domaine
cd ~/public_html  # ou cd ~/subdomains/app/public_html

# 3. Cloner le projet
git clone https://github.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium-v2
cd Webapp-Devis-Chassis-Aluminium-v2

# 4. Créer l'environnement virtuel (via cPanel Python App ou manuellement)
virtualenv --python=python3.11 venv
source venv/bin/activate

# 5. Mettre à jour pip et installer les outils de base
python -m pip install -U pip wheel setuptools

# 6. Installer les dépendances
pip install -r requirements.txt
pip install gunicorn

# 7. Configurer la base de données via cPanel
# Créer une base MySQL ou PostgreSQL dans cPanel

# 8. Créer le fichier .env
cat > .env << EOF
DATABASE_URL=mysql://user:password@localhost/database_name
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
FLASK_ENV=production
EOF

# 9. Créer le fichier passenger_wsgi.py
cat > passenger_wsgi.py << 'EOF'
import sys
import os

# Ajouter le chemin de l'application
INTERP = os.path.join(os.environ['HOME'], 'public_html', 'Webapp-Devis-Chassis-Aluminium-v2', 'venv', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.insert(0, os.path.dirname(__file__))

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Importer l'application Flask
from main import app as application
EOF
```

### Configuration dans cPanel

1. **Setup Python App** (si disponible) :
   - Application root : `/home/user/public_html/Webapp-Devis-Chassis-Aluminium-v2`
   - Application URL : `/` ou votre sous-domaine
   - Python version : 3.11
   - Application startup file : `passenger_wsgi.py`

2. **Fichier .htaccess** (si nécessaire) :

```apache
# Créer dans public_html
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ /Webapp-Devis-Chassis-Aluminium-v2/passenger_wsgi.py/$1 [QSA,L]
```

3. **Redémarrer l'application** via cPanel Python App

### Variables d'environnement recommandées

```env
# Production
FLASK_ENV=production
SECRET_KEY=votre-cle-secrete-tres-longue-et-unique
DATABASE_URL=postgresql://user:password@localhost/devis_prod
ENCRYPTION_KEY=votre-cle-chiffrement-unique

# Email (optionnel)
SENDGRID_API_KEY=votre-cle-sendgrid
SENDGRID_FROM_EMAIL=noreply@votredomaine.com
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
