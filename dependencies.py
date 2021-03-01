#!/usr/bin/env python

import logging
import click
import git
from gitlab_helper import GitlabHelper


@click.command()
@click.argument('gitlab-url')
@click.argument('private-token')
@click.option('--group-name', required=True, help='Group name to process')
@click.option('--loglevel', default='INFO')
def dependencies(gitlab_url, private_token, loglevel, group_name):
    # Configure logger
    numeric_loglevel = getattr(logging, loglevel.upper(), None)
    logging.basicConfig(level=numeric_loglevel)
    logging.info(
        f"Dependencies program started: gitlab_url={gitlab_url}, private_token={private_token}")

    # private token or personal token authentication
    gitlab_connection = GitlabHelper(gitlab_url, private_token)
    logging.info("GitlabHelper created")

    projects = gitlab_connection.get_project_id_list(
        group_name, skip_archived=False)
    num_projects = len(projects)
    logging.info(f"There are {num_projects} projects in {group_name}")
    logging.info(
        "------------------------------------------------------------")
    num_archived_projs = 0
    for project in projects:
        project_dict = project.attributes
        http_clone_url = project_dict['http_url_to_repo'].replace(
            "https://", f"https://oauth2:{private_token}@")
        logging.info(
            f" - Project name: {project_dict['name']} {'[archived]' if project_dict['archived'] else ''}")
        if project_dict['archived']:
            num_archived_projs += 1
        else:
            logging.info(f"   -> HTTP URL : {http_clone_url}")
            logging.info("   -> Going to clone repository...")
            git.Repo.clone_from(
                http_clone_url, f"tmp/{project_dict['name']}", env={'GIT_LFS_SKIP_SMUDGE': '1'})
            logging.info("   -> Done.")
    logging.info(
        "------------------------------------------------------------")
    logging.info(
        f"{num_archived_projs} archived project(s) out of the {num_projects}.")


if __name__ == '__main__':
    dependencies()
