import logging
import subprocess

import os
import requests

import settings

logging.basicConfig(filename=settings.LOG_FILE, level=logging.INFO, format='[%(asctime)s] %(message)s')
logging.FileHandler(filename=settings.LOG_FILE, mode='a')
logging.getLogger().addHandler(logging.StreamHandler())

FNULL = open(os.devnull, 'w')

def setup_git():
    checkout_master = subprocess.Popen(['git', 'checkout', 'development'], cwd=settings.DIR)
    checkout_master.wait()
    delete_branches_cmd = 'git branch | grep -v "development" | xargs git branch -D'
    delete_branches = subprocess.Popen(delete_branches_cmd, cwd=settings.DIR, stdout=subprocess.PIPE, shell=True)
    delete_branches.wait()
    pull = subprocess.Popen(['git', 'pull'], cwd=settings.DIR)
    pull.wait()
    checkout_branch_cmd = 'git checkout -b {} --track origin/{}'.format(branch, branch)
    checkout_branch = subprocess.Popen(checkout_branch_cmd, cwd=settings.DIR, stdout=subprocess.PIPE, shell=True)
    checkout_branch.wait()


def is_failed(subprocess_stdout, fail_text, success_text):
    while True:
        line = subprocess_stdout.stdout.readline().decode("utf-8")
        if fail_text in line:
            return True
        if success_text in line:
            return False


def run_ng(command, task_type):
    ng_command = 'node_modules/@angular/cli/bin/ng {}'.format(command)
    npm_serve = subprocess.Popen(ng_command, shell=True, cwd=settings.DIR, stdout=FNULL)
    npm_serve.wait()
    return_code = npm_serve.returncode
    if return_code == 1:
        logging.info('ERROR: {} FAILED for: {}'.format(task_type, branch))
    npm_serve.kill()
    return return_code


if __name__ == "__main__":
    params = {'private_token': settings.GITLAB_TOKEN, 'state': 'opened'}
    url = '{}projects/{}/merge_requests'.format(settings.GITLAB_URL, settings.GITLAB_PROJECT_ID)
    merge_requests = requests.get(url, params=params).json()
    for merge_request in merge_requests:
        # if merge_request.get('work_in_progress'):
        branch = merge_request.get('source_branch')
        setup_git()
        tests_passed = True if run_ng(command='test --watch=false', task_type='Tests') == 0 else False
        if tests_passed:
            run_ng(command='build --prod --aot --base-href', task_type='Build')
