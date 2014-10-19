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
        multifs = MultiFS()
        self.multifs = multifs

        for resource in resources:
            pattern = re.compile(fnmatch.translate(resource), re.IGNORECASE)
            for root, _, files in os.walk(root_path):
                path = root.replace(root_path, '').strip(os.sep)
                if re.match(pattern, path):
                    multifs.addfs(path, OSFS(root))
                else:
                    files.sort()
                    for f in files:
                        full = os.path.join(root, f)
                        path = full.replace(root_path, '').strip(os.sep)
                        if re.match(pattern, path):
                            multifs.addfs(path, ZipFS(full))
        self.mountdir('resource', multifs)
        self.mountdir('cache', MemoryFS())
