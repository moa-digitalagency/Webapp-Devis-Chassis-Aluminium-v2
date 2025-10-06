# Déploiement sur Railway 🚂

## 🔧 Configuration requise

### 1. Variables d'environnement obligatoires

Sur Railway, configurez ces variables dans l'onglet **Variables** :

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

### 3. CORS (Optionnel)

L'application détecte automatiquement le domaine Railway (`RAILWAY_PUBLIC_DOMAIN`).

Si vous devez spécifier manuellement :
```bash
ALLOWED_ORIGINS=https://votre-app.up.railway.app
```

Pour plusieurs domaines :
```bash
ALLOWED_ORIGINS=https://app1.com,https://app2.com
```

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

### "Erreur de connexion au serveur"
- Vérifiez que SECRET_KEY et ENCRYPTION_KEY sont configurées
- Vérifiez que PostgreSQL est ajouté au projet
- Consultez les logs Railway pour les erreurs spécifiques

### Sessions ne fonctionnent pas
- Vérifiez que SECRET_KEY est configurée
- Vérifiez que CORS est correctement configuré

### Données chiffrées illisibles
- Vous avez probablement changé ENCRYPTION_KEY
- Restaurez l'ancienne clé ou régénérez les données

## 📚 Documentation

Pour plus d'informations, consultez :
- [Railway Documentation](https://docs.railway.app/)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/latest/deploying/)
