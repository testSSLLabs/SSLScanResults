from git import Repo
import os
import shutil
import subprocess
from logger_helper import logger

PATH_OF_GIT_REPO = r'/tmp/SSLLab_hosts_and_report'
SSLLab_hosts_and_report_GIT_REPO = "git@github.com:testSSLLabs/SSLLab_hosts_and_report.git"
SSLLab_hosts_and_report_LINK = "https://github.com/testSSLLabs/SSLLab_hosts_and_report/tree/main/Reports"
COMMIT_MESSAGE = 'New reports'
DESTINATION_PATH_OF_GIT_REPO = os.path.join(PATH_OF_GIT_REPO, ".git")

def clone_report_repo():
    try:
        logger.info(f"Removing any existing Repo [{PATH_OF_GIT_REPO}]") 
        shutil.rmtree("/tmp/SSLLab_hosts_and_report", ignore_errors=True)
        logger.info(f"Cloning Report repo at [{PATH_OF_GIT_REPO}]")
        Repo.clone_from(SSLLab_hosts_and_report_GIT_REPO, PATH_OF_GIT_REPO)
        logger.info(f"Successfully Cloned rep at [{PATH_OF_GIT_REPO}]")
    except Exception as Err:
        logger.info(f"Could not clone the Report repo at [{PATH_OF_GIT_REPO}] due to error: \n{Err}")
        return 1

def git_push():
    try:
        repo = Repo(DESTINATION_PATH_OF_GIT_REPO)
        repo.git.add("--all")
        repo.index.commit(COMMIT_MESSAGE)
        repo.git.push()
        logger.info(f"Successfully pushed new Reports at [{PATH_OF_GIT_REPO}]")
        logger.info(f"Please check the JSON/CSV Reports at [{SSLLab_hosts_and_report_LINK}]")
    except Exception as Err:
        logger.info(f"Could not push the Report repo at [{PATH_OF_GIT_REPO}] due to error: \n{Err}")
        return 1

