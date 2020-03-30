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

    'depends': ['base',
		'analytic',
		'account',                
		'project',
		'hr_timesheet',
		'queue_job'
                ],

    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
	'wizard/views/q_p_wizard.xml',
        'wizard/views/project_azure.xml',
	'views/system_parameter.xml',
        'views/res_partner.xml',
        'views/crone_job.xml',
        'views/project_task.xml',
        'views/project_project.xml',
    ],
    'application' : True,
    'installable' : True,
}
