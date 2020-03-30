# dependency : pip install dohq-tfs

from tfs import TFSAPI
from odoo import _
import logging
import base64
import requests


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

    def finalize_name(string):  # get string='name <email>' return array ['name', 'email']
        if string:
            string = str(string)
            aname = ['', '']
            starte = string.find('<')
            ende = string.find('>')
            aname[0] = string[:starte - 1].replace('.', ' ').title()
            aname[1] = string[starte + 1:ende]
            return aname
        return None

    client = TFSAPI(org_url, pat=personal_access_token)
    all_workitems = []
    query = f"select System.Id from workitems WHERE [System.TeamProject] = '{project}' "
    if start_date:
        query += f"and [System.{on}] > '{start_date}' and [System.{on2}] > '{start_date}' "
    if end_date:
        query += f"and [System.{on}] <= '{end_date}' and [System.{on2}] <= '{end_date}' "

    # query = f"""select System.Id from workitems
    #                 WHERE [System.{on}] > '{start_date}'
    #                 and [System.{on2}] > '{start_date}'
    #                 and [System.{on}] <= '{end_date}'
    #                 and [System.{on2}] <= '{end_date}'
    #                 and [System.TeamProject] = '{project}'
    #                 """
    try:
        workitems = client.run_wiql(query).workitems  # runs a query and fetch workitems

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
                'user_id': finalize_name(workitem['System.AssignedTo']),
                # azure => assigned to  is the  odoo => user_id
                'created_date': workitem["System.CreatedDate"],
                'created_by_id': finalize_name(workitem['System.CreatedBy']),
                'changed_date': workitem["System.ChangedDate"],
                'changed_by_id': finalize_name(workitem['System.ChangedBy']),
                'name': workitem["System.Title"],
                'priority': workitem["Microsoft.VSTS.Common.Priority"],
                'remaining_work_hour': workitem["Microsoft.VSTS.Scheduling.RemainingWork"] or 0.0,
                'original_estimate_hour': workitem["Microsoft.VSTS.Scheduling.OriginalEstimate"] or 0.0,
                'complete_work_hour': workitem["Microsoft.VSTS.Scheduling.CompletedWork"] or 0.0,
                'parent_task_id': workitem.parent.id if workitem.parent else -1,
                'child_ids': [i.id for i in workitem.childs if i],
                'description': workitem['System.Description'],
                'color': 0
            }
            all_workitems.append(workitem_ob)
        return all_workitems
    except Exception as e:
        logging.error(f"No project named '{project}' present in devops azure at {org_url} or {e} ")
        return {}


def get_project(org_url, personal_access_token):
    client = TFSAPI(org_url, pat=personal_access_token)
    return client.get_projects()


def get_team(org_url, personal_access_token,project_name):
    client = TFSAPI(org_url, pat=personal_access_token)
    project = client.get_project(project_name)
    # Get project team
    return project.defaultTeam


def getheader(personal_access_token):
    USERNAME = ""
    USER_PASS = USERNAME + ":" + personal_access_token
    B64USERPASS = base64.b64encode(USER_PASS.encode()).decode()
    HEADERS = {
        'Authorization': 'Basic %s' % B64USERPASS
    }
    return HEADERS


def get_all_iteration(org_url, personal_access_token, project_name):
    team_name = get_team(org_url, personal_access_token, project_name)
    url = org_url + f'/{project_name}/{team_name}/_apis/work/teamsettings/iterations?api-version=5.1'
    iterations = []
    all_project_iteration = requests.get(url, headers=getheader(personal_access_token))
    if all_project_iteration.status_code in [200]:
        responces = (all_project_iteration.json())
        for responce in responces['value']:
            iterations.append({
                'azure_id': responce['id'],
                'name': responce['name'],
                'path': responce['path'],
                'startdate': responce['attributes']['startDate'],
                'enddate': responce['attributes']['finishDate'],
                'time_frame': responce['attributes']['timeFrame'],
            })
        return iterations
    else:
        return False

