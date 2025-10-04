# Script d'installation automatique pour Windows Server
# Compatible: Windows Server 2016/2019/2022

Write-Host "🚀 Installation PWA Devis Menuiserie sur Windows Server" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Vérifier si Python est installé
$pythonVersion = python --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python n'est pas installé!" -ForegroundColor Red
    Write-Host "📥 Téléchargez Python 3.11+ depuis: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Python détecté: $pythonVersion" -ForegroundColor Green

# Vérifier si Git est installé
$gitVersion = git --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git n'est pas installé!" -ForegroundColor Red
    Write-Host "📥 Téléchargez Git depuis: https://git-scm.com/downloads" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Git détecté: $gitVersion" -ForegroundColor Green

# Définir le répertoire d'installation
$installPath = "C:\inetpub\Webapp-Devis-Chassis-Aluminium-v2"

# Créer le répertoire inetpub s'il n'existe pas
if (-not (Test-Path "C:\inetpub")) {
    New-Item -ItemType Directory -Path "C:\inetpub" | Out-Null
}

# Cloner ou mettre à jour le projet
Write-Host "📥 Téléchargement du projet..." -ForegroundColor Cyan
if (Test-Path $installPath) {
    Write-Host "Le projet existe déjà. Mise à jour..." -ForegroundColor Yellow
    Set-Location $installPath
    git pull
} else {
    Set-Location "C:\inetpub"
    git clone https://github.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium-v2
    Set-Location $installPath
}

# Créer l'environnement virtuel
Write-Host "🔧 Configuration de l'environnement virtuel..." -ForegroundColor Cyan
python -m venv .venv

# Activer l'environnement virtuel
& "$installPath\.venv\Scripts\Activate.ps1"

# Mettre à jour pip et installer les dépendances
Write-Host "📦 Installation des dépendances..." -ForegroundColor Cyan
python -m pip install -U pip wheel setuptools
pip install -r requirements.txt
pip install waitress

# Créer le fichier .env s'il n'existe pas
if (-not (Test-Path ".env")) {
    Write-Host "📝 Création du fichier .env..." -ForegroundColor Cyan
    $secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})
    @"
SECRET_KEY=$secretKey
DATABASE_URL=sqlite:///devis_menuiserie.db
FLASK_ENV=production
"@ | Out-File -FilePath .env -Encoding utf8
}

Write-Host ""
Write-Host "🎉 Installation terminée avec succès!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Prochaines étapes:" -ForegroundColor Cyan
Write-Host "1. Installer NSSM depuis: https://nssm.cc/download" -ForegroundColor White
Write-Host "2. Créer le service Windows avec les commandes dans README.md" -ForegroundColor White
Write-Host "3. Configurer IIS comme reverse proxy (optionnel)" -ForegroundColor White
Write-Host ""
Write-Host "Pour démarrer manuellement:" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "  python -m waitress --port=5000 main:app" -ForegroundColor Yellow
Write-Host ""
Write-Host "L'application sera accessible sur http://localhost:5000" -ForegroundColor Green
