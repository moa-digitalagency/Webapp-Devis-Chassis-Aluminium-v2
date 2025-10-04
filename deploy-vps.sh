#!/bin/bash
# Script d'installation automatique pour VPS/Serveur Linux
# Compatible: Ubuntu 20.04+, Debian 11+, CentOS 8+

set -e

echo "🚀 Installation PWA Devis Menuiserie sur VPS"
echo "=============================================="

# Détecter la distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
fi

echo "📦 Mise à jour du système..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3-pip git nginx postgresql postgresql-contrib
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ] || [ "$OS" = "fedora" ]; then
    sudo dnf update -y
    sudo dnf install -y python3.11 python3-pip git nginx postgresql-server postgresql-contrib
    sudo postgresql-setup --initdb
fi

echo "👤 Création utilisateur devisapp..."
if ! id "devisapp" &>/dev/null; then
    sudo useradd -m -s /bin/bash devisapp
fi

echo "📥 Clonage du projet..."
sudo -u devisapp bash << 'USEREOF'
cd ~
if [ -d "Webapp-Devis-Chassis-Aluminium-v2" ]; then
    echo "Le répertoire existe déjà. Mise à jour..."
    cd Webapp-Devis-Chassis-Aluminium-v2
    git pull
else
    git clone https://github.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium-v2
    cd Webapp-Devis-Chassis-Aluminium-v2
fi

echo "🔧 Configuration environnement virtuel..."
python3.11 -m venv .venv
source .venv/bin/activate

echo "📦 Installation des dépendances..."
python -m pip install -U pip wheel setuptools
pip install -r requirements.txt
pip install gunicorn

echo "✅ Installation terminée!"
USEREOF

echo ""
echo "🎉 Installation terminée avec succès!"
echo ""
echo "📋 Prochaines étapes:"
echo "1. Configurer PostgreSQL et créer la base de données"
echo "2. Créer le fichier .env avec DATABASE_URL et SECRET_KEY"
echo "3. Configurer le service systemd (voir README.md)"
echo "4. Configurer Nginx (voir README.md)"
echo ""
echo "Pour plus d'informations, consultez le README.md"
