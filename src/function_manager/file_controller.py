import os.path
import shutil
import uuid


class FileController:
    def __init__(self):
        self.storage_dir = None
        self.container_id_dir = {}

    def init(self, storage_dir):
        self.storage_dir = storage_dir
        if os.path.exists(self.storage_dir):
            shutil.rmtree(self.storage_dir)
        os.mkdir(self.storage_dir)
        os.chmod(self.storage_dir, 0o777)


    def allocate_dir(self):
        while True:
            dir_id = uuid.uuid4().hex
            path = os.path.join(self.storage_dir, dir_id)
            if not os.path.exists(path):
                os.mkdir(path, mode=0o777)
                os.chmod(path, 0o777)
                return path, dir_id

    def bind(self, container_id, dir_id):
        self.container_id_dir[container_id] = dir_id

    def get_container_dir(self, container_id):
        return os.path.join(self.storage_dir, self.container_id_dir[container_id])


file_controller = FileController()
