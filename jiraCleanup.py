import json
import os

from atlassian import jira as JIRA


# OS specific strings - find configs file and import values
sys_path = os.path.sep
# Path of the config file, relative to the working directory
dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = f'{dir_path}{sys_path}configs{sys_path}config.json'
jira_config = json.load(open(config_path))["JIRA"]

# Add Jira connection
# jira = JIRA.Jira(url=jira_config["JiraBaseURL"], username=jira_config["JiraUser"], password=jira_config["JiraPass"]) #Use this method if you want to login with username and PW


jira = JIRA.Jira(url=jira_config["JiraBaseURL"], token=jira_config["JiraToken"])
query = 'project=%s' % (jira_config['ProjectKey'])
issue_count = jira.jql(query)["total"] #fetch how many issues there are (mind you, this method only returns issues that are unresolved -> Cannot use for cleanup)
issues = jira.get_all_project_issues("WASP", fields='*all', limit = issue_count)

issue_dict = {} #invoke a dictionary for the sorting

for issue in issues: #Let's sort through the issue summaries and list versions of each SW package
    if issue["fields"]["status"]["name"] == "Production":
        summary_split = issue["fields"]["summary"].split("@")
        buffer = [[int(item) for item in summary_split[1].split(".")]] + [issue["key"]] #ATTENTION -> You need this weird structure of the list in order for .sort() to work
        try: issue_dict[summary_split[0]].append(buffer)
        except: issue_dict[summary_split[0]] = [buffer] #ATTENTION -> Buffer needs to be added as a tuplet with the square brackets to form the first element, otherwise sorting won't work
'''
returns a dictionary with the structure: 
issue_dict =    {"SOFTWARE NAME": [["VERSION",","JIRA ISSUE KEY"],["VERSION"...
                 "SOFTWARE NAME": [["VERSION","JIRA ISSUE KEY"], ... }
The issue key is needed for the deletion request
'''

to_be_deleted = [] #list of issue keys to be deleted

for software_name in issue_dict: #take each package to determine the issue keys to be deleted
    issue_dict[software_name].sort(reverse=True) #sorts the tuplets in descending order (first element is the highest version number)
    if len(issue_dict[software_name])>jira_config['VersionsToKeep']:
        to_be_deleted.extend(issue_dict[software_name][jira_config['VersionsToKeep']:])


#This will pull the trigger (delete all in to_be_deleted) from the Jira Board
ans = input("Are you sure, that you want to delete old issue [y/n] ?")

try:
    if ans.lower() == "y":
        for issue in to_be_deleted:
            jira.delete_issue(issue[1])
            print("Deleted")
            print("Thanks for choosing the Jira cleaner, see you next time")
    elif ans.lower() == "n":
        print("Maybe next time...")
    else:
        print("No valid answer...")
except:
    print("No valid answer...")











