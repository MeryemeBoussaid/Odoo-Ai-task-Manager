# -*- coding: utf-8 -*-
{
    'name': 'AI Task Manager',
    'version': '1.0.0',
    'category': 'Productivity',
    'summary': 'Manage tasks with AI assistance',
    'description': """
        AI Task Manager
        ===============
        Simple task management system with AI-powered suggestions.
        
        Features:
        ---------
        * Create and assign tasks
        * AI generates descriptions and subtasks
        * Team member management
        * Simple dashboard with statistics
        * Priority management
        * Deadline tracking
    """,
    'author': 'Votre Équipe',
    'website': 'https://github.com/votre-equipe/ai-task-manager',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/task_views.xml',
        'views/team_member_views.xml',
        'views/dashboard_views.xml',
        'views/menu_views.xml',
        'data/demo_data.xml',
    ],
    # 'external_dependencies': {
    #     'python': ['anthropic'],
    # },
    'demo': [
        'data/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 'ai_task_manager/static/src/css/dashboard.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}