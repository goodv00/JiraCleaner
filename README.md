**This code is a clean-up script for a Jira Board.** 
Its purpose is to delete Jira Issues that concern software packages which are x-numbers of versions outdated. 

Start by installing all dependencies on your machine.

--> python -m pip install requirements.txt

Add you credentials to configs.json in the configs folder:

"JIRA" : {
"JiraBaseURL" : "https://jira.its.unibas.ch",
"ProjectKey" : "WASP",
"JiraUser" : "",
"JiraPass" : "",
"JiraToken" : "",
"VersionsToKeep": 5

Add at least one method (either Username and PW or a Token). Note, the config file allows you to specify how many ticket versions you want to keep.

After that, just run jiraCleanup.py