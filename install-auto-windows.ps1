# Installation automatique Windows - PWA Devis Menuiserie
# Aucune interaction requise - Credentials générés automatiquement

#Requires -RunAsAdministrator

Clear-Host
Write-Host @"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     🚀 PWA DEVIS MENUISERIE - INSTALLATION AUTO           ║
║                                                            ║
║     Installation 100% automatique avec credentials        ║
║     sécurisés générés aléatoirement                       ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Vérifier Python
Write-Host "`n🔍 Vérification de Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python non installé. Installation via winget..." -ForegroundColor Red
    winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Vérifier Git
Write-Host "🔍 Vérification de Git..." -ForegroundColor Yellow
$gitVersion = git --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git non installé. Installation via winget..." -ForegroundColor Red
    winget install Git.Git --silent --accept-package-agreements --accept-source-agreements
}

# Générer credentials sécurisés
Write-Host "`n🔐 Génération des credentials sécurisés..." -ForegroundColor Yellow
$DB_PASSWORD = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
$SECRET_KEY = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
$ADMIN_PASSWORD = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 16 | ForEach-Object {[char]$_})
$SUPERADMIN_PASSWORD = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 16 | ForEach-Object {[char]$_})

# Créer répertoire installation
$installPath = "C:\DevisApp"
Write-Host "`n📁 Création du répertoire: $installPath" -ForegroundColor Yellow
if (-not (Test-Path $installPath)) {
    New-Item -ItemType Directory -Path $installPath | Out-Null
}

# Cloner ou mettre à jour
Write-Host "📥 Téléchargement de l'application..." -ForegroundColor Green
Set-Location $installPath
if (Test-Path "Webapp-Devis-Chassis-Aluminium-v2") {
    Set-Location "Webapp-Devis-Chassis-Aluminium-v2"
    git pull
} else {
    git clone https://github.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium-v2
    Set-Location "Webapp-Devis-Chassis-Aluminium-v2"
}

# Créer environnement virtuel
Write-Host "🔧 Configuration environnement Python..." -ForegroundColor Green
python -m venv .venv
& ".\.venv\Scripts\Activate.ps1"

# Installer dépendances
Write-Host "📦 Installation des dépendances..." -ForegroundColor Green
python -m pip install -q -U pip wheel setuptools
pip install -q -r requirements.txt
pip install -q waitress

# Créer .env
Write-Host "⚙️ Configuration application..." -ForegroundColor Green
@"
DATABASE_URL=sqlite:///devis_menuiserie.db
SECRET_KEY=$SECRET_KEY
FLASK_ENV=production
"@ | Out-File -FilePath .env -Encoding utf8

# Initialiser DB avec users personnalisés
Write-Host "🗄️ Initialisation base de données..." -ForegroundColor Green
python -c @"
from app import create_app, db
from app.models import User, Company
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    db.create_all()
    
    company = Company.query.first()
    if not company:
        company = Company(name='Entreprise par défaut', is_approved=True, is_active=True)
        db.session.add(company)
        db.session.commit()
    
    if not User.query.filter_by(username='superadmin').first():
        superadmin = User(
            username='superadmin',
            email='superadmin@devis.local',
            password_hash=generate_password_hash('$SUPERADMIN_PASSWORD'),
            role='super_admin',
            company_id=company.id,
            is_active=True
        )
        db.session.add(superadmin)
    
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@devis.local',
            password_hash=generate_password_hash('$ADMIN_PASSWORD'),
            role='admin',
            company_id=company.id,
            is_active=True
        )
        db.session.add(admin)
    
    db.session.commit()
"@

# Créer service Windows avec NSSM
Write-Host "🔧 Configuration du service Windows..." -ForegroundColor Green
$nssmPath = "$installPath\nssm.exe"
if (-not (Test-Path $nssmPath)) {
    Write-Host "📥 Téléchargement NSSM..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile "$installPath\nssm.zip"
    Expand-Archive -Path "$installPath\nssm.zip" -DestinationPath $installPath -Force
    Copy-Item "$installPath\nssm-2.24\win64\nssm.exe" -Destination $nssmPath
    Remove-Item "$installPath\nssm.zip" -Force
    Remove-Item "$installPath\nssm-2.24" -Recurse -Force
}

# Supprimer service s'il existe
& $nssmPath stop DevisApp 2>$null
& $nssmPath remove DevisApp confirm 2>$null

# Créer le service
& $nssmPath install DevisApp "$installPath\Webapp-Devis-Chassis-Aluminium-v2\.venv\Scripts\python.exe"
& $nssmPath set DevisApp AppParameters "-m waitress --host=0.0.0.0 --port=5000 main:app"
& $nssmPath set DevisApp AppDirectory "$installPath\Webapp-Devis-Chassis-Aluminium-v2"
& $nssmPath set DevisApp DisplayName "PWA Devis Menuiserie"
& $nssmPath set DevisApp Description "Application de devis menuiserie aluminium"
& $nssmPath set DevisApp Start SERVICE_AUTO_START
& $nssmPath start DevisApp

# Configurer pare-feu
Write-Host "🔥 Configuration du pare-feu..." -ForegroundColor Green
New-NetFirewallRule -DisplayName "DevisApp HTTP" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow -ErrorAction SilentlyContinue

# Obtenir IP
$IP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"} | Select-Object -First 1).IPAddress

# Sauvegarder credentials
$credFile = "$env:USERPROFILE\Desktop\DevisApp_Credentials.txt"
@"
═══════════════════════════════════════════════════════════════
  🔐 CREDENTIALS - PWA DEVIS MENUISERIE
═══════════════════════════════════════════════════════════════

📅 Date installation: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
🖥️  Serveur IP: $IP

─────────────────────────────────────────────────────────────

🌐 ACCÈS APPLICATION
   URL: http://${IP}:5000
   URL Local: http://localhost:5000

👑 SUPER ADMINISTRATEUR
   Username: superadmin
   Password: $SUPERADMIN_PASSWORD
   Email: superadmin@devis.local

👤 ADMINISTRATEUR
   Username: admin
   Password: $ADMIN_PASSWORD
   Email: admin@devis.local

─────────────────────────────────────────────────────────────

🗄️  BASE DE DONNÉES SQLITE
   Fichier: devis_menuiserie.db
   Path: $installPath\Webapp-Devis-Chassis-Aluminium-v2\devis_menuiserie.db

─────────────────────────────────────────────────────────────

🔑 CLÉS DE SÉCURITÉ
   SECRET_KEY: $SECRET_KEY

─────────────────────────────────────────────────────────────

⚙️  COMMANDES UTILES
   Status Service:     Get-Service DevisApp
   Restart Service:    Restart-Service DevisApp
   Stop Service:       Stop-Service DevisApp
   Logs Application:   Get-EventLog -LogName Application -Source DevisApp

─────────────────────────────────────────────────────────────

⚠️  SÉCURITÉ
   - Changez les mots de passe après première connexion
   - Fichier sauvegardé: $credFile
   - Installation: $installPath\Webapp-Devis-Chassis-Aluminium-v2

═══════════════════════════════════════════════════════════════
"@ | Out-File -FilePath $credFile -Encoding UTF8

# Afficher résultat
Clear-Host
Write-Host @"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║           ✅ INSTALLATION TERMINÉE AVEC SUCCÈS            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Green

Get-Content $credFile

Write-Host "`n📋 Credentials sauvegardés sur le Bureau: DevisApp_Credentials.txt" -ForegroundColor Yellow
Write-Host "`n🌐 Accès: http://localhost:5000" -ForegroundColor Cyan
Write-Host "   ou:    http://${IP}:5000" -ForegroundColor Cyan

$service = Get-Service DevisApp -ErrorAction SilentlyContinue
if ($service.Status -eq 'Running') {
    Write-Host "`n✅ Service démarré avec succès" -ForegroundColor Green
} else {
    Write-Host "`n❌ Erreur au démarrage du service" -ForegroundColor Red
}

Write-Host "`nAppuyez sur une touche pour ouvrir l'application..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
Start-Process "http://localhost:5000"
