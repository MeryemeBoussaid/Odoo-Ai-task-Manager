# -*- coding: utf-8 -*-
import os
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AIConfig(models.TransientModel):
    """Configuration pour l'API Claude AI"""
    _name = 'task.ai.config'
    _description = 'Configuration IA pour Task Manager'

    api_key = fields.Char(
        string='Clé API Claude',
        help='Votre clé API Anthropic (commence par sk-ant-...)'
    )
    
    model_name = fields.Selection([
        ('claude-sonnet-4-20250514', 'Claude Sonnet 4 (Recommandé)'),
        ('claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet'),
    ], string='Modèle Claude', default='claude-sonnet-4-20250514')
    
    temperature = fields.Float(
        string='Créativité (Temperature)',
        default=0.7,
        help='0 = très précis, 1 = très créatif'
    )
    
    max_tokens = fields.Integer(
        string='Tokens Maximum',
        default=1000,
        help='Longueur maximale de la réponse'
    )
    
    ai_enabled = fields.Boolean(
        string='IA Activée',
        default=True
    )
    
    daily_limit = fields.Integer(
        string='Limite Quotidienne',
        default=100,
        help='Nombre maximum d\'appels API par jour'
    )
    
    @api.model
    def get_api_key(self):
        """
        Récupère la clé API de manière sécurisée
        Ordre de priorité :
        1. Variable d'environnement CLAUDE_API_KEY
        2. Paramètre système ir.config_parameter
        3. Fichier de configuration externe
        """
        # 1. Variable d'environnement (RECOMMANDÉ)
        api_key = os.environ.get('CLAUDE_API_KEY')
        if api_key:
            _logger.info('🔑 Clé API chargée depuis variable d\'environnement')
            return api_key
        
        # 2. Paramètre système Odoo
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        api_key = IrConfigParam.get_param('task_manager.claude_api_key')
        if api_key:
            _logger.info('🔑 Clé API chargée depuis paramètres système')
            return api_key
        
        # 3. Aucune clé trouvée
        raise UserError(
            "❌ Clé API Claude non configurée !\n\n"
            "Pour configurer :\n"
            "1. Allez dans Paramètres > Technique > Paramètres système\n"
            "2. Créez : task_manager.claude_api_key = votre_clé\n\n"
            "OU définissez la variable d'environnement CLAUDE_API_KEY"
        )
    
    @api.model
    def set_api_key(self, api_key):
        """Enregistre la clé API de manière sécurisée"""
        if not api_key or not api_key.startswith('sk-ant-'):
            raise UserError("❌ Clé API invalide ! Elle doit commencer par 'sk-ant-'")
        
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        IrConfigParam.set_param('task_manager.claude_api_key', api_key)
        _logger.info('✅ Clé API enregistrée avec succès')
        return True
    
    @api.model
    def get_config(self):
        """Retourne la configuration complète de l'IA"""
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        
        return {
            'api_key': self.get_api_key(),
            'model': IrConfigParam.get_param('task_manager.ai_model', 'claude-sonnet-4-20250514'),
            'temperature': float(IrConfigParam.get_param('task_manager.ai_temperature', '0.7')),
            'max_tokens': int(IrConfigParam.get_param('task_manager.ai_max_tokens', '1000')),
            'enabled': IrConfigParam.get_param('task_manager.ai_enabled', 'True') == 'True',
            'daily_limit': int(IrConfigParam.get_param('task_manager.ai_daily_limit', '100')),
        }
    
    @api.model
    def test_connection(self):
        """Test la connexion à l'API Claude"""
        try:
            import anthropic
            api_key = self.get_api_key()
            
            client = anthropic.Anthropic(api_key=api_key)
            
            # Test simple
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=50,
                messages=[{
                    "role": "user",
                    "content": "Réponds juste : OK"
                }]
            )
            
            if response.content[0].text:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '✅ Connexion réussie !',
                        'message': 'L\'API Claude fonctionne correctement.',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '❌ Erreur de connexion',
                    'message': f'Impossible de se connecter à l\'API : {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    @api.model
    def check_daily_limit(self):
        """Vérifie si la limite quotidienne d'appels n'est pas dépassée"""
        today = fields.Date.today()
        count = self.env['task.ai.history'].search_count([
            ('generation_date', '>=', today),
            ('success', '=', True)
        ])
        
        config = self.get_config()
        limit = config.get('daily_limit', 100)
        
        if count >= limit:
            raise UserError(
                f"❌ Limite quotidienne atteinte !\n\n"
                f"Vous avez utilisé {count}/{limit} appels aujourd'hui.\n"
                f"La limite sera réinitialisée demain."
            )
        
        return True