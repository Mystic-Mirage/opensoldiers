from fnmatch import translate
from fs.errors import ResourceNotFoundError
from fs.memoryfs import MemoryFS
from fs.mountfs import MountFS
from fs.multifs import MultiFS
from fs.osfs import OSFS
from fs.zipfs import ZipFS
import os
import re


class OpenSoldiersFS(MountFS):

    res_patterns = [
        ('', 'game.pak'),
        ('', 'localize.pak'),
        ('', 'expansion.pak'),
        ('resource/patch', '*.pat'),
        ('resource', '')
    ]

    resource_list = []

    def __init__(self, root_dir='', *args, **kwargs):
        super(OpenSoldiersFS, self).__init__(*args, **kwargs)
        self.root_dir = root_dir
        multi = MultiFS()
        mount = MountFS()
        for r, p in self.res_patterns:
            re_r = re.compile(translate(r), re.IGNORECASE)
            re_p = re.compile(translate(p), re.IGNORECASE)
            for root, dirs, files in os.walk(self.root_dir):
                sub_dir = root.replace(self.root_dir, '').strip(os.sep)
                if re.match(re_r, sub_dir):
                    if p:
                        for f in files:
                            if re.match(re_p, f):
                                self.resource_list.append((sub_dir, f))
                                full_r = os.path.join(self.root_dir, sub_dir, f)
                                multi.addfs(f, ZipFS(full_r))
                    else:
                        self.resource_list.append((sub_dir, ''))
                        full_r = os.path.join(self.root_dir, sub_dir)
                        for d in os.listdir(full_r):
                            re_i = re.compile(r'patch', re.IGNORECASE)
                            if not re.match(re_i, d):
                                mount.mountdir(d, OSFS(os.path.join(full_r, d)))
                        multi.addfs('mount', mount)
        if not self.resource_list:
            raise ResourceNotFoundError(self.root_dir)
        self.mountdir('resource', multi)
        self.mountdir('cache', MemoryFS())
