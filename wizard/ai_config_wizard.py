# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class AIConfigWizard(models.TransientModel):
    """Wizard pour configurer facilement la clé API Claude"""
    _name = 'task.ai.config.wizard'
    _description = 'Assistant de Configuration IA'
    
    api_key = fields.Char(
        string='Clé API Claude',
        required=True,
        help='Votre clé API Anthropic (sk-ant-...)'
    )
    
    model_name = fields.Selection([
        ('claude-sonnet-4-20250514', 'Claude Sonnet 4 (Recommandé - Plus intelligent)'),
        ('claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet (Plus économique)'),
    ], string='Modèle IA', default='claude-sonnet-4-20250514', required=True)
    
    ai_enabled = fields.Boolean(
        string='Activer l\'IA',
        default=True
    )
    
    daily_limit = fields.Integer(
        string='Limite Quotidienne d\'Appels',
        default=100,
        help='Nombre maximum d\'appels API par jour (pour éviter les coûts excessifs)'
    )
    
    def action_save_config(self):
        """Enregistre la configuration"""
        self.ensure_one()
        
        # Valider la clé API
        if not self.api_key.startswith('sk-ant-'):
            raise UserError(
                "❌ Clé API invalide !\n\n"
                "La clé doit commencer par 'sk-ant-'\n"
                "Exemple : sk-ant-api03-xxxxx..."
            )
        
        # Enregistrer dans les paramètres système
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        IrConfigParam.set_param('task_manager.claude_api_key', self.api_key)
        IrConfigParam.set_param('task_manager.ai_model', self.model_name)
        IrConfigParam.set_param('task_manager.ai_enabled', str(self.ai_enabled))
        IrConfigParam.set_param('task_manager.ai_daily_limit', str(self.daily_limit))
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✅ Configuration enregistrée !',
                'message': 'Vous pouvez maintenant utiliser l\'IA pour vos tâches.',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_test_and_save(self):
        """Teste la connexion puis enregistre si OK"""
        self.ensure_one()
        
        # D'abord enregistrer temporairement
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        IrConfigParam.set_param('task_manager.claude_api_key', self.api_key)
        
        # Tester
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model=self.model_name,
                max_tokens=50,
                messages=[{
                    "role": "user",
                    "content": "Réponds juste : Configuration OK"
                }]
            )
            
            # Si succès, enregistrer tout
            self.action_save_config()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '✅ Test réussi !',
                    'message': 'La connexion à l\'API fonctionne. Configuration enregistrée.',
                    'type': 'success',
                    'sticky': True,
                }
            }
            
        except Exception as e:
            # Supprimer la clé temporaire en cas d'échec
            IrConfigParam.set_param('task_manager.claude_api_key', '')
            
            error_msg = str(e)
            if 'authentication' in error_msg.lower():
                message = "Clé API invalide ou expirée"
            elif 'quota' in error_msg.lower():
                message = "Quota API dépassé"
            else:
                message = f"Erreur : {error_msg}"
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '❌ Test échoué',
                    'message': message,
                    'type': 'danger',
                    'sticky': True,
                }
            }


class TaskPriorityWizard(models.TransientModel):
    """Wizard pour confirmer la suggestion de priorité"""
    _name = 'task.priority.wizard'
    _description = 'Confirmation Priorité IA'
    
    task_id = fields.Many2one('task.manager', string='Tâche', required=True)
    
    current_priority = fields.Selection(
        related='task_id.priority',
        string='Priorité Actuelle',
        readonly=True
    )
    
    suggested_priority = fields.Selection([
        ('low', '🟢 Basse'),
        ('medium', '🟡 Moyenne'),
        ('high', '🔴 Haute'),
    ], string='Priorité Suggérée', required=True)
    
    suggestion_reason = fields.Text(
        string='Raison',
        compute='_compute_suggestion_reason'
    )
    
    @api.depends('suggested_priority', 'task_id')
    def _compute_suggestion_reason(self):
        for wizard in self:
            reasons = {
                'low': "Cette tâche peut attendre. Pas de deadline imminente.",
                'medium': "Tâche importante mais pas urgente. Planifiez-la bientôt.",
                'high': "⚠️ Tâche urgente ! Deadline proche ou impact critique."
            }
            wizard.suggestion_reason = reasons.get(wizard.suggested_priority, '')
    
    def action_accept_suggestion(self):
        """Accepte la suggestion et met à jour la priorité"""
        self.ensure_one()
        self.task_id.write({'priority': self.suggested_priority})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✅ Priorité mise à jour !',
                'message': f'La tâche est maintenant en priorité {self.suggested_priority}',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_reject_suggestion(self):
        """Rejette la suggestion"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'ℹ️ Suggestion ignorée',
                'message': 'La priorité n\'a pas été modifiée.',
                'type': 'info',
                'sticky': False,
            }
        }