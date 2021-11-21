import os
import docker

client = docker.from_env()
# containers = client.containers.list()
# for container in containers:
#     if container.name != 'couchdb_workflow' and container.name != 'redis':
#         container.remove(force=True)
# os.system('rm -rf /var/run/workflow_results/*.json')
for image in client.images.list():
    if image.tags == []:
        client.images.remove(image.id)
