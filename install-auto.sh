#!/bin/bash
# Installation automatique VPS - PWA Devis Menuiserie
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

# Vérifier root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Exécutez avec sudo${NC}"
    exit 1
fi

# Générer credentials sécurisés
echo -e "${YELLOW}🔐 Génération des credentials sécurisés...${NC}"
DB_USER="devisapp_$(openssl rand -hex 4)"
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
SECRET_KEY=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null || openssl rand -base64 32)
ADMIN_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-16)
SUPERADMIN_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-16)

# Détecter OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

echo -e "${GREEN}📦 Installation des dépendances (${OS})...${NC}"
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    export DEBIAN_FRONTEND=noninteractive
    apt update -qq
    apt install -y -qq software-properties-common
    add-apt-repository ppa:deadsnakes/ppa -y
    apt update -qq
    apt install -y -qq python3.11 python3.11-venv python3-pip git nginx postgresql postgresql-contrib ufw
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ] || [ "$OS" = "fedora" ]; then
    dnf install -y -q python3.11 python3-pip git nginx postgresql-server postgresql-contrib firewalld
    postgresql-setup --initdb
    systemctl start postgresql
    systemctl enable postgresql
fi

echo -e "${GREEN}👤 Configuration utilisateur système...${NC}"
if ! id "devisapp" &>/dev/null; then
    useradd -m -s /bin/bash devisapp
fi

echo -e "${GREEN}📥 Installation application...${NC}"
sudo -u devisapp bash << 'USEREOF'
cd ~
if [ -d "Webapp-Devis-Chassis-Aluminium-v2" ]; then
    cd Webapp-Devis-Chassis-Aluminium-v2
    git pull -q
else
    git clone -q https://github.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium-v2
    cd Webapp-Devis-Chassis-Aluminium-v2
fi

python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -q -U pip wheel setuptools
pip install -q -r requirements.txt
pip install -q gunicorn
USEREOF

echo -e "${GREEN}🗄️ Configuration PostgreSQL...${NC}"
sudo -u postgres psql -q << SQLEOF
DROP DATABASE IF EXISTS devis_menuiserie;
DROP USER IF EXISTS ${DB_USER};
CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';
CREATE DATABASE devis_menuiserie OWNER ${DB_USER};
GRANT ALL PRIVILEGES ON DATABASE devis_menuiserie TO ${DB_USER};
SQLEOF

echo -e "${GREEN}⚙️ Configuration application...${NC}"
sudo -u devisapp bash << ENVEOF
cd ~/Webapp-Devis-Chassis-Aluminium-v2
cat > .env << EOF
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@localhost/devis_menuiserie
SECRET_KEY=${SECRET_KEY}
ENCRYPTION_KEY=${ENCRYPTION_KEY}
FLASK_ENV=production
EOF
chmod 600 .env

# Initialiser DB et créer users avec mots de passe personnalisés
source .venv/bin/activate
python << PYEOF
from app import create_app, db
from app.models import User, Company
from werkzeug.security import generate_password_hash
import sys

app = create_app()
with app.app_context():
    db.create_all()
    
    # Créer entreprise par défaut
    company = Company.query.first()
    if not company:
        company = Company(
            name="Entreprise par défaut",
            is_approved=True,
            is_active=True
        )
        db.session.add(company)
        db.session.commit()
    
    # Super Admin
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
    
    # Admin
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
ENVEOF

echo -e "${GREEN}🔧 Configuration service systemd...${NC}"
cat > /etc/systemd/system/devisapp.service << 'SERVICEEOF'
[Unit]
Description=PWA Devis Menuiserie
After=network.target postgresql.service

[Service]
Type=notify
User=devisapp
Group=devisapp
WorkingDirectory=/home/devisapp/Webapp-Devis-Chassis-Aluminium-v2
Environment="PATH=/home/devisapp/Webapp-Devis-Chassis-Aluminium-v2/.venv/bin"
ExecStart=/home/devisapp/Webapp-Devis-Chassis-Aluminium-v2/.venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 --reuse-port main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

echo -e "${GREEN}🌐 Configuration Nginx...${NC}"
SERVER_IP=$(hostname -I | awk '{print $1}')
cat > /etc/nginx/sites-available/devisapp << NGINXEOF
server {
    listen 80 default_server;
    server_name ${SERVER_IP} _;
    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /home/devisapp/Webapp-Devis-Chassis-Aluminium-v2/app/static;
        expires 30d;
    }
}
NGINXEOF

ln -sf /etc/nginx/sites-available/devisapp /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t -q

echo -e "${GREEN}🔥 Configuration firewall...${NC}"
if command -v ufw &> /dev/null; then
    ufw --force enable
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
fi

echo -e "${GREEN}🚀 Démarrage services...${NC}"
systemctl daemon-reload
systemctl start devisapp
systemctl enable devisapp -q
systemctl restart nginx

sleep 3

# Sauvegarder credentials dans fichier sécurisé
CRED_FILE="/root/.devisapp_credentials"
cat > ${CRED_FILE} << CREDEOF
═══════════════════════════════════════════════════════════════
  🔐 CREDENTIALS - PWA DEVIS MENUISERIE
═══════════════════════════════════════════════════════════════

📅 Date installation: $(date)
🖥️  Serveur IP: ${SERVER_IP}

─────────────────────────────────────────────────────────────

🌐 ACCÈS APPLICATION
   URL: http://${SERVER_IP}

👑 SUPER ADMINISTRATEUR
   Username: superadmin
   Password: ${SUPERADMIN_PASSWORD}
   Email: superadmin@devis.local

👤 ADMINISTRATEUR
   Username: admin
   Password: ${ADMIN_PASSWORD}
   Email: admin@devis.local

─────────────────────────────────────────────────────────────

🗄️  BASE DE DONNÉES POSTGRESQL
   Database: devis_menuiserie
   User: ${DB_USER}
   Password: ${DB_PASSWORD}
   
   Connexion: psql -U ${DB_USER} -d devis_menuiserie

─────────────────────────────────────────────────────────────

🔑 CLÉS DE SÉCURITÉ
   SECRET_KEY: ${SECRET_KEY}
   ENCRYPTION_KEY: ${ENCRYPTION_KEY}

─────────────────────────────────────────────────────────────

⚙️  COMMANDES UTILES
   Status:    sudo systemctl status devisapp
   Restart:   sudo systemctl restart devisapp
   Logs:      sudo journalctl -u devisapp -f
   Nginx:     sudo systemctl status nginx

─────────────────────────────────────────────────────────────

⚠️  SÉCURITÉ
   - Changez les mots de passe après première connexion
   - Ce fichier est dans: ${CRED_FILE}
   - Supprimez ce fichier après avoir noté les credentials

═══════════════════════════════════════════════════════════════
CREDEOF

chmod 600 ${CRED_FILE}

# Afficher résultat
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

cat ${CRED_FILE}

echo -e "\n${YELLOW}📋 Credentials sauvegardés dans: ${CRED_FILE}${NC}"
echo -e "${YELLOW}   Commande pour les revoir: cat ${CRED_FILE}${NC}\n"

if systemctl is-active --quiet devisapp; then
    echo -e "${GREEN}✅ Application démarrée avec succès${NC}\n"
else
    echo -e "${RED}❌ Erreur au démarrage - Voir les logs:${NC}"
    echo -e "${YELLOW}   sudo journalctl -u devisapp -n 50${NC}\n"
fi
