# dependency : pip install dohq-tfs

from tfs import TFSAPI


def work_items(org_url, personal_access_token, project='', start_date='2020-03-01', end_date='2021-03-01',
               on='ChangedDate', on2='CreatedDate'):
    """
    desc : get the workitems from azure and return a array of dict that contains all workitems
    :rtype: Array
    :param : web url of azure workspace
    :param :personal access token for authentication
    :param project: project name for which it will return workitems
    :param start_date: start date of which workitem are created or changed
    :param end_date: end date of which workitem are created or changed
    :param on: AcceptedValues are => [ChangedDate, CreatedDate, AssignedDate etc ]
    :param on2: AcceptedValues are => [ChangedDate, CreatedDate, AssignedDate etc ]
    :return: array of workitems
    """
    def finalize_name(string): #get string='name <email>' return array ['name', 'email']
        if string :
            string = str(string)
            aname = ['', '']
            starte = string.find('<')
            ende = string.find('>')
            aname[0] = string[:starte - 1].replace('.', ' ').title()
            aname[1] = string[starte+1:ende]
            return aname
        return None

    client = TFSAPI(org_url , pat=personal_access_token)
    all_workitems  = []
    query = f"""select System.Id from workitems 
                    WHERE [System.{on}] > '{start_date}' and [System.{on}] <= '{end_date}'
                    and [System.{on2}] > '{start_date}' and [System.{on2}] <= '{end_date}'
                    and [System.TeamProject] = '{project}'
                    """

    workitems = client.run_wiql(query).workitems #runs a query and fetch workitems

    for workitem in workitems:
        workitem_ob = {
            'azure_id': workitem['system.Id'],
            'areapath_id': workitem["System.AreaPath"],
            'project_id': workitem["System.TeamProject"],
            'iteration_path': workitem["System.IterationPath"],
            'iteration_id': workitem["System.IterationId"],
            'type': workitem["System.WorkItemType"],
            'stage_id': workitem['System.State'],
            'reason': workitem['System.Reason'],
            'user_id': finalize_name(workitem['System.AssignedTo']),  # azure => assigned to  is the  odoo => user_id
            'created_date': workitem["System.CreatedDate"],
            'created_by_id': finalize_name(workitem['System.CreatedBy']),
            'changed_date': workitem["System.ChangedDate"],
            'changed_by_id': finalize_name(workitem['System.ChangedBy']),
            'title': workitem["System.Title"],
            'name': workitem["System.Title"],
            'priority': workitem["Microsoft.VSTS.Common.Priority"],
            'remaining_work_hour': workitem["Microsoft.VSTS.Scheduling.RemainingWork"] or 0.0,
            'original_estimate_hour': workitem["Microsoft.VSTS.Scheduling.OriginalEstimate"]or 0.0,
            'complete_work_hour': workitem["Microsoft.VSTS.Scheduling.CompletedWork"]or 0.0,
            'parent_task_id': workitem.parent.id if workitem.parent else -1,
            'child_ids': [i.id for i in workitem.childs if i],
            'description': workitem['System.Description'],
            'color' : 0
        }
        all_workitems.append(workitem_ob)
    return all_workitems