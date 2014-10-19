import fnmatch
import os
import re

from fs.errors import ResourceNotFoundError
from fs.memoryfs import MemoryFS
from fs.mountfs import MountFS
from fs.multifs import MultiFS
from fs.osfs import OSFS
from fs.zipfs import ZipFS


class VFS(MountFS):

    resources = [
        'game.pak',
        'localize.pak',
        'expansion.pak',
        'resource/patch/*.pat',
        'resource',
    ]

    def __init__(self, root_path='', *args, **kwargs):
        MountFS.__init__(self, *args, **kwargs)
        self.root_path = root_path
        resources = [r.replace('/', os.sep).strip(os.sep)
                     for r in self.resources]
        self.multifs = MultiFS()

        for resource in resources:
            pattern = re.compile(fnmatch.translate(resource), re.IGNORECASE)
            for root, dirs, files in os.walk(root_path):
                for d in sorted(dirs):
                    full = os.path.join(root, d)
                    path = full.replace(root_path, '').strip(os.sep)
                    if re.match(pattern, path):
                        self.multifs.addfs(path, OSFS(full))
                for f in sorted(files):
                    full = os.path.join(root, f)
                    path = full.replace(root_path, '').strip(os.sep)
                    if re.match(pattern, path):
                        self.multifs.addfs(path, ZipFS(full))
        self.mountdir('resource', self.multifs)
        self.mountdir('cache', MemoryFS())
