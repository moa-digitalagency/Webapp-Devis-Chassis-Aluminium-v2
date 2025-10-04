# 🚀 Installation VPS en 1 commande

## Installation automatique complète

Connectez-vous à votre VPS en SSH, puis lancez cette commande :

```bash
curl -fsSL https://raw.githubusercontent.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium-v2/main/install-vps.sh | sudo bash
```

**OU téléchargez puis exécutez :**

```bash
wget https://raw.githubusercontent.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium-v2/main/install-vps.sh
chmod +x install-vps.sh
sudo ./install-vps.sh
```

## Ce que fait le script automatiquement

✅ Installe Python 3.11, PostgreSQL, Nginx  
✅ Configure la base de données  
✅ Installe l'application et toutes les dépendances  
✅ Configure le service systemd (démarrage automatique)  
✅ Configure Nginx comme reverse proxy  
✅ Configure SSL/HTTPS avec Let's Encrypt  

## Informations demandées

Le script vous demandera :
1. **Nom de domaine** : `devis.example.com`
2. **Email** : Pour le certificat SSL
3. **Mot de passe** : Pour la base de données PostgreSQL

## Après l'installation

🌐 **Accédez à votre application** : `https://votre-domaine.com`

👤 **Identifiants par défaut** :
- Super Admin : `superadmin` / `admin123`
- Admin : `admin / admin123`

⚠️ **Important** : Changez ces mots de passe dès la première connexion !

## Commandes utiles

```bash
# Voir le statut du service
sudo systemctl status devisapp

# Redémarrer l'application
sudo systemctl restart devisapp

# Voir les logs en temps réel
sudo journalctl -u devisapp -f

# Redémarrer Nginx
sudo systemctl restart nginx
```

## Systèmes supportés

- ✅ Ubuntu 20.04 / 22.04 / 24.04
- ✅ Debian 11 / 12
- ✅ CentOS 8+
- ✅ RHEL 8+
- ✅ Fedora

## Temps d'installation

⏱️ Environ **5-10 minutes** selon votre connexion VPS

---

**En cas de problème** : Consultez les logs avec `sudo journalctl -u devisapp -n 50`
