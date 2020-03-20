# -*- coding: utf-8 -*-
{
    'name': "Aproject",
    'summary': """
        PROJECT MANAGMENT AND JOB COSTING  AT BIZNOVARE""",
    'description': """
        Long description of module's purpose 
    """,

    'author': "kevin",
    'website': "http://www.yourcompany.com",

    'version': '0.1',

    'depends': ['base',
                'analytic',
                'crm',
                'account',
                'project',
                'hr_timesheet'
                ],

    # always loaded
    'data': [
        # 'security/ir.models.access.csv',
        'security/groups.xml',
        'widget/views/views.xml',
        'widget/views/project_azure.xml',
        'views/templates.xml',
        'views/crone_job.xml',
        'views/views_workitem.xml',
        'views/project_project.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'application' : True,
    'installable' : True,
}
