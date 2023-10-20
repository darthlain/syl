from util import FileList, Path
import pygame

class FilerFileList:

    def __init__(self, mode, side = None, history = None):
        self.filelist = FileList('.')
        self.line = 0
        self.scroll = 0
        self.mode = mode
        self.side = side
        self.select = []
        self.history = history
        self.fileinfo_flag = False

    def path(self):
        return self.filelist.path

    def __len__(self):
        return len(self.filelist)

    def __getitem__(self, i):
        return self.filelist[i]

    def get_all(self):
        return [self.__getitem__(i) for i in range(self.__len__())]

    def chdir(self, path = str(Path('.'))):
        self.history.set(self.filelist.path, self.line, self.scroll)

        a = self.history.get(path)
        if a:
            self.line = a.line
            self.scroll = a.scroll
        else:
            self.line = 0
            self.scroll = 0

        self.select = []
        self.filelist = FileList(str(path))

    def is_empty(self):
        return self.filelist.is_empty()

    def displayed_item(self, i):
        if i < len(self.filelist) - self.scroll:
            return self.filelist[i + self.scroll]
        else:
            return None

    def line_item(self):
        if self.is_empty():
            return None
        else:
            return self.filelist[self.line + self.scroll]

class History:

    def __init__(self, d = dict()):
        self.dict = d

    def set(self, path, line = 0, scroll = 0):
        self.dict[str(path)] = HistoryItem(line, scroll)

    def get(self, path):
        return self.dict.get(str(path))

class HistoryItem:

    def __init__(self, line = 0, scroll = 0):
        self.line = line
        self.scroll = scroll

class ImageDraw:

    def __init__(self):
        self.image = None
        self.aspect = True
        self.resize = None

class ExtCommand:

    def __init__(self):
        self.dict = dict()

    def set(self, ext, fn):
        self.dict[ext] = fn

    def get(self, ext):
        return self.dict.get(ext)
