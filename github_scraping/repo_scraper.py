# Imports
# NOTE: Will need to install requests[secure] via >>> pip install "requests[secure]"
# and make sure that openssl in updated on your system
from github import Github, GithubException, RateLimitExceededException # PyGithub
from github.Repository import Repository
from base64 import b64decode
import pandas as pd 
import time
import pickle

TOKENS_CSV = "tokens.csv"
DEST_CSV = "scraped_data.csv"
MIN_STARS = 5
NUM_REPOS = 100

# Wrapper around github.Github class
class RotatingAuthRepo():

    def __init__(self, tokens_df_, repo_path_):
        self.tokens_df = tokens_df_
        self.tokens_list = list(self.tokens_df["Token Hex"])
        self.names_list = list(self.tokens_df["Name"])
        self.current_idx = 0
        self.repo_path = repo_path_
        # TODO: Wrap this call in a rotate token thing?
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
                # TODO: Output something on sleep for too long
                time.sleep(sleep_time_in_secs)
                sleep_time_in_secs *= 2
                self.rotate_token()
                print("Switched to using " + self.get_current_name() + "'s token")
            except GithubException as ge:
                if ge.data["errors"][0]["code"] == "too_large":
                    #TODO: Use github data API on failure here? Or just don't use this file
                    print("Tried to fetch too large of a file")
                else:
                    print("An unkown error occurred:")
                    print(ge.status, ge.data)
                    print("\n\n\n")
                contents = None
                obtained_results = True

        return contents
    

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
def is_dir_path(path):
    return not ( "." in path.split("/")[-1])

# Checks if a given path points to a file with a valid source code extensions
def has_source_code_ext(path):
    extension = path.split(".")[-1].lower()
    return extension in valid_extensions_set

# Checks what language the source code file pointed to by path is (based on extension)
def get_language(path):
    extension = path.split(".")[-1].lower()
    return extension_to_langauge[extension]


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
    
    #TODO: Save individual repo content and concatenate after (offline)?
    return pd.DataFrame(data={"Repo Url" : repo_url_list, 
                            "Path in Repo" : paths_in_repo,
                            "Source Languages" : source_languages, 
                            "B64 File Contents" : b64_file_contents})

# A function to get a list of public repos at least min_num_repos long, where each repo is not a 
# fork and has at least min_num_stars stars
# NOTE: Not robust to rate limiting, so call this once and save the result in a pickle file
def get_public_repos(token_to_use, min_num_repos, min_num_stars, initial_since=0):
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
        except GithubException as ge:
            # The case where we try to access a deleted repo
            print(ge.data["message"])
            pass
    
    return valid_repos
            

tokens_df = pd.read_csv("tokens.csv")

final_df = pd.DataFrame(data={"Repo Url" : [], "Path in Repo" : [], "Source Languages" : [], "B64 File Contents" : []})

# A list of 10,000 public repos to get the contents of- filtered by stars/fork-iness
repos_to_pull = get_public_repos(tokens_df["Token Hex"][2], NUM_REPOS, MIN_STARS)
#repos_to_pull = pickle.load("Repo_List.p")

#for repo_to_pull in repos_to_pull:
#    rotating_auth_repo = RotatingAuthRepo(tokens_df, repo_to_pull)
#    repo_files_df = get_repo_files(rotating_auth_repo)
    # TODO: Not memory efficient/feasible? Save each individual repo offline instead or save in batches
#    final_df = pd.concat([final_df, repo_files_df])

#final_df.to_csv(DEST_CSV)