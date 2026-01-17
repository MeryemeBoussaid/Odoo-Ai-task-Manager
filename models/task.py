# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class TaskManagerTask(models.Model):
    _name = 'task.manager.task'
    _description = 'Task Manager - Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, deadline asc, id desc'

    # Champs de base
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
    
    # Champs de priorité et état
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
    
    # Champs de temps
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
    
    # Champs relationnels
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
    
    # Champs IA (seront remplis par Ibtissam)
    ai_suggestions = fields.Html(
        string='Suggestions IA',
        readonly=True,
        help="Suggestions générées par l'intelligence artificielle"
    )
    
    subtasks = fields.Text(
        string='Sous-tâches suggérées',
        help="Liste des sous-tâches générées par IA"
    )
    
    # Champ calculé
    is_overdue = fields.Boolean(
        string='En retard',
        compute='_compute_is_overdue',
        store=True,
        help="Indique si la tâche est en retard"
    )
    
    # Champs système (gérés automatiquement par Odoo)
    active = fields.Boolean(default=True)
    
    # Méthode de calcul pour is_overdue
    @api.depends('deadline', 'state')
    def _compute_is_overdue(self):
        today = date.today()
        for task in self:
            if task.deadline and task.state != 'done':
                task.is_overdue = task.deadline < today
            else:
                task.is_overdue = False
    
    # Contrainte : deadline ne peut pas être dans le passé à la création
    @api.constrains('deadline')
    def _check_deadline(self):
        for task in self:
            if task.deadline and task.deadline < fields.Date.context_today(self):
                if task.state == 'new':  # Seulement pour les nouvelles tâches
                    raise ValidationError("La date limite ne peut pas être dans le passé.")
    
    # Méthode : Démarrer la tâche
    def action_start_task(self):
        for task in self:
            if task.state == 'new':
                task.state = 'in_progress'
        return True
    
    # Méthode : Terminer la tâche
    def action_complete_task(self):
        for task in self:
            if task.state == 'in_progress':
                task.state = 'done'
        return True
    
    # Méthode : Réinitialiser la tâche
    def action_reset_task(self):
        for task in self:
            task.state = 'new'
        return True