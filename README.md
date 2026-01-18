# 🤖 AI Task Manager - Module Odoo avec Intelligence Artificielle

Un module Odoo 19 puissant pour la gestion de tâches enrichi par l'IA Google Gemini.

![Odoo](https://img.shields.io/badge/Odoo-19.0-purple?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square)
![License](https://img.shields.io/badge/License-LGPL--3-green?style=flat-square)
![AI](https://img.shields.io/badge/AI-Google%20Gemini-orange?style=flat-square)

## ✨ Fonctionnalités

### 📋 Gestion de Tâches Complète
- ✅ Création et suivi de tâches avec statuts (nouveau, en cours, terminé, annulé)
- ✅ Niveaux de priorité (low, medium, high)
- ✅ Gestion des membres d'équipe et assignations
- ✅ Estimation de durée et suivi du temps
- ✅ Dashboard avec graphiques et statistiques

### 🤖 Intelligence Artificielle Intégrée (GRATUIT)
- **🎯 Génération de Description** : Crée automatiquement une description professionnelle détaillée
- **📝 Génération de Sous-tâches** : Décompose la tâche en étapes actionnables
- **⏱️ Estimation de Durée** : Estime intelligemment le temps nécessaire
- **⚡ Suggestion de Priorité** : Analyse et recommande le niveau de priorité approprié

### 📊 Historique IA
- Suivi de toutes les générations IA
- Analyse des performances et temps d'exécution
- Gestion du quota quotidien

## 🚀 Installation

### Prérequis
- Odoo 19.0 ou supérieur
- Python 3.10+
- Compte Google (gratuit)

### Étape 1 : Installer le Module

```bash
# Copier le module dans le dossier addons
cp -r ai_task_manager /path/to/odoo/addons/

# OU créer un lien symbolique
ln -s /path/to/ai_task_manager /path/to/odoo/addons/
```

### Étape 2 : Installer les Dépendances Python

```bash
pip install google-generativeai
```

### Étape 3 : Obtenir une Clé API Gemini (GRATUIT)

1. Allez sur [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Connectez-vous avec votre compte Google
3. Cliquez sur **"Create API Key"**
4. Copiez la clé (commence par `AIza...`)

### Étape 4 : Configurer la Clé API

**Option A : Variable d'Environnement (Recommandé)**

```bash
# Windows PowerShell
$env:GEMINI_API_KEY="VOTRE_CLE_API"

# Linux/Mac
export GEMINI_API_KEY="VOTRE_CLE_API"
```

**Option B : Paramètres Système Odoo**

1. Dans Odoo : **Paramètres → Technique → Paramètres système**
2. Activez le mode développeur
3. Créez un nouveau paramètre :
   - **Clé** : `task_manager.gemini_api_key`
   - **Valeur** : Votre clé API

### Étape 5 : Activer le Module

1. Redémarrez Odoo
2. Allez dans **Applications**
3. Recherchez "AI Task Manager"
4. Cliquez sur **Installer**

## 📖 Utilisation

### Créer une Tâche avec IA

1. **Créez une nouvelle tâche**
   - Menu : Task Manager → Tâches → Créer
   - Donnez un titre descriptif

2. **Utilisez l'IA** (4 boutons disponibles) :
   - 🤖 **Générer Description** : Génère une description complète
   - 📋 **Générer Sous-tâches** : Crée une liste de sous-tâches
   - ⏱️ **Estimer Durée** : Calcule le temps nécessaire
   - ⚡ **Suggérer Priorité** : Recommande la priorité

3. **Gérez votre équipe**
   - Menu : Task Manager → Équipe → Membres
   - Ajoutez des membres et assignez des tâches

4. **Consultez le Dashboard**
   - Menu : Task Manager → Dashboard
   - Visualisez les statistiques et graphiques

## 💡 Exemples d'Utilisation

### Exemple 1 : Tâche de Développement

**Titre** : "Créer une API REST pour la gestion des utilisateurs"

**Résultat IA** :
- **Description** : Description technique détaillée avec objectifs, étapes et résultats attendus
- **Sous-tâches** :
  - Concevoir le schéma de base de données
  - Implémenter les endpoints CRUD
  - Ajouter l'authentification JWT
  - Écrire les tests unitaires
  - Documenter l'API avec Swagger
- **Durée estimée** : 16 heures
- **Priorité** : High

### Exemple 2 : Tâche Marketing

**Titre** : "Lancer une campagne email pour le nouveau produit"

**Résultat IA** :
- **Description** : Plan de campagne avec objectifs, cibles et KPIs
- **Sous-tâches** :
  - Définir la liste de contacts cibles
  - Créer le template email
  - Rédiger le contenu
  - Configurer l'automation
  - Analyser les résultats
- **Durée estimée** : 8 heures
- **Priorité** : Medium

## 🎁 Quota Gratuit Google Gemini

- ✅ **1500 requêtes par jour**
- ✅ **15 requêtes par minute**
- ✅ **100% GRATUIT**
- ✅ **Pas de carte bancaire requise**

## 🔧 Configuration Avancée

### Limites Quotidiennes

Modifiez la limite quotidienne d'appels IA :

1. Paramètres → Technique → Paramètres système
2. Créez : `task_manager.ai_daily_limit` = `100` (par défaut)

### Activer/Désactiver l'IA

1. Paramètres → Technique → Paramètres système
2. Créez : `task_manager.ai_enabled` = `True` ou `False`

## 📊 Structure du Module

```
ai_task_manager/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── task.py              # Modèle principal avec fonctions IA
│   ├── team_member.py       # Gestion des membres
│   ├── ai_config.py         # Configuration IA
│   └── task_ai_history.py   # Historique des générations
├── views/
│   ├── task_views.xml       # Vues des tâches
│   ├── team_member_views.xml
│   ├── dashboard_views.xml  # Dashboard et graphiques
│   └── menu_views.xml       # Structure des menus
├── security/
│   └── ir.model.access.csv  # Droits d'accès
├── data/
│   ├── ai_config_data.xml   # Configuration par défaut
│   └── demo_data.xml        # Données de démonstration
└── static/
    └── description/
        └── icon.png
```

## 🐛 Dépannage

### Erreur "Clé API non configurée"
→ Vérifiez que la variable d'environnement `GEMINI_API_KEY` est définie
→ OU que le paramètre système `task_manager.gemini_api_key` existe

### Erreur "Quota dépassé"
→ Attendez la réinitialisation (minuit UTC)
→ OU créez une nouvelle clé API sur un nouveau projet Google

### L'IA ne génère rien
→ Vérifiez votre connexion internet
→ Vérifiez que la clé API est valide sur [Google AI Studio](https://makersuite.google.com/app/apikey)

### Les résultats ne s'affichent pas
→ Rafraîchissez la page (F5)
→ Vérifiez les logs Odoo pour les erreurs

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Pushez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence LGPL-3. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Auteurs

- **Développeur Principal** - Meryeme Boussaid , Safaa Bouhnine , Ibtissam Aidoun , Chaimae Azzouz
- **IA Integration** - Powered by Google Gemini

## 🙏 Remerciements

- Google pour l'API Gemini gratuite
- La communauté Odoo
- Tous les contributeurs



