#!/bin/bash
# Script d'installation et configuration automatique pour VPS
# Compatible: Ubuntu 20.04+, Debian 11+, CentOS 8+
# Usage: sudo bash install-vps.sh

set -e

# Couleurs pour affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════╗"
echo "║   🚀 Installation PWA Devis Menuiserie        ║"
echo "║   Installation automatique sur VPS            ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

# Vérifier si exécuté en tant que root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Ce script doit être exécuté en tant que root (sudo)${NC}"
    exit 1
fi

# Demander les informations de configuration
echo -e "${YELLOW}📋 Configuration initiale${NC}"
read -p "Nom de domaine (ex: devis.example.com) : " DOMAIN_NAME
read -p "Email pour SSL Let's Encrypt : " SSL_EMAIL
read -p "Mot de passe PostgreSQL pour l'application : " -s DB_PASSWORD
echo ""

# Générer une clé secrète
SECRET_KEY=$(openssl rand -hex 32)

# Détecter la distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

echo -e "${GREEN}📦 Installation des dépendances système...${NC}"
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt update && apt upgrade -y
    apt install -y software-properties-common
    add-apt-repository ppa:deadsnakes/ppa -y
    apt update
    apt install -y python3.11 python3.11-venv python3-pip git nginx postgresql postgresql-contrib certbot python3-certbot-nginx
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ] || [ "$OS" = "fedora" ]; then
    dnf update -y
    dnf install -y python3.11 python3-pip git nginx postgresql-server postgresql-contrib certbot python3-certbot-nginx
    postgresql-setup --initdb
    systemctl start postgresql
    systemctl enable postgresql
fi

echo -e "${GREEN}👤 Création de l'utilisateur devisapp...${NC}"
if ! id "devisapp" &>/dev/null; then
    useradd -m -s /bin/bash devisapp
fi

echo -e "${GREEN}📥 Téléchargement de l'application...${NC}"
sudo -u devisapp bash << 'USEREOF'
cd ~
if [ -d "Webapp-Devis-Chassis-Aluminium-v2" ]; then
    echo "Mise à jour du projet existant..."
    cd Webapp-Devis-Chassis-Aluminium-v2
    git pull
else
    git clone https://github.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium-v2
    cd Webapp-Devis-Chassis-Aluminium-v2
fi

echo "🔧 Configuration de l'environnement virtuel..."
python3.11 -m venv .venv
source .venv/bin/activate

echo "📦 Installation des dépendances Python..."
python -m pip install -U pip wheel setuptools
pip install -r requirements.txt
pip install gunicorn
USEREOF

echo -e "${GREEN}🗄️ Configuration de PostgreSQL...${NC}"
sudo -u postgres psql << SQLEOF
-- Supprimer l'utilisateur s'il existe déjà
DROP USER IF EXISTS devisuser;
DROP DATABASE IF EXISTS devis_menuiserie;

-- Créer la base de données et l'utilisateur
CREATE USER devisuser WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE devis_menuiserie OWNER devisuser;
GRANT ALL PRIVILEGES ON DATABASE devis_menuiserie TO devisuser;
SQLEOF

echo -e "${GREEN}⚙️ Configuration de l'application...${NC}"
sudo -u devisapp bash << ENVEOF
cd ~/Webapp-Devis-Chassis-Aluminium-v2
cat > .env << EOF
DATABASE_URL=postgresql://devisuser:$DB_PASSWORD@localhost/devis_menuiserie
SECRET_KEY=$SECRET_KEY
FLASK_ENV=production
EOF
chmod 600 .env
ENVEOF

echo -e "${GREEN}🔧 Configuration du service systemd...${NC}"
cat > /etc/systemd/system/devisapp.service << 'SERVICEEOF'
[Unit]
Description=PWA Devis Menuiserie Application
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

echo -e "${GREEN}🌐 Configuration de Nginx...${NC}"
cat > /etc/nginx/sites-available/devisapp << NGINXEOF
server {
    listen 80;
    server_name $DOMAIN_NAME;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }

    location /static {
        alias /home/devisapp/Webapp-Devis-Chassis-Aluminium-v2/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Favicon
    location = /static/favicon.ico {
        alias /home/devisapp/Webapp-Devis-Chassis-Aluminium-v2/app/static/favicon.ico;
        expires 30d;
    }
}
NGINXEOF

# Activer le site
ln -sf /etc/nginx/sites-available/devisapp /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Tester la configuration Nginx
nginx -t

echo -e "${GREEN}🚀 Démarrage des services...${NC}"
systemctl daemon-reload
systemctl start devisapp
systemctl enable devisapp
systemctl restart nginx

# Vérifier le statut
sleep 2
if systemctl is-active --quiet devisapp; then
    echo -e "${GREEN}✅ Service devisapp démarré avec succès${NC}"
else
    echo -e "${RED}❌ Erreur au démarrage du service${NC}"
    journalctl -u devisapp -n 20
fi

echo -e "${GREEN}🔒 Configuration SSL avec Let's Encrypt...${NC}"
certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --email $SSL_EMAIL --redirect

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════╗"
echo "║   ✅ Installation terminée avec succès !       ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}📋 Informations importantes :${NC}"
echo -e "🌐 URL de l'application : ${GREEN}https://$DOMAIN_NAME${NC}"
echo -e "👤 Identifiants par défaut :"
echo -e "   - Super Admin: ${YELLOW}superadmin / admin123${NC}"
echo -e "   - Admin: ${YELLOW}admin / admin123${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT : Changez ces mots de passe dès la première connexion !${NC}"
echo ""
echo -e "${BLUE}🔧 Commandes utiles :${NC}"
echo -e "   Statut du service : ${GREEN}sudo systemctl status devisapp${NC}"
echo -e "   Redémarrer        : ${GREEN}sudo systemctl restart devisapp${NC}"
echo -e "   Logs              : ${GREEN}sudo journalctl -u devisapp -f${NC}"
echo -e "   Nginx             : ${GREEN}sudo systemctl status nginx${NC}"
echo ""
echo -e "${GREEN}🎉 Votre application est maintenant en ligne !${NC}"
