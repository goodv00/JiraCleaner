import json
import os

from atlassian import jira as JIRA

# OS specific strings - find configs and libs file and import values
sys_path = os.path.sep
dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = f'{dir_path}{sys_path}configs{sys_path}config.json'

jira_config = json.load(open(config_path))["JIRA"]

def jira_init():

    query = 'project=%s' % (jira_config['ProjectKey'])
    # Add Jira connection
    try:
        jira = JIRA.Jira(
            url=jira_config["JiraBaseURL"],
            username=jira_config["JiraUser"],
            password=jira_config["JiraPass"]
        )
        # Fetches how many issues there are (mind you, this method only returns issues that are unresolved)
        issue_count = jira.jql(query)["total"]
        print('Authentication success')
        print(f'Jira issues found: {issue_count}')
        return jira

    except:
        # Use this method if you want to login with a token
        jira = JIRA.Jira(url=jira_config["JiraBaseURL"],
                         token=jira_config["JiraToken"]
        )
        print('Trying to use Jira Token')
        try:
            issue_count = jira.jql(query)["total"]
            print(f'Jira issues found: {issue_count}')
            return jira

        except:
            print('Authentication failed')
            return

def jira_clean(jira):
    query = 'project=%s' % (jira_config['ProjectKey'])
    issue_count = jira.jql(query)["total"]
    issues = jira.get_all_project_issues("WASP", fields='*all', limit=issue_count)
    issue_dict = {}  # Invokes a dictionary for the sorting

    for issue in issues:  # Let's sort through the issue summaries and list versions of each SW package
        if issue["fields"]["status"]["name"] == "Production":
            summary_split = issue["fields"]["summary"].split("@")
            # ATTENTION -> You need this weird structure of the list in order for .sort() to work
            buffer = [[int(item) for item in summary_split[1].split(".")]] + [issue["key"]]
            try:
                issue_dict[summary_split[0]].append(buffer)
            except:
                # ATTENTION -> Buffer needs to be added as a list with the [] to form the first element
                issue_dict[summary_split[0]] = [buffer]
    del summary_split, issue

    '''
    returns a dictionary with the structure: 
    issue_dict =    {"SOFTWARE NAME": [["VERSION as [MAJOR, MINOR, DIST]",","JIRA ISSUE KEY"],["VERSION"...
                     "SOFTWARE NAME": [["VERSION","JIRA ISSUE KEY"], ... }
    The issue key is needed for the deletion request
    '''

    to_be_deleted = []  # List of issue keys to be deleted
    to_be_deleted_dict = {}

    for software_name in issue_dict:  # Takes each package to determine the issue keys to be deleted
        issue_dict[software_name].sort(reverse=True)  # Sorts the version numbers in descending order
        if len(issue_dict[software_name])>jira_config['VersionsToKeep']:
            to_be_deleted_dict[software_name] = []
            buffer = issue_dict[software_name][jira_config['VersionsToKeep']:]
            to_be_deleted.extend(buffer)
            buffer2 = ""
            for i in buffer:
                buffer2 = ".".join([str(i) for i in i[0]])
                to_be_deleted_dict[software_name].append(buffer2)

    print(f'{len(to_be_deleted)} issues were found to be old')
    ans1 = input("Would you like to see the versions to be deleted [y/n]? ")
    try:
        if ans1.lower() == "y":

            for software_name in to_be_deleted_dict:
                printout = software_name + "\n"
                for version in to_be_deleted_dict[software_name]:
                    printout += "\t\t" + version + "\n"
                print(printout)

        elif ans1.lower() == "n":
            print("Maybe next time...")
        else:
            print("No valid answer...")
    except:
        print("No valid answer...")


    # This will pull the trigger (deletes all in to_be_deleted) from the Jira Board
    ans = input("Are you sure, that you want to delete old issue [y/n]? ")
    try:
        if ans.lower() == "y":
            for issue in to_be_deleted:
                jira.delete_issue(issue[1])

            print("Done deleting")
            print("Thanks for choosing the Jira cleaner, see you next time")
        elif ans.lower() == "n":
            print("Maybe next time...")
        else:
            print("No valid answer...")
    except:
        print("No valid answer...")

if __name__ == '__main__':
    jira = jira_init()
    if not jira:
        print("Enter a valid Jira Authentication in /configs/config.json")
    else:
        jira_clean(jira)









