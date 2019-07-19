from typing import Dict
from typing import NamedTuple

from all_repos import gitlab_api


class Settings(NamedTuple):
    access_token: str
    org: str
    base_url: str = 'https://gitlab.example.com/api/v4'
    # collaborator: bool = True
    # forks: bool = False
    # private: bool = False
    archived: bool = False


def list_repos(settings: Settings) -> Dict[str, str]:
    repos = gitlab_api.get_all(
        f'{settings.base_url}/groups/{settings.org}/projects',
        headers={'Private-Token': settings.access_token},
    )
    return gitlab_api.filter_repos_from_settings(repos, settings)
