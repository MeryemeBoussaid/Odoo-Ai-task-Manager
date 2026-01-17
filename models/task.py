# -*- coding: utf-8 -*-
import anthropic
import logging
import time
import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import date

_logger = logging.getLogger(__name__)


class TaskManagerTask(models.Model):
    _name = 'task.manager.task'
    _description = 'Task Manager - Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, deadline asc, id desc'

    # ========== CHAMPS DE BASE ==========
    
    name = fields.Char(
        string='Titre de la tâche',
        required=True,
        tracking=True,
        index=True,
        help="Titre court et descriptif de la tâche"
    )
    
    description = fields.Text(
        string='Description',
        tracking=True,
        help="Description détaillée de la tâche"
    )
    
    # ========== CHAMPS DE PRIORITÉ ET ÉTAT ==========
    
    priority = fields.Selection([
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Haute')
    ], string='Priorité', default='medium', required=True, tracking=True)
    
    state = fields.Selection([
        ('new', 'Nouveau'),
        ('in_progress', 'En cours'),
        ('done', 'Terminé')
    ], string='État', default='new', required=True, tracking=True)
    
    # ========== CHAMPS DE TEMPS ==========
    
    deadline = fields.Date(
        string='Date limite',
        tracking=True,
        help="Date limite pour terminer la tâche"
    )
    
    estimated_hours = fields.Float(
        string='Durée estimée (heures)',
        default=0.0,
        help="Estimation du temps nécessaire en heures"
    )
    
    # ========== CHAMPS RELATIONNELS ==========
    
    user_id = fields.Many2one(
        'res.users',
        string='Assigné à',
        default=lambda self: self.env.user,
        tracking=True,
        help="Utilisateur responsable de la tâche"
    )
    
    team_member_id = fields.Many2one(
        'task.manager.team.member',
        string='Membre d\'équipe',
        ondelete='set null',
        tracking=True,
        help="Membre d'équipe assigné"
    )
    
    # ========== CHAMPS IA ==========
    
    ai_suggestions = fields.Html(
        string='Suggestions IA',
        readonly=True,
        help="Suggestions générées par l'intelligence artificielle"
    )
    
    subtasks = fields.Text(
        string='Sous-tâches suggérées',
        help="Liste des sous-tâches générées par IA"
    )
    
    # Relation avec l'historique IA
    ai_history_ids = fields.One2many(
        'task.ai.history',
        'task_id',
        string='Historique IA',
        help='Historique de toutes les générations IA pour cette tâche'
    )
    
    # Compteur de générations
    ai_suggestion_count = fields.Integer(
        string='Nombre de suggestions IA',
        compute='_compute_ai_suggestion_count',
        store=True
    )
    
    # ========== CHAMPS CALCULÉS ==========
    
    is_overdue = fields.Boolean(
        string='En retard',
        compute='_compute_is_overdue',
        store=True,
        help="Indique si la tâche est en retard"
    )
    
    # ========== CHAMPS SYSTÈME ==========
    
    active = fields.Boolean(default=True)
    
    # ========== MÉTHODES DE CALCUL ==========
    
    @api.depends('deadline', 'state')
    def _compute_is_overdue(self):
        """Calcule si la tâche est en retard"""
        today = date.today()
        for task in self:
            if task.deadline and task.state != 'done':
                task.is_overdue = task.deadline < today
            else:
                task.is_overdue = False
    
    @api.depends('ai_history_ids')
    def _compute_ai_suggestion_count(self):
        """Compte le nombre de générations IA réussies"""
        for task in self:
            task.ai_suggestion_count = len(task.ai_history_ids.filtered(lambda h: h.success))
    
    # ========== CONTRAINTES ==========
    
    @api.constrains('deadline')
    def _check_deadline(self):
        """Vérifie que la deadline n'est pas dans le passé"""
        for task in self:
            if task.deadline and task.deadline < fields.Date.context_today(self):
                if task.state == 'new':  # Seulement pour les nouvelles tâches
                    raise ValidationError("La date limite ne peut pas être dans le passé.")
    
    # ========== MÉTHODES DE GESTION DES TÂCHES ==========
    
    def action_start_task(self):
        """Démarre la tâche"""
        for task in self:
            if task.state == 'new':
                task.state = 'in_progress'
        return True
    
    def action_complete_task(self):
        """Termine la tâche"""
        for task in self:
            if task.state == 'in_progress':
                task.state = 'done'
        return True
    
    def action_reset_task(self):
        """Réinitialise la tâche"""
        for task in self:
            task.state = 'new'
        return True
    
    # ========== MÉTHODES IA ==========
    
    def action_generate_ai_description(self):
        """
        Génère automatiquement une description détaillée basée sur le titre
        """
        self.ensure_one()
        
        if not self.name:
            raise UserError("❌ Impossible de générer une description sans titre !")
        
        # Vérifier la configuration
        ai_config = self.env['task.ai.config']
        ai_config.check_daily_limit()
        config = ai_config.get_config()
        
        if not config['enabled']:
            raise UserError("❌ L'IA est désactivée. Activez-la dans les paramètres.")
        
        # Préparer le prompt
        prompt = f"""Tu es un assistant de gestion de projet professionnel.
Titre de la tâche : {self.name}

Génère une description professionnelle et détaillée de cette tâche qui explique :
1. L'objectif principal
2. Les étapes à suivre
3. Les résultats attendus

Sois concis mais complet (maximum 200 mots).
Réponds en français, sans introduction ni conclusion."""
        
        start_time = time.time()
        
        try:
            # Appel à l'API Claude
            client = anthropic.Anthropic(api_key=config['api_key'])
            
            response = client.messages.create(
                model=config['model'],
                max_tokens=config['max_tokens'],
                temperature=config['temperature'],
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extraire la réponse
            description = response.content[0].text.strip()
            execution_time = time.time() - start_time
            
            # Mettre à jour la tâche
            self.write({'description': description})
            
            # Logger dans l'historique
            self.env['task.ai.history'].create_log(
                task_id=self.id,
                generation_type='description',
                prompt=prompt,
                response=description,
                success=True,
                tokens=response.usage.input_tokens + response.usage.output_tokens,
                exec_time=execution_time,
                model=config['model']
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '✅ Description générée !',
                    'message': f'La description a été générée avec succès en {execution_time:.1f}s',
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            error_msg = str(e)
            _logger.error(f"Erreur lors de la génération de description : {error_msg}")
            
            # Logger l'erreur
            self.env['task.ai.history'].create_log(
                task_id=self.id,
                generation_type='description',
                prompt=prompt,
                success=False,
                error=error_msg,
                exec_time=time.time() - start_time,
                model=config.get('model', '')
            )
            
            # Messages d'erreur spécifiques
            if 'authentication' in error_msg.lower() or 'api_key' in error_msg.lower():
                message = "Clé API invalide. Vérifiez votre configuration."
            elif 'quota' in error_msg.lower() or 'rate_limit' in error_msg.lower():
                message = "Quota API dépassé. Réessayez plus tard."
            else:
                message = f"Erreur : {error_msg}"
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '❌ Erreur de génération',
                    'message': message,
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    def action_generate_ai_subtasks(self):
        """
        Génère automatiquement des sous-tâches basées sur le titre et la description
        """
        self.ensure_one()
        
        if not self.name:
            raise UserError("❌ Impossible de générer des sous-tâches sans titre !")
        
        # Vérifier la configuration
        ai_config = self.env['task.ai.config']
        ai_config.check_daily_limit()
        config = ai_config.get_config()
        
        # Préparer le prompt
        description_text = self.description or "Pas de description disponible"
        
        prompt = f"""Titre : {self.name}
Description : {description_text}

Génère une liste de 3 à 5 sous-tâches concrètes pour accomplir cette tâche principale.
Chaque sous-tâche doit être :
- Actionnable
- Mesurable
- Courte (une ligne)

Format : liste à puces en markdown.
Réponds en français, sans introduction ni conclusion.
Exemple de format attendu :
- Sous-tâche 1
- Sous-tâche 2
- Sous-tâche 3"""
        
        start_time = time.time()
        
        try:
            client = anthropic.Anthropic(api_key=config['api_key'])
            
            response = client.messages.create(
                model=config['model'],
                max_tokens=config['max_tokens'],
                temperature=config['temperature'],
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            subtasks = response.content[0].text.strip()
            execution_time = time.time() - start_time
            
            self.write({'subtasks': subtasks})
            
            self.env['task.ai.history'].create_log(
                task_id=self.id,
                generation_type='subtasks',
                prompt=prompt,
                response=subtasks,
                success=True,
                tokens=response.usage.input_tokens + response.usage.output_tokens,
                exec_time=execution_time,
                model=config['model']
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '✅ Sous-tâches générées !',
                    'message': f'{len(subtasks.split(chr(10)))} sous-tâches créées en {execution_time:.1f}s',
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            error_msg = str(e)
            _logger.error(f"Erreur génération sous-tâches : {error_msg}")
            
            self.env['task.ai.history'].create_log(
                task_id=self.id,
                generation_type='subtasks',
                prompt=prompt,
                success=False,
                error=error_msg,
                exec_time=time.time() - start_time
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '❌ Erreur',
                    'message': f'Impossible de générer les sous-tâches : {error_msg}',
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    def action_estimate_duration(self):
        """
        Estime automatiquement la durée nécessaire pour accomplir la tâche
        """
        self.ensure_one()
        
        ai_config = self.env['task.ai.config']
        ai_config.check_daily_limit()
        config = ai_config.get_config()
        
        description_text = self.description or "Pas de description disponible"
        
        prompt = f"""Titre : {self.name}
Description : {description_text}

Estime le temps nécessaire pour accomplir cette tâche.
Donne une estimation réaliste en heures (nombre décimal).

Considère :
- La complexité de la tâche
- Les dépendances potentielles
- Le travail de recherche éventuel

Réponds UNIQUEMENT avec un nombre décimal (exemple: 4.5)
Ne mets AUCUN texte avant ou après le nombre."""
        
        start_time = time.time()
        
        try:
            client = anthropic.Anthropic(api_key=config['api_key'])
            
            response = client.messages.create(
                model=config['model'],
                max_tokens=50,
                temperature=0.3,  # Moins créatif pour les chiffres
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = response.content[0].text.strip()
            
            # Extraire le nombre de la réponse
            match = re.search(r'(\d+\.?\d*)', response_text)
            if not match:
                raise ValueError("Aucun nombre trouvé dans la réponse")
            
            estimated_hours = float(match.group(1))
            
            # Validation
            if estimated_hours <= 0 or estimated_hours > 1000:
                raise ValueError(f"Estimation invalide : {estimated_hours}h")
            
            execution_time = time.time() - start_time
            
            self.write({'estimated_hours': estimated_hours})
            
            self.env['task.ai.history'].create_log(
                task_id=self.id,
                generation_type='duration',
                prompt=prompt,
                response=response_text,
                success=True,
                tokens=response.usage.input_tokens + response.usage.output_tokens,
                exec_time=execution_time,
                model=config['model']
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '✅ Durée estimée !',
                    'message': f'Estimation : {estimated_hours}h',
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            error_msg = str(e)
            _logger.error(f"Erreur estimation durée : {error_msg}")
            
            self.env['task.ai.history'].create_log(
                task_id=self.id,
                generation_type='duration',
                prompt=prompt,
                success=False,
                error=error_msg,
                exec_time=time.time() - start_time
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '❌ Erreur',
                    'message': f'Impossible d\'estimer la durée : {error_msg}',
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    def action_suggest_priority(self):
        """
        Suggère un niveau de priorité basé sur le contexte de la tâche
        """
        self.ensure_one()
        
        ai_config = self.env['task.ai.config']
        ai_config.check_daily_limit()
        config = ai_config.get_config()
        
        description_text = self.description or "Pas de description disponible"
        deadline_text = str(self.deadline) if self.deadline else "non définie"
        
        prompt = f"""Titre : {self.name}
Description : {description_text}
Deadline : {deadline_text}

Analyse cette tâche et suggère un niveau de priorité.

Critères :
- high : urgent, critique, deadline proche, bloquant
- medium : important mais pas urgent, deadline raisonnable
- low : peut attendre, nice to have, pas de deadline proche

Réponds UNIQUEMENT avec : low, medium, ou high
Ne mets AUCUN autre texte."""
        
        start_time = time.time()
        
        try:
            client = anthropic.Anthropic(api_key=config['api_key'])
            
            response = client.messages.create(
                model=config['model'],
                max_tokens=20,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            suggested_priority = response.content[0].text.strip().lower()
            
            # Validation
            if suggested_priority not in ['low', 'medium', 'high']:
                raise ValueError(f"Priorité invalide : {suggested_priority}")
            
            execution_time = time.time() - start_time
            
            self.env['task.ai.history'].create_log(
                task_id=self.id,
                generation_type='priority',
                prompt=prompt,
                response=suggested_priority,
                success=True,
                tokens=response.usage.input_tokens + response.usage.output_tokens,
                exec_time=execution_time,
                model=config['model']
            )
            
            # Créer un wizard pour demander confirmation
            wizard = self.env['task.priority.wizard'].create({
                'task_id': self.id,
                'suggested_priority': suggested_priority,
            })
            
            return {
                'name': 'Suggestion de Priorité',
                'type': 'ir.actions.act_window',
                'res_model': 'task.priority.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
            }
            
        except Exception as e:
            error_msg = str(e)
            _logger.error(f"Erreur suggestion priorité : {error_msg}")
            
            self.env['task.ai.history'].create_log(
                task_id=self.id,
                generation_type='priority',
                prompt=prompt,
                success=False,
                error=error_msg,
                exec_time=time.time() - start_time
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '❌ Erreur',
                    'message': f'Impossible de suggérer la priorité : {error_msg}',
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    def action_generate_all_ai_suggestions(self):
        """
        Génère toutes les suggestions IA en une seule fois
        """
        self.ensure_one()
        
        if not self.name:
            raise UserError("❌ Impossible de générer des suggestions sans titre !")
        
        results = []
        
        try:
            # 1. Description
            result = self.action_generate_ai_description()
            if result.get('params', {}).get('type') == 'success':
                results.append('✅ Description')
            else:
                results.append('❌ Description')
            
            # 2. Sous-tâches
            result = self.action_generate_ai_subtasks()
            if result.get('params', {}).get('type') == 'success':
                results.append('✅ Sous-tâches')
            else:
                results.append('❌ Sous-tâches')
            
            # 3. Durée
            result = self.action_estimate_duration()
            if result.get('params', {}).get('type') == 'success':
                results.append('✅ Durée')
            else:
                results.append('❌ Durée')
            
            # 4. Priorité
            result = self.action_suggest_priority()
            results.append('✅ Priorité (à confirmer)')
            
            summary = '\n'.join(results)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '🎉 Génération complète terminée !',
                    'message': f'Résultats :\n{summary}',
                    'type': 'success',
                    'sticky': True,
                }
            }
            
        except Exception as e:
            _logger.error(f"Erreur génération complète : {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '❌ Erreur',
                    'message': f'Génération interrompue : {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }