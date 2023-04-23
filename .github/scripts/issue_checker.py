import os
import re
from github import Github

# Get GitHub token from environment variables
token = os.environ['GITHUB_TOKEN']
g = Github(token)

# Get the current repository
repo = g.get_repo(os.environ['GITHUB_REPOSITORY'])

# Get the issue number from the event payload
issue_number = int(os.environ['ISSUE_NUMBER'])

# Get the issue object
issue = repo.get_issue(issue_number)

# Define the keywords to search for in the issue
keywords = ['Python', 'Installing requirements for Web UI', 'Commit hash', 'Launching Web UI with arguments', 'Model loaded', 'text2video']

# Check if ALL of the keywords are present in the issue
def check_keywords(issue_body, keywords):
    for keyword in keywords:
        if not re.search(r'\b' + re.escape(keyword) + r'\b', issue_body, re.IGNORECASE):
            return False
    return True

# Check if the issue title has at least a specified number of words
def check_title_word_count(issue_title, min_word_count):
    words = issue_title.replace("/", " ").replace("\\\\", " ").split()
    return len(words) >= min_word_count

# Check if the issue title is concise
def check_title_concise(issue_title, max_word_count):
    words = issue_title.replace("/", " ").replace("\\\\", " ").split()
    return len(words) <= max_word_count

# Check if the commit ID is in the correct hash form
def check_commit_id_format(issue_body):
    match = re.search(r'webui commit id - ([a-fA-F0-9]+)', issue_body)
    if not match:
        return False
    webui_commit_id = match.group(1)
    if not (7 <= len(commit_id) <= 40):
        return False
    match = re.search(r'txt2vid commit id - ([a-fA-F0-9]+)', issue_body)
    if match:
        return False
    t2v_commit_id = match.group(1)
    if not (7 <= len(t2v_commit_id) <= 40):
        return False
    return True

# Only if a bug report
if check_keywords(issue.title, ['[Bug]']) and not check_keywords(issue.title, ['[Feature Request]']):
    # Initialize an empty list to store error messages
    error_messages = []

    # Check for each condition and add the corresponding error message if the condition is not met
    if not check_keywords(issue.body, keywords):
        error_messages.append("Include **THE FULL LOG FROM THE START OF THE WEBUI** in the issue description.")

    if not check_title_word_count(issue.title, 3):
        error_messages.append("Make sure the issue title has at least 3 words.")

    if not check_title_concise(issue.title, 9):
        error_messages.append("The issue title should be concise and contain no more than 9 words.")

    if not check_commit_id_format(issue.body):
        error_messages.append("Provide a valid commit ID in the format 'commit id - [commit_hash]' **both** for the WebUI and the Extension.")
        
    # If there are any error messages, close the issue and send a comment with the error messages
    if error_messages:
        # Add the "not planned" label to the issue
        not_planned_label = repo.get_label("invalid")
        issue.add_to_labels(not_planned_label)
        
        # Close the issue
        issue.edit(state='closed')
        
        # Generate the comment by concatenating the error messages
        comment = "This issue has been closed due to incorrect formatting. Please address the following mistakes and reopen the issue:\n\n"
        comment += "\n".join(f"- {error_message}" for error_message in error_messages)

        # Add the comment to the issue
        issue.create_comment(comment)
    elif issue.state is 'closed':
        issue.edit(state='open')
        issue.delete_labels()
        bug_label = repo.get_label("bug")
        issue.add_to_labels(bug_label)
        comment = "Thanks for addressing your formatting mistakes. The issue has been reopened now."
        issue.create_comment(comment)
