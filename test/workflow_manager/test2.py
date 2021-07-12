import os
import docker

client = docker.from_env()
for image in client.images.list():
    if image.tags[0].startswith('action_utility'):
        client.images.remove(image.id)
