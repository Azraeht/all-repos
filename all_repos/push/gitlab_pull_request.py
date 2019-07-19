import json
import subprocess
from typing import NamedTuple

from all_repos import autofix_lib
from all_repos import git
from all_repos import gitlab_api


class Settings(NamedTuple):
    access_token: str
    base_url: str = 'https://gitlab.example.com/api/v4'
    fork: bool = False

# https://gitlab.com/gitlab-org/gitlab-ce/issues/64320


def push(settings: Settings, branch_name: str) -> None:
    headers = {'Private-Token': settings.access_token}

    remote_url = git.remote('.')
    _, _, repo_slug = remote_url.rpartition(':')

    if settings.fork:
        raise NotImplementedError('fork support  not yet implemented')
    else:
        remote = 'origin'
        head = branch_name

    autofix_lib.run('git', 'push', remote, f'HEAD:{branch_name}', '--quiet')

    title = subprocess.check_output(('git', 'log', '-1', '--format=%s'))
    body = subprocess.check_output(('git', 'log', '-1', '--format=%b'))

    data = json.dumps({
        'title': title.decode().strip(),
        'body': body.decode().strip(),
        'base': autofix_lib.target_branch(),
        'head': head,
    }).encode()

    resp = gitlab_api.req(
        f'{settings.base_url}/{repo_slug}/pulls',
        data=data, headers=headers, method='POST',
    )

    url = resp.json['html_url']
    print(f'Pull request created at {url}')
