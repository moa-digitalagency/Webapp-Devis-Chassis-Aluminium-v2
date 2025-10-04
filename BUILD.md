# Instructions de Build

## Prérequis

### 1. Binary Tailwind CSS (obligatoire)

Le binary Tailwind CSS n'est **pas inclus dans Git** (trop volumineux - 116MB). Vous devez le télécharger :

#### Linux (x86_64 - Replit)
```bash
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
chmod +x tailwindcss-linux-x64
mv tailwindcss-linux-x64 tailwindcss
```

#### macOS (Apple Silicon)
```bash
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64
chmod +x tailwindcss-macos-arm64
mv tailwindcss-macos-arm64 tailwindcss
```

#### macOS (Intel)
```bash
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-x64
chmod +x tailwindcss-macos-x64
mv tailwindcss-macos-x64 tailwindcss
```

#### Windows
```powershell
Invoke-WebRequest -Uri "https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-windows-x64.exe" -OutFile "tailwindcss.exe"
```

### 2. Dépendances Python

```bash
pip install -r requirements.txt
```

## Build CSS

### Option 1 : Script Python (recommandé)
```bash
python build_css.py
```

### Option 2 : Binary directement
```bash
./tailwindcss -i app/static/css/tailwind-input.css -o app/static/css/tailwind.css --minify
```

### Option 3 : Mode watch (développement)
```bash
python build_css.py --watch
```

## Lancement de l'application

```bash
python main.py
```

L'application sera accessible sur http://localhost:5000

## Notes importantes

- **100% Python** - Aucune dépendance Node.js requise
- Le binary Tailwind CSS est dans `.gitignore` et doit être téléchargé manuellement
- Configuration Tailwind via CSS pur (pas de `tailwind.config.js`)
- Utilisez `build_css.py` pour rebuilder le CSS après modifications
