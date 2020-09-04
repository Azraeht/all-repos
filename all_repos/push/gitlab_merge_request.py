import json
import subprocess
import urllib
from typing import NamedTuple, Dict

from all_repos import autofix_lib
from all_repos import git
from all_repos import gitlab_api


class Settings(NamedTuple):
    access_token: str
    base_url: str = 'https://gitlab.example.com/api/v4'
    fork: bool = False
    mr_bodies: Dict[str, str] = {}

# https://gitlab.com/gitlab-org/gitlab-ce/issues/64320


def get_mr_url(repo_slug: str, settings: Settings) -> int:
    headers = {'Private-Token': settings.access_token}

    url_slug = urllib.parse.quote(repo_slug, safe='')

    resp = gitlab_api.req(
        f'{settings.base_url}/projects/{url_slug}',
        headers=headers, method='GET',
    )
    return resp.json['_links']['merge_requests']

def push(settings: Settings, branch_name: str) -> None:
    headers = {
        'Private-Token': settings.access_token,
        'Content-Type': 'application/json'
        }

    remote_url = git.remote('.')
    _, _, repo_slug = remote_url.rpartition(':')
    repo_slug = repo_slug.replace('.git', '')
    repo_short_name = repo_slug.split('/')[-1]

    if settings.fork:
        raise NotImplementedError('fork support  not yet implemented')
    else:
        remote = 'origin'
        head = branch_name

    autofix_lib.run('git', 'push', remote, f'HEAD:{branch_name}', '--quiet')

    title = subprocess.check_output(('git', 'log', '-1', '--format=%s')).decode().strip()
    if repo_short_name in settings.mr_bodies:
        body = settings.mr_bodies[repo_short_name]
    else:
        body = subprocess.check_output(('git', 'log', '-1', '--format=%b')).decode().strip()

    data = json.dumps({
        'title': title,
        'description': body,
        'target_branch': autofix_lib.target_branch(),
        'source_branch': branch_name,
    }).encode()

    resp = gitlab_api.req(
        get_mr_url(repo_slug, settings),
        data=data, headers=headers, method='POST',
    )

    url = resp.json['web_url']
    print(f'Pull request created at {url}')
