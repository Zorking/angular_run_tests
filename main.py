import logging
import subprocess

import settings

logging.basicConfig(filename=settings.LOG_FILE, level=logging.ERROR, format='[%(asctime)s] %(message)s')
logging.FileHandler(filename=settings.LOG_FILE, mode='a')
logging.getLogger().addHandler(logging.StreamHandler())


def setup_git():
    checkout_master = subprocess.Popen(['git', 'checkout', 'master'], cwd=settings.DIR)
    checkout_master.wait()
    delete_branches_cmd = 'git branch | grep -v "master" | xargs git branch -D'
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
        print(line)
        if fail_text in line:

            return True
        if success_text in line:
            return False


def run_tests():
    npm_test = subprocess.Popen('npm test --single-run=true', shell=True, cwd=settings.DIR, stdout=subprocess.PIPE)
    if is_failed(npm_test, '✖', 'SUMMARY:'):
        logging.error('Tests failed for: {}'.format(branch))
    npm_test.kill()


def run_build():
    npm_serve = subprocess.Popen('npm start', shell=True, cwd=settings.DIR, stdout=subprocess.PIPE)
    if is_failed(npm_serve, 'Failed to compile', 'Compiled successfully'):
        logging.error('Build failed for: {}'.format(branch))
    npm_serve.kill()


if __name__ == "__main__":
    for branch in settings.BRANCHES:
        setup_git()
        run_tests()
        run_build()
