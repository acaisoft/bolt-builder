import tempfile
import uuid
import os

import git

from google_cloud_build import GoogleCloudBuild
from locust_wrapper_packer import LocustWrapperPacker

import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

logger = logging.getLogger(__name__)


def get_docker_image_destination(tenant_id: str, project_id: str):
    name = str(uuid.uuid4())
    return '{base_registry}:tenants-{tenant}-projects-{project}-{name}'.format(
        base_registry='eu.gcr.io/acai-bolt/bolt-deployer-builds-local'.rstrip('/'),
        tenant=tenant_id,
        project=project_id,
        name=name,
    )


repo_url = os.environ.get('REPOSITORY_URL')
repo_path = tempfile.mkdtemp()
tenant_id = os.environ.get('TENANT_ID')
project_id = os.environ.get('PROJECT_ID')

logger.info(f'Cloning repository {repo_url}...')
repo = git.Repo.clone_from(repo_url, repo_path, depth=1)
logger.info(f'Repository cloned to {repo_path}')

logger.info('Wrapping repository')
wrapper = LocustWrapperPacker()
wrapper.wrap(repo_path)
logger.info('Repository wrapped')

destination = get_docker_image_destination(tenant_id, project_id)
logger.info(f'Starting to build image {destination}')
google_cloud_build = GoogleCloudBuild()
google_cloud_build.build(repo_path, destination)
logger.info('Image built')

with open('/tmp/image.txt', 'w+') as file:
    file.write(destination)