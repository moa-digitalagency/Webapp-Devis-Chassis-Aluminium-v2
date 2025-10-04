import os
import subprocess
import json
from datetime import datetime
from pathlib import Path
from flask import current_app
from .backup import BackupService

class UpdateService:
    """Service de mise à jour automatique depuis GitHub avec migration BD
    
    AVERTISSEMENT DE SÉCURITÉ:
    - Ce service doit être utilisé uniquement par des super administrateurs de confiance
    - L'utilisation en production nécessite des mesures de sécurité supplémentaires:
      * Protection CSRF
      * Ré-authentification avant mise à jour critique
      * Rate limiting
      * Validation stricte des URLs de repo
      * Exécution asynchrone avec monitoring
    - Recommandé: Utiliser un système CI/CD pour les déploiements production
    """
    
    def __init__(self, repo_url=None, branch=None):
        self.repo_url = repo_url or os.environ.get(
            'UPDATE_REPO_URL', 
            'https://github.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium-v2'
        )
        self.branch = branch or os.environ.get('UPDATE_BRANCH', 'main')
        self.update_log_file = 'update_history.json'
        self.backup_service = BackupService()
        
    def check_for_updates(self):
        """Vérifie si des mises à jour sont disponibles"""
        try:
            result = subprocess.run(
                ['git', 'fetch', 'origin'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f"Erreur lors de la vérification: {result.stderr}"
                }
            
            result = subprocess.run(
                ['git', 'rev-list', f'HEAD..origin/{self.branch}', '--count'],
                capture_output=True,
                text=True
            )
            
            commits_behind = int(result.stdout.strip()) if result.returncode == 0 else 0
            
            current_commit = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            latest_commit = subprocess.run(
                ['git', 'rev-parse', f'origin/{self.branch}'],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            return {
                'success': True,
                'updates_available': commits_behind > 0,
                'commits_behind': commits_behind,
                'current_commit': current_commit[:8],
                'latest_commit': latest_commit[:8]
            }
            
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Timeout lors de la vérification'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def check_git_status(self):
        """Vérifie que le dépôt Git est propre"""
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            return {
                'clean': False,
                'modified_files': result.stdout.strip().split('\n')
            }
        
        return {'clean': True}
    
    def perform_update(self, auto_backup=True, auto_migrate=True):
        """Effectue la mise à jour complète avec backup et migration"""
        update_log = {
            'timestamp': datetime.now().isoformat(),
            'steps': [],
            'success': False
        }
        
        try:
            step_log = {'step': 'check_git_status', 'success': False}
            git_status = self.check_git_status()
            
            if not git_status['clean']:
                step_log['error'] = 'Le dépôt Git a des modifications locales'
                step_log['modified_files'] = git_status['modified_files']
                update_log['steps'].append(step_log)
                raise RuntimeError(
                    "Modifications locales détectées. Veuillez les valider ou les annuler."
                )
            step_log['success'] = True
            update_log['steps'].append(step_log)
            
            if auto_backup:
                step_log = {'step': 'create_backup', 'success': False}
                backup_result = self.backup_service.create_backup(
                    description="Backup automatique avant mise à jour"
                )
                step_log['backup_file'] = backup_result['backup_file']
                step_log['success'] = True
                update_log['steps'].append(step_log)
            
            step_log = {'step': 'git_pull', 'success': False}
            result = subprocess.run(
                ['git', 'pull', 'origin', self.branch],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                step_log['error'] = result.stderr
                update_log['steps'].append(step_log)
                raise RuntimeError(f"Échec du git pull: {result.stderr}")
            
            step_log['output'] = result.stdout
            step_log['success'] = True
            update_log['steps'].append(step_log)
            
            step_log = {'step': 'install_dependencies', 'success': False}
            result = subprocess.run(
                ['pip', 'install', '-r', 'requirements.txt', '--upgrade'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                step_log['error'] = result.stderr
                update_log['steps'].append(step_log)
                raise RuntimeError(f"Échec de l'installation des dépendances: {result.stderr}")
            
            step_log['success'] = True
            update_log['steps'].append(step_log)
            
            if auto_migrate:
                step_log = {'step': 'database_migration', 'success': False}
                migration_result = self._run_database_migration()
                step_log.update(migration_result)
                step_log['success'] = migration_result.get('success', False)
                update_log['steps'].append(step_log)
                
                if not step_log['success']:
                    raise RuntimeError(f"Échec de la migration: {migration_result.get('error')}")
            
            update_log['success'] = True
            update_log['message'] = 'Mise à jour effectuée avec succès'
            
            self._log_update(update_log)
            
            return update_log
            
        except Exception as e:
            update_log['error'] = str(e)
            self._log_update(update_log)
            raise
    
    def _run_database_migration(self):
        """Exécute les migrations de base de données avec Flask-Migrate"""
        try:
            result = subprocess.run(
                ['flask', 'db', 'upgrade'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                if 'No migrations to apply' in result.stderr or 'No migrations to apply' in result.stdout:
                    return {
                        'success': True,
                        'message': 'Aucune migration à appliquer',
                        'output': result.stdout
                    }
                
                return {
                    'success': False,
                    'error': result.stderr,
                    'output': result.stdout
                }
            
            return {
                'success': True,
                'message': 'Migrations appliquées avec succès',
                'output': result.stdout
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Timeout lors de la migration'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def rollback_update(self, commit_hash):
        """Annule une mise à jour en revenant à un commit précédent"""
        try:
            backup_result = self.backup_service.create_backup(
                description=f"Backup avant rollback vers {commit_hash}"
            )
            
            result = subprocess.run(
                ['git', 'reset', '--hard', commit_hash],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Échec du rollback: {result.stderr}")
            
            subprocess.run(
                ['pip', 'install', '-r', 'requirements.txt'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                'success': True,
                'message': f'Rollback vers {commit_hash} effectué',
                'backup_file': backup_result['backup_file']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_update_history(self):
        """Récupère l'historique des mises à jour"""
        if not os.path.exists(self.update_log_file):
            return []
        
        with open(self.update_log_file, 'r') as f:
            history = json.load(f)
        
        return sorted(history, key=lambda x: x['timestamp'], reverse=True)
    
    def _log_update(self, update_log):
        """Enregistre une mise à jour dans l'historique"""
        history = []
        if os.path.exists(self.update_log_file):
            with open(self.update_log_file, 'r') as f:
                history = json.load(f)
        
        history.append(update_log)
        
        if len(history) > 50:
            history = history[-50:]
        
        with open(self.update_log_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_current_version(self):
        """Récupère la version actuelle (dernier commit)"""
        try:
            commit = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            date = subprocess.run(
                ['git', 'log', '-1', '--format=%ci'],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            message = subprocess.run(
                ['git', 'log', '-1', '--format=%s'],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            return {
                'commit': commit[:8],
                'full_commit': commit,
                'date': date,
                'message': message,
                'branch': self.branch
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'commit': 'unknown'
            }
