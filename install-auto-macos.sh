#!/bin/bash
# Installation automatique macOS - PWA Devis Menuiserie
# Aucune interaction requise - Credentials générés automatiquement

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear
echo -e "${CYAN}"
cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     🚀 PWA DEVIS MENUISERIE - INSTALLATION AUTO           ║
║                                                            ║
║     Installation 100% automatique avec credentials        ║
║     sécurisés générés aléatoirement                       ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

# Générer credentials sécurisés
echo -e "${YELLOW}🔐 Génération des credentials sécurisés...${NC}"
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
SECRET_KEY=$(openssl rand -hex 32)
ADMIN_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-16)
SUPERADMIN_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-16)

# Vérifier Homebrew
if ! command -v brew &> /dev/null; then
    echo -e "${YELLOW}📦 Installation de Homebrew...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Installer Python et dépendances
echo -e "${GREEN}📦 Installation de Python 3.11...${NC}"
brew install python@3.11 git 2>/dev/null || true

# Répertoire installation
INSTALL_DIR="$HOME/DevisApp"
echo -e "${GREEN}📁 Création du répertoire: ${INSTALL_DIR}${NC}"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Cloner projet
echo -e "${GREEN}📥 Téléchargement de l'application...${NC}"
if [ -d "Webapp-Devis-Chassis-Aluminium-v2" ]; then
    cd Webapp-Devis-Chassis-Aluminium-v2
    git pull -q
else
    git clone -q https://github.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium-v2
    cd Webapp-Devis-Chassis-Aluminium-v2
fi

# Environnement virtuel
echo -e "${GREEN}🔧 Configuration environnement Python...${NC}"
python3.11 -m venv .venv
source .venv/bin/activate

# Installer dépendances
echo -e "${GREEN}📦 Installation des dépendances...${NC}"
python -m pip install -q -U pip wheel setuptools
pip install -q -r requirements.txt
pip install -q gunicorn

# Configuration .env
echo -e "${GREEN}⚙️ Configuration application...${NC}"
cat > .env << EOF
DATABASE_URL=sqlite:///devis_menuiserie.db
SECRET_KEY=${SECRET_KEY}
FLASK_ENV=production
EOF
chmod 600 .env

# Initialiser DB avec users personnalisés
echo -e "${GREEN}🗄️ Initialisation base de données...${NC}"
python << PYEOF
from app import create_app, db
from app.models import User, Company
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    db.create_all()
    
    company = Company.query.first()
    if not company:
        company = Company(
            name='Entreprise par défaut',
            is_approved=True,
            is_active=True
        )
        db.session.add(company)
        db.session.commit()
    
    if not User.query.filter_by(username='superadmin').first():
        superadmin = User(
            username='superadmin',
            email='superadmin@devis.local',
            password_hash=generate_password_hash('${SUPERADMIN_PASSWORD}'),
            role='super_admin',
            company_id=company.id,
            is_active=True
        )
        db.session.add(superadmin)
    
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@devis.local',
            password_hash=generate_password_hash('${ADMIN_PASSWORD}'),
            role='admin',
            company_id=company.id,
            is_active=True
        )
        db.session.add(admin)
    
    db.session.commit()
    print("✅ Base de données initialisée")
PYEOF

# Créer script de lancement
echo -e "${GREEN}🚀 Configuration du service...${NC}"
cat > ~/DevisApp/start-devisapp.sh << 'STARTEOF'
#!/bin/bash
cd ~/DevisApp/Webapp-Devis-Chassis-Aluminium-v2
source .venv/bin/activate
gunicorn -w 4 -b 127.0.0.1:5000 --reuse-port main:app
STARTEOF
chmod +x ~/DevisApp/start-devisapp.sh

# Créer LaunchAgent pour démarrage auto
mkdir -p ~/Library/LaunchAgents
cat > ~/Library/LaunchAgents/com.devisapp.plist << PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.devisapp</string>
    <key>ProgramArguments</key>
    <array>
        <string>${HOME}/DevisApp/start-devisapp.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>${HOME}/DevisApp/Webapp-Devis-Chassis-Aluminium-v2</string>
    <key>StandardOutPath</key>
    <string>${HOME}/DevisApp/devisapp.log</string>
    <key>StandardErrorPath</key>
    <string>${HOME}/DevisApp/devisapp-error.log</string>
</dict>
</plist>
PLISTEOF

# Charger le service
launchctl unload ~/Library/LaunchAgents/com.devisapp.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.devisapp.plist

# Obtenir IP local
LOCAL_IP=$(ipconfig getifaddr en0 || ipconfig getifaddr en1 || echo "localhost")

# Sauvegarder credentials
CRED_FILE="$HOME/Desktop/DevisApp_Credentials.txt"
cat > "${CRED_FILE}" << CREDEOF
═══════════════════════════════════════════════════════════════
  🔐 CREDENTIALS - PWA DEVIS MENUISERIE
═══════════════════════════════════════════════════════════════

📅 Date installation: $(date)
🖥️  Serveur IP: ${LOCAL_IP}

─────────────────────────────────────────────────────────────

🌐 ACCÈS APPLICATION
   URL Local: http://localhost:5000
   URL Réseau: http://${LOCAL_IP}:5000

👑 SUPER ADMINISTRATEUR
   Username: superadmin
   Password: ${SUPERADMIN_PASSWORD}
   Email: superadmin@devis.local

👤 ADMINISTRATEUR
   Username: admin
   Password: ${ADMIN_PASSWORD}
   Email: admin@devis.local

─────────────────────────────────────────────────────────────

🗄️  BASE DE DONNÉES SQLITE
   Fichier: devis_menuiserie.db
   Path: ${INSTALL_DIR}/Webapp-Devis-Chassis-Aluminium-v2/devis_menuiserie.db

─────────────────────────────────────────────────────────────

🔑 CLÉS DE SÉCURITÉ
   SECRET_KEY: ${SECRET_KEY}

─────────────────────────────────────────────────────────────

⚙️  COMMANDES UTILES
   Démarrer:  launchctl load ~/Library/LaunchAgents/com.devisapp.plist
   Arrêter:   launchctl unload ~/Library/LaunchAgents/com.devisapp.plist
   Logs:      tail -f ~/DevisApp/devisapp.log
   Erreurs:   tail -f ~/DevisApp/devisapp-error.log

─────────────────────────────────────────────────────────────

⚠️  SÉCURITÉ
   - Changez les mots de passe après première connexion
   - Fichier sauvegardé: ${CRED_FILE}
   - Installation: ${INSTALL_DIR}/Webapp-Devis-Chassis-Aluminium-v2

═══════════════════════════════════════════════════════════════
CREDEOF

chmod 600 "${CRED_FILE}"

# Afficher résultat
sleep 2
clear
echo -e "${GREEN}"
cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║           ✅ INSTALLATION TERMINÉE AVEC SUCCÈS            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

cat "${CRED_FILE}"

echo -e "\n${YELLOW}📋 Credentials sauvegardés sur le Bureau: DevisApp_Credentials.txt${NC}"
echo -e "${GREEN}\n✅ Application démarrée automatiquement${NC}"
echo -e "${CYAN}\n🌐 Accès: http://localhost:5000${NC}\n"

# Ouvrir navigateur
sleep 2
open http://localhost:5000
