# Imports
# NOTE: Will need to install requests[secure] via >>> pip install "requests[secure]"
# and make sure that openssl in updated on your system
from github import Github, GithubException, RateLimitExceededException # PyGithub
from github.Repository import Repository
from base64 import b64decode, b64encode
import pandas as pd 
import time
import pickle
import os
from os.path import join, isdir, isfile
import subprocess

# Wrapper around github.Github class
class RotatingAuthRepo():

    def __init__(self, tokens_df_, repo_path_):
        self.tokens_df = tokens_df_
        self.tokens_list = list(self.tokens_df["Token Hex"])
        self.names_list = list(self.tokens_df["Name"])
        self.current_idx = 0
        self.repo_path = repo_path_
        # TODO: Wrap this call with a try/catch and rotate_token?
        self.github_obj = Github(self.get_current_token())
        self.repo = self.github_obj.get_repo(self.repo_path)

    
    def rotate_token(self):
        self.current_idx = (self.current_idx + 1) % len(self.tokens_list)
        self.github_obj = Github(self.get_current_token())
        self.repo = self.github_obj.get_repo(self.repo_path)

    def get_current_token(self):
        return self.tokens_list[self.current_idx]
    
    def get_current_name(self):
        return self.names_list[self.current_idx]

    def get_repo_url(self):
        return self.repo.html_url

    def get_contents(self, path_to_get):
        sleep_time_in_secs = 0.1
        obtained_results = False
        contents = None

        while not obtained_results:
            try:
                contents = self.repo.get_contents(path_to_get)
                obtained_results = True
            except RateLimitExceededException:
                # Rate limit exceeded- sleep and switch to next token
                # TODO: Output something on sleep for too long (send email or log somewhere visible)
                time.sleep(sleep_time_in_secs)
                sleep_time_in_secs *= 2
                self.rotate_token()
                print("Switched to using " + self.get_current_name() + "'s token")
            except GithubException as ge:
                if ge.data["errors"][0]["code"] == "too_large":
                    #TODO: Use github data API on failure here?
                    print("Tried to fetch too large of a file")
                else:
                    print("An unkown error occurred:")
                    print(ge.status, ge.data)
                    print("\n\n\n")
                contents = None
                obtained_results = True

        return contents
    
class Constants() :
    extension_to_langauge = {
        "java" : "Java",
        "py" : "Python",
        "cpp" : "C++",
        "cc" : "C++",
        "cxx" : "C++",
        "hxx" : "C++",
        "cp" : "C++",
        "cs" : "C#",
        "c" : "C",
        "h" : "C",
        "go" : "Go",
        "sh" : "Shell",
        "pl" : "Perl",
        "js" : "JavaScript",
        "has" : "Haskell",
        "lisp" : "lisp",
    }

    valid_extensions_set = set([extension for extension in extension_to_langauge])
    
# Checks if a given path is of a directory (assumed to be the case if the last part of the path doesn't have a ".")
# Can't use os function to check because this is for paths in git
def is_dir_path(path):
    return not ( "." in path.split("/")[-1])

# Checks if a given path points to a file with a valid source code extensions
def has_source_code_ext(path):
    extension = path.split(".")[-1].lower()
    return extension in Constants.valid_extensions_set

# Checks what language the source code file pointed to by path is (based on extension)
def get_language(path):
    extension = path.split(".")[-1].lower()
    return Constants.extension_to_langauge[extension]


# A function to walk a repo and save the repo name, path, and file contents of all files in the repo to a dataframe
# Expects repo to be a RotatingAuthRepo object
# NOTE: Will not follow paths in folders that have a "." in the name (hidden paths etc...)
def get_repo_files(repo):
    repo_url_list = []
    paths_in_repo = []
    b64_file_contents = []
    source_languages = []
    repo_url = repo.get_repo_url()

    # Basically a DFS on the repo
    paths_to_retreive = ["/"]

    while paths_to_retreive:
        path_to_get = paths_to_retreive.pop()
        contents = repo.get_contents(path_to_get)
        if contents is None:
            # If contents was too large to be retreived
            pass
        elif isinstance(contents, list):
            # Then this is a directory
            for subpath in contents:
                if is_dir_path(subpath.path) or has_source_code_ext(subpath.path):
                    # We only keep looking through subdirectories or valid source code files
                    paths_to_retreive.append(subpath.path)
        else:
            # Check the extension again to catch edgecases where a file has no extension so is 
            # expected to be a directory but is actually a source file
            if (has_source_code_ext(path_to_get)):
                repo_url_list.append(repo_url)
                paths_in_repo.append(path_to_get)
                source_languages.append(get_language(path_to_get))
                b64_file_contents.append(contents.content)
    
    return pd.DataFrame(data={"Repo Url" : repo_url_list, 
                            "Path in Repo" : paths_in_repo,
                            "Source Languages" : source_languages, 
                            "B64 File Contents" : b64_file_contents})

# A function to clone then walk a repo and save the repo name, path, and file contents of all files in the repo 
# to a dataframe. Expects repo to be a string of the form <user>/<repo>
def get_repo_files_wth_clone(repo):
    clone_command = "git clone https://github.com/" + repo + ".git"
    # TODO: Check for errors by checking returned output
    returned_output = subprocess.call(clone_command, shell=True)

    repo_url_list = []
    paths_in_repo = []
    b64_file_contents = []
    source_languages = []

    repo_url = "https://github.com/" + repo

    # Basically a DFS on the cloned repo
    paths_to_retrieve = [repo.split("/")[-1]]

    while paths_to_retrieve:
        path_to_get = paths_to_retrieve.pop()

        if isdir(path_to_get):
            for subpath in os.listdir(path_to_get):
                full_subpath = join(path_to_get, subpath)
                #print(full_subpath)
                if isdir(full_subpath) or (isfile(full_subpath) and has_source_code_ext(full_subpath)):
                    #print("Adding path " + full_subpath)
                    paths_to_retrieve.append(full_subpath)

        elif isfile(path_to_get):
            # Check the extension again to catch edgecases where a file has no extension so is 
            # expected to be a directory but is actually a source file
            if (has_source_code_ext(path_to_get)):
                repo_url_list.append(repo_url)
                paths_in_repo.append(path_to_get)
                source_languages.append(get_language(path_to_get))

                with open(path_to_get, "rb") as f:
                    file_contents = f.read()
                
                b64_file_contents.append(b64encode(file_contents))

        else:
            # Edgecase where a path des not point to a file or to a directory- just do nothing
            pass
        
    remove_command = "rm -rf ./" + repo.split("/")[-1]
    returned_output = subprocess.call(remove_command, shell=True)

    return pd.DataFrame(data={"Repo Url" : repo_url_list, 
                        "Path in Repo" : paths_in_repo,
                        "Source Languages" : source_languages, 
                        "B64 File Contents" : b64_file_contents})

# A function to get a list of public repos at least min_num_repos long, where each repo is not a 
# fork and has at least min_num_stars stars
def get_public_repos(tokens, min_num_repos, min_num_stars, initial_since=0):
    sleep_time_in_sec = 0.1
    current_idx = 0
    token_to_use = tokens[current_idx]
    valid_repos = []
    since = initial_since
    g = Github(token_to_use)
    
    while len(valid_repos) < min_num_repos:
        try:
            print("Getting batch since " + str(since))
            next_batch_of_repos = g.get_repos(since)
            for potential_repo in next_batch_of_repos:
                since += 1
                if (not potential_repo.fork) and (potential_repo.stargazers_count >= min_num_stars):
                    valid_repos.append(potential_repo.full_name)
        except RateLimitExceededException:
            print("Rate limit exceeded, sleeping for " + str(sleep_time_in_sec) + " seconds.")
            time.sleep(sleep_time_in_sec)
            sleep_time_in_sec *= 2
            current_idx = (current_idx + 1) % len(tokens)
            token_to_use = tokens[current_idx]
            g = Github(token_to_use)
        except GithubException as ge:
            # The case where we try to access a deleted repo (or general error case)
            print(ge.data["message"])
            pass
        
    
    return valid_repos

# Calculate how many repos we've already gone through (so we can start saving new pulled ones without 
# overwriting old pulled ones)
# NOTE: This simplistic calculation returns the result based on the max filename of the form <number>.csv
# in temp_dir (this is consistent with the saving method used here)
def get_max_saved_repo_num(temp_dir):
    filename_ints = [int(filename[:-4]) if filename[-4:] == ".csv" else -1 for filename in os.listdir(temp_dir)]
    if len(filename_ints) == 0:
        return -1
    return max(filename_ints)

def merge_and_save_temp_dfs(final_savefile, temp_dir):
    # Once we reach here then the to-do list must be empty
    # TODO: Right now the to-do list always saves with the last element on completion
    repo_urls = []
    paths_in_repo = []
    source_langs = []
    b64_file_contents = []

    max_repo_num = get_max_saved_repo_num(temp_dir)

    for i in range(max_repo_num + 1):
        repo_df = pd.read_csv(os.path.join(temp_dir, str(i) + ".csv"))
        repo_urls += list(repo_df["Repo Url"])
        paths_in_repo += list(repo_df["Path in Repo"])
        source_langs += list(repo_df["Source Languages"])
        b64_file_contents += list(repo_df["B64 File Contents"])


    final_df = pd.DataFrame(data={"Repo Url" : repo_urls, 
                                "Path in Repo" : paths_in_repo, 
                                "Source Languages" : source_langs, 
                                "B64 File Contents" : b64_file_contents})

    final_df.to_csv(final_savefile)

def scrape_repos_with_api(pickled_to_do_list, tokens_df, final_savefile, temp_dir):
    # Get the current list of repos to pull (which funcitons as a to-do list)
    with open(pickled_to_do_list, "rb") as f:
        repos_to_pull = pickle.load(f)
        # Edgecase when there's only 1 repo left- pickle loads as str instead of 1-element list
        if isinstance(repos_to_pull, str):
            repos_to_pull = [repos_to_pull]

    offset = get_max_saved_repo_num(temp_dir) + 1

    for i in range(len(repos_to_pull)):
        repo_to_pull = repos_to_pull.pop()
        rotating_auth_repo = RotatingAuthRepo(tokens_df, repo_to_pull)
        repo_files_df = get_repo_files(rotating_auth_repo)
        repo_files_df.to_csv(join(temp_dir, str(offset + i) + ".csv"))
        # "Save" updated to-do list so can resume on interrupt
        with open(pickled_to_do_list, "wb") as f:
            pickle.dump(repos_to_pull, f)

    merge_and_save_temp_dfs(final_savefile, temp_dir)
    


def scrape_repos_with_git_clone(pickled_to_do_list, final_savefile, temp_dir):
    # Get the current list of repos to pull (which funcitons as a to-do list)
    with open(pickled_to_do_list, "rb") as f:
        repos_to_pull = pickle.load(f)
        # Edgecase when there's only 1 repo left- pickle loads as str instead of 1-element list
        if isinstance(repos_to_pull, str):
            repos_to_pull = [repos_to_pull]

    offset = get_max_saved_repo_num(temp_dir) + 1

    for i in range(len(repos_to_pull)):
        repo_to_pull = repos_to_pull.pop()
        print("Getting repo: " + repo_to_pull)
        # TODO: Check to see if repo_to_pull name is ok (wouldn't be same as temp_dir or any existing dirs)
        repo_files_df = get_repo_files_wth_clone(repo_to_pull)
        repo_files_df.to_csv(join(temp_dir, str(offset + i) + ".csv"))
        # "Save" updated to-do list so can resume on interrupt
        with open(pickled_to_do_list, "wb") as f:
            pickle.dump(repos_to_pull, f)

    merge_and_save_temp_dfs(final_savefile, temp_dir)

def main():
    # Define constants/magic numbers
    # TODO: Take these in via command line args instead?
    USING_API = False
    TOKENS_CSV = "tokens.csv"
    DEST_CSV = "scraped_data.csv"
    TEMP_DIR = "tmp"
    MIN_STARS = 5
    NUM_REPOS = 10000
    REPO_LIST = "To-Do-List.p"


    if REPO_LIST is None:
        # Generate a new list of repos to pull from (since it's not already saved)
        tokens_df = pd.read_csv(TOKENS_CSV)
        repos_to_pull = get_public_repos(list(tokens_df["Token Hex"]), NUM_REPOS, MIN_STARS)
        save_file = "Repo_List_" + str(len(repos_to_pull)) + "_" + str(MIN_STARS) + "+.p"
        with open(save_file, "wb") as f:
            pickle.dump(repos_to_pull, f)
        REPO_LIST = save_file

    # Using API the scraping portion (getting list of repos is still done with API until I can get BigQuery to Work)
    if USING_API: 
        tokens_df = pd.read_csv(TOKENS_CSV)
        scrape_repos_with_api(REPO_LIST, tokens_df, DEST_CSV, TEMP_DIR)
    else:
        #Use git clone method
        scrape_repos_with_git_clone(REPO_LIST, DEST_CSV, TEMP_DIR)


if __name__ == "__main__":
    main()
