# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TaskAIHistory(models.Model):
    """Historique des générations IA pour traçabilité et debug"""
    _name = 'task.ai.history'
    _description = 'Historique des Générations IA'
    _order = 'generation_date desc'
    
    task_id = fields.Many2one(
        'task.manager.task',
        string='Tâche',
        required=True,
        ondelete='cascade'
    )
    
    generation_type = fields.Selection([
        ('description', 'Description'),
        ('subtasks', 'Sous-tâches'),
        ('duration', 'Estimation Durée'),
        ('priority', 'Suggestion Priorité'),
        ('complete', 'Génération Complète'),
    ], string='Type de Génération', required=True)
    
    prompt_sent = fields.Text(
        string='Prompt Envoyé',
        help='Le prompt envoyé à Claude'
    )
    
    response_received = fields.Text(
        string='Réponse Reçue',
        help='La réponse complète de Claude'
    )
    
    generation_date = fields.Datetime(
        string='Date de Génération',
        default=fields.Datetime.now,
        required=True
    )
    
    success = fields.Boolean(
        string='Succès',
        default=False
    )
    
    error_message = fields.Text(
        string='Message d\'Erreur',
        help='Détails de l\'erreur si échec'
    )
    
    tokens_used = fields.Integer(
        string='Tokens Utilisés',
        help='Nombre de tokens consommés (pour tracking coûts)'
    )
    
    execution_time = fields.Float(
        string='Temps d\'Exécution (s)',
        help='Temps pris par l\'appel API'
    )
    
    model_used = fields.Char(
        string='Modèle Utilisé',
        help='Quel modèle Claude a été utilisé'
    )
    
    @api.model
    def create_log(self, task_id, generation_type, prompt, response=None, 
                   success=False, error=None, tokens=0, exec_time=0.0, model=''):
        """Méthode helper pour créer un log rapidement"""
        return self.create({
            'task_id': task_id,
            'generation_type': generation_type,
            'prompt_sent': prompt,
            'response_received': response,
            'success': success,
            'error_message': error,
            'tokens_used': tokens,
            'execution_time': exec_time,
            'model_used': model,
        })
    
    @api.model
    def get_statistics(self):
        """Retourne des statistiques d'utilisation de l'IA"""
        total_calls = self.search_count([])
        successful_calls = self.search_count([('success', '=', True)])
        failed_calls = self.search_count([('success', '=', False)])
        
        total_tokens = sum(self.search([]).mapped('tokens_used'))
        
        today = fields.Date.today()
        calls_today = self.search_count([
            ('generation_date', '>=', today)
        ])
        
        return {
            'total_calls': total_calls,
            'successful_calls': successful_calls,
            'failed_calls': failed_calls,
            'success_rate': (successful_calls / total_calls * 100) if total_calls > 0 else 0,
            'total_tokens': total_tokens,
            'calls_today': calls_today,
        }