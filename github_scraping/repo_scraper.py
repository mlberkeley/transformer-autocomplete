# Imports
# NOTE: Will need to install requests[secure] via >>> pip install "requests[secure]"
from github import Github # PyGithub
from github.Repository import Repository
from base64 import b64decode

import pandas as pd 

# TODO: Extend this dictionary
extension_to_langauge = {
    "java" : "Java",
    "py" : "Python",
    "cpp" : "C++",
    "cc" : "C++",
    "c" : "C",
    "go" : "Go"
}

valid_extensions_set = set([extension for extension in extension_to_langauge])

# A function to walk a repo and save the repo name, path, and file contents of all files in the repo to a dataframe
# Expects repo to be a github.Repository.Repository object
# TODO: Don't retreive contents of junk files, check if we've , sleep on rate limit (wrap API calls)
def get_repo_files(repo):
    repo_url_list = []
    paths_in_repo = []
    b64_file_contents = []
    repo_url = repo.html_url

    # Basically a DFS on the repo
    paths_to_retreive = ["/"]

    while paths_to_retreive:
        path_to_get = paths_to_retreive.pop()
        print(path_to_get)
        contents = repo.get_contents(path_to_get)
        if isinstance(contents, list):
            # Then this is a directory
            for subpath in contents:
                paths_to_retreive.append(subpath.path)
        else:
            extension = path_to_get.split(".")[-1]
            print(extension)
            print(extension in valid_extensions_set)
            if (extension in valid_extensions_set):
                # Dont' want to record junk, so we only save actual source code files
                repo_url_list.append(repo_url)
                paths_in_repo.append(path_to_get)
                b64_file_contents.append(contents.content)
    return pd.DataFrame(data={"Repo Url" : repo_url_list, 
                            "Path in Repo" : paths_in_repo, 
                            "B64 File Contents" : b64_file_contents})


#TODO: Get list of public repos- filter by stars/followers/fork-iness

g = Github("INSERT TOKEN HERE")
sample_repo= g.get_repo("mlberkeley/transformer-autocomplete")

sample_contents_df = get_repo_files(sample_repo)
print(sample_contents_df.head())