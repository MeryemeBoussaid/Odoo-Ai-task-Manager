# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class TaskManagerTeamMember(models.Model):
    _name = 'task.manager.team.member'
    _description = 'Task Manager - Team Member'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # ← IMPORTANT
    _order = 'name asc'
    
    # ========== CHAMPS DE BASE ==========
    name = fields.Char(
        string='Nom complet',
        required=True,
        size=100,
        tracking=True,  # ← Ajouté pour le tracking
        help="Nom complet du membre d'équipe"
    )
    
    email = fields.Char(
        string='Email professionnel',
        tracking=True,  # ← Ajouté
        help="Adresse email professionnelle"
    )
    
    phone = fields.Char(
        string='Téléphone',
        help="Numéro de téléphone"
    )
    
    role = fields.Selection([
        ('developer', 'Développeur'),
        ('designer', 'Designer'),
        ('manager', 'Manager'),
        ('tester', 'Testeur')
    ], string='Rôle', required=True, default='developer', tracking=True)
    
    avatar = fields.Image(
        string='Photo',
        max_width=128,
        max_height=128,
        help="Photo du membre"
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Utilisateur Odoo',
        tracking=True,  # ← Ajouté
        help="Lien avec un utilisateur Odoo"
    )
    
    # ========== RELATION AVEC TASKS ==========
    task_ids = fields.One2many(
        'task.manager.task',
        'team_member_id',
        string='Tâches assignées'
    )
    
    active = fields.Boolean(
        string='Actif',
        default=True,
        help="Décocher pour archiver le membre"
    )
    
    joining_date = fields.Date(
        string="Date d'arrivée",
        default=fields.Date.today,
        tracking=True,  # ← Ajouté
        help="Date d'entrée dans l'équipe"
    )
    
    # ========== CHAMPS CALCULÉS ==========
    task_count = fields.Integer(
        string='Total tâches',
        compute='_compute_task_count',
        store=True
    )
    
    task_new_count = fields.Integer(
        string='Nouvelles',
        compute='_compute_task_counts',
        store=True
    )
    
    task_in_progress_count = fields.Integer(
        string='En cours',
        compute='_compute_task_counts',
        store=True
    )
    
    task_done_count = fields.Integer(
        string='Terminées',
        compute='_compute_task_counts',
        store=True
    )
    
    completion_rate = fields.Float(
        string='Taux de complétion (%)',
        compute='_compute_completion_rate',
        store=True
    )
    
    # ========== MÉTHODES DE CALCUL ==========
    @api.depends('task_ids')
    def _compute_task_count(self):
        for member in self:
            member.task_count = len(member.task_ids)
    
    @api.depends('task_ids.state')
    def _compute_task_counts(self):
        for member in self:
            member.task_new_count = len(member.task_ids.filtered(lambda t: t.state == 'new'))
            member.task_in_progress_count = len(member.task_ids.filtered(lambda t: t.state == 'in_progress'))
            member.task_done_count = len(member.task_ids.filtered(lambda t: t.state == 'done'))
    
    @api.depends('task_count', 'task_done_count')
    def _compute_completion_rate(self):
        for member in self:
            if member.task_count > 0:
                member.completion_rate = (member.task_done_count / member.task_count) * 100
            else:
                member.completion_rate = 0.0
    
    # ========== CONTRAINTES ==========
    @api.constrains('email')
    def _check_email_format(self):
        """Valide le format de l'email"""
        for member in self:
            if member.email:
                email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_regex, member.email):
                    raise ValidationError("Format d'email invalide. Exemple: nom@exemple.com")
    
    # ========== ACTIONS ==========
    def action_view_tasks(self):
        """Ouvre la vue avec toutes les tâches du membre"""
        self.ensure_one()
        return {
            'name': f'Tâches de {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'task.manager.task',
            'view_mode': 'list,form',
            'domain': [('team_member_id', '=', self.id)],
            'context': {'default_team_member_id': self.id}
        }