# -*- coding: utf-8 -*-
{
    'name': "project_management",

    'summary': """
         PROJECT MANAGMENT AND JOB COSTING  AT BIZNOVARE
        """,

    'description': """
        Project Management and Job costing manages project related data and its costing
    """,

    'author': "Biznovare",

    'category': 'Management and Costing',
    'version': '0.1',

    'depends': [
        'base',
        'project',
        'hr',
        'hr_timesheet',
        'my_mode'
        ],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/project_expense.xml',
        'views/project_recurring_expense.xml',
        'views/project_forecast_input.xml',
        'views/project_forecast_output.xml'
    ]
}
