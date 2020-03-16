# dependency : pip install dohq-tfs

from tfs import TFSAPI

import base64
import json
import pprint as pp
import requests

def getheader(personal_access_token):
    
    USERNAME = ""
    USER_PASS = USERNAME + ":" + personal_access_token
    B64USERPASS = base64.b64encode(USER_PASS.encode()).decode()

    HEADERS = {
        'Authorization': 'Basic %s' % B64USERPASS
    }

def query_azure(org_url, personal_access_token, query):
    client = TFSAPI(org_url, pat=personal_access_token)
    wiql = client.run_wiql(query)
    return wiql.workitems

def get_project(org_url, personal_access_token):
    client = TFSAPI(org_url, pat=personal_access_token)
    """
    :return: array of all project with id, name,url,state,visibility,lsatUpdateTime
    """
    all_projects = requests.get(org_url + '_apis/projects?api-version=5.1' ,headers=getheader(personal_access_token))
    # responce = json.dumps(all_projects.json())
    if all_projects.status_code == 200:
        responce = (all_projects.json())
        return responce['value']

def work_items(org_url, personal_access_token, date='2020-02-27', on='ChangedDate', on2=False):
    client = TFSAPI(org_url, pat=personal_access_token)
    """
    :rtype: bytearray
    :param date: fatch workietms on specific date
    :param on: AcceptedValues are => [ChangedDate, CreatedDate, etc ]
    :return: array of workitems
    """
    relate_workitem_field = []
    lastdate = date #"2020-02-22"
    query1 = f"""select System.Id from workitems WHERE [System.{on}] = '{lastdate}'"""
    if on2 : query1 += f"OR [System.{on2}] = '{lastdate}'"
    workitems = query_azure(org_url, personal_access_token, query1)
    # print("--------------> total workitems : " , len(workitems))

    def finalize_name(string):
        if string :
            aname = ['', '']
            string = str(string)
            startE = string.find('<')
            endE = string.find('>')
            aname[0] = string[:startE - 1].replace('.', ' ').title()
            aname[1] = string[startE+1:endE]
            return aname
        return None

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
        relate_workitem_field.append(workitem_ob)
        # print( f"Id :-  {id} parent :- {parent} childs :- {childs} title:- {title} {created_by} Created_date :- {created_date} ")
    # print(relate_workitem_field)
    # return workitems will return whole TFS object..
    return relate_workitem_field

def get_work_item_type(org_url, personal_access_token, ):
    """
    :param project: project from which you want to fetch workitemstype
    :return: array of workitem_type names
    """
    
    client = TFSAPI(org_url, pat=personal_access_token)
    project=get_project(org_url, personal_access_token)[0]['name']
    url = org_url + project
    response = requests.get(url + '/_apis/wit/workitemtypes?api-version=5.1' , headers=getheader(personal_access_token))
    work_item_types = []
    if response.status_code == 200:
        work_item_type = response.json()
        for i in work_item_type['value']:
            work_item_types.append(i['name'])
    return work_item_types

def get_project_team(org_url, personal_access_token):
    client = TFSAPI(org_url, pat=personal_access_token)
    url = org_url + '/_apis/teams?api-version=5.1-preview.3'
    all_project_teams = requests.get( url , headers=getheader(personal_access_token))
    if all_project_teams.status_code == 200:
        responce = (all_project_teams.json())
        return responce['value']

def get_all_iteration(org_url, personal_access_token):
    client = TFSAPI(org_url, pat=personal_access_token)
    project=get_project(org_url, personal_access_token)[0]['name']
    team=get_project_team(org_url, personal_access_token,)[0]['name']
    url = org_url + f'/{project}/{team}/_apis/work/teamsettings/iterations?api-version=5.1'
    iterations = []
    all_project_iteration = requests.get( url , headers=getheader(personal_access_token))
    if all_project_iteration.status_code == 200:
        responces = (all_project_iteration.json())
        for responce in responces['value']:
            # print(dir(responce["value"]))
            iterations.append({
                'id' : responce['id'],
                'name' : responce['name'],
                'path' : responce['path'],
                'start_date' : responce['attributes']['startDate'],
                'finish_date' : responce['attributes']['finishDate'],
                'time_frame' : responce['attributes']['timeFrame'],
            })
        return iterations
    else : return False

# print([i['name'] for i in get_all_iteration()])
# print(client.get_workitem(12390).__dict__)
# work_items()
# print(get_project()[0]['name'])
