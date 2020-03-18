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
                'project',
                'hr_timesheet'
                ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/groups.xml',
        'views/templates.xml',
        'views/crone_job.xml',
        # 'views/views.xml',
        'views/views_workitem.xml',
        'views/project_project.xml',
        'widget/views/views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'application' : True,
    'installable' : True,
}
