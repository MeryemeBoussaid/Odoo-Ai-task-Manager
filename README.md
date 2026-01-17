# 🤖 AI Task Manager - Odoo Module

## 📋 Description
Gestionnaire de tâches intelligent avec assistance IA pour:
- Générer des descriptions détaillées
- Estimer la durée des tâches
- Suggérer des sous-tâches
- Prioriser automatiquement

## 🚀 Installation

### Prérequis
- Odoo 19.0
- Python 3.8+
- Clé API Anthropic Claude

### Étapes
1. Cloner le repository dans `custom_addons/`
2. Installer les dépendances Python:
```bash
   pip install anthropic
```
3. Redémarrer Odoo
4. Activer le mode développeur
5. Mettre à jour la liste des applications
6. Installer "AI Task Manager"

## 📁 Structure du Projet
```
ai_task_manager/
├── models/          # Modèles de données
├── views/           # Interfaces XML
├── security/        # Contrôle d'accès
├── data/            # Données de démo
└── static/          # Ressources statiques
```

## 🔧 Configuration
Ajouter votre clé API Claude dans `models/task.py`:
```python
api_key = "votre_cle_api_ici"
```

