import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
import json
from flask import current_app

class BackupService:
    """Service de gestion des sauvegardes de base de données et fichiers critiques"""
    
    def __init__(self, backup_dir=None):
        self.backup_dir = backup_dir or os.environ.get('BACKUP_DIR', 'backups')
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
        self.catalog_file = os.path.join(self.backup_dir, 'backup_catalog.json')
        
    def get_database_type(self):
        """Détermine le type de base de données (SQLite ou PostgreSQL)"""
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if database_url.startswith('sqlite'):
            return 'sqlite'
        elif database_url.startswith('postgresql'):
            return 'postgresql'
        return 'unknown'
    
    def create_backup(self, description="Backup manuel"):
        """Crée une sauvegarde complète de la base de données"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        db_type = self.get_database_type()
        
        backup_info = {
            'timestamp': timestamp,
            'datetime': datetime.now().isoformat(),
            'description': description,
            'database_type': db_type,
            'files': []
        }
        
        try:
            if db_type == 'sqlite':
                backup_file = self._backup_sqlite(timestamp)
                backup_info['files'].append(backup_file)
            elif db_type == 'postgresql':
                backup_file = self._backup_postgresql(timestamp)
                backup_info['files'].append(backup_file)
            else:
                raise ValueError(f"Type de base de données non supporté: {db_type}")
            
            backup_info['success'] = True
            backup_info['size'] = os.path.getsize(backup_file)
            
            self._update_catalog(backup_info)
            self._cleanup_old_backups()
            
            return {
                'success': True,
                'backup_file': backup_file,
                'timestamp': timestamp,
                'size': backup_info['size']
            }
            
        except Exception as e:
            backup_info['success'] = False
            backup_info['error'] = str(e)
            self._update_catalog(backup_info)
            raise
    
    def _backup_sqlite(self, timestamp):
        """Sauvegarde une base SQLite"""
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        db_path = database_url.replace('sqlite:///', '')
        
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Base de données SQLite introuvable: {db_path}")
        
        backup_filename = f"backup_sqlite_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        shutil.copy2(db_path, backup_path)
        
        return backup_path
    
    def _backup_postgresql(self, timestamp):
        """Sauvegarde une base PostgreSQL avec pg_dump"""
        backup_filename = f"backup_postgresql_{timestamp}.sql"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        pg_host = os.environ.get('PGHOST', 'localhost')
        pg_port = os.environ.get('PGPORT', '5432')
        pg_user = os.environ.get('PGUSER')
        pg_password = os.environ.get('PGPASSWORD')
        pg_database = os.environ.get('PGDATABASE')
        
        if not all([pg_user, pg_password, pg_database]):
            raise ValueError("Variables PostgreSQL manquantes (PGUSER, PGPASSWORD, PGDATABASE)")
        
        env = os.environ.copy()
        if pg_password:
            env['PGPASSWORD'] = pg_password
        
        cmd = [
            'pg_dump',
            '-h', pg_host,
            '-p', pg_port,
            '-U', pg_user,
            '-F', 'c',
            '-f', backup_path,
            pg_database
        ]
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Échec du backup PostgreSQL: {result.stderr}")
        
        return backup_path
    
    def list_backups(self):
        """Liste toutes les sauvegardes disponibles"""
        if not os.path.exists(self.catalog_file):
            return []
        
        with open(self.catalog_file, 'r') as f:
            catalog = json.load(f)
        
        return sorted(catalog, key=lambda x: x['datetime'], reverse=True)
    
    def restore_backup(self, backup_file):
        """Restaure une sauvegarde (à implémenter avec précaution)"""
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Fichier de sauvegarde introuvable: {backup_file}")
        
        db_type = self.get_database_type()
        
        if db_type == 'sqlite':
            return self._restore_sqlite(backup_file)
        elif db_type == 'postgresql':
            return self._restore_postgresql(backup_file)
        else:
            raise ValueError(f"Type de base de données non supporté: {db_type}")
    
    def _restore_sqlite(self, backup_file):
        """Restaure une base SQLite (ATTENTION: Requiert redémarrage de l'application)"""
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        db_path = database_url.replace('sqlite:///', '')
        
        backup_current = f"{db_path}.before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(db_path, backup_current)
        
        shutil.copy2(backup_file, db_path)
        
        return {
            'success': True, 
            'message': 'Base SQLite restaurée avec succès. REDÉMARRAGE DE L\'APPLICATION REQUIS.',
            'requires_restart': True
        }
    
    def _restore_postgresql(self, backup_file):
        """Restaure une base PostgreSQL avec pg_restore"""
        pg_host = os.environ.get('PGHOST', 'localhost')
        pg_port = os.environ.get('PGPORT', '5432')
        pg_user = os.environ.get('PGUSER')
        pg_password = os.environ.get('PGPASSWORD')
        pg_database = os.environ.get('PGDATABASE')
        
        env = os.environ.copy()
        if pg_password:
            env['PGPASSWORD'] = pg_password
        
        cmd = [
            'pg_restore',
            '-h', pg_host,
            '-p', pg_port,
            '-U', pg_user,
            '-d', pg_database,
            '--clean',
            '--if-exists',
            backup_file
        ]
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Échec de la restauration PostgreSQL: {result.stderr}")
        
        return {'success': True, 'message': 'Base PostgreSQL restaurée avec succès'}
    
    def _update_catalog(self, backup_info):
        """Met à jour le catalogue des sauvegardes"""
        catalog = []
        if os.path.exists(self.catalog_file):
            with open(self.catalog_file, 'r') as f:
                catalog = json.load(f)
        
        catalog.append(backup_info)
        
        with open(self.catalog_file, 'w') as f:
            json.dump(catalog, f, indent=2)
    
    def _cleanup_old_backups(self, keep_last=10):
        """Supprime les anciennes sauvegardes (conserve les N dernières)"""
        backups = self.list_backups()
        
        if len(backups) <= keep_last:
            return
        
        to_delete = backups[keep_last:]
        
        for backup in to_delete:
            if backup.get('success') and backup.get('files'):
                for file_path in backup['files']:
                    if os.path.exists(file_path):
                        os.remove(file_path)
        
        catalog = backups[:keep_last]
        with open(self.catalog_file, 'w') as f:
            json.dump(catalog, f, indent=2)
    
    def get_backup_stats(self):
        """Retourne des statistiques sur les sauvegardes"""
        backups = self.list_backups()
        
        total_size = sum(b.get('size', 0) for b in backups if b.get('success'))
        successful = len([b for b in backups if b.get('success')])
        failed = len([b for b in backups if not b.get('success')])
        
        return {
            'total_backups': len(backups),
            'successful': successful,
            'failed': failed,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'latest_backup': backups[0] if backups else None
        }
