import os, sys, copy, wx, platform, pygame, chardet
from pygame.locals import *
from pathlib import Path as _Path


# pygame用のキーインプットクラス
class Input:

    def __init__(self):
        self.bind = {}
        self.frozen = False

    def __add__(self, b):
        new = Input()
        new.bind = self.bind | b.bind
        return new

    # eventから何が入力されたのか読み取って実行
    def get(self, event):
        if not self.frozen:
            a = {event.key}
            if KMOD_SHIFT & event.mod:
                a.add('shift')
            if KMOD_CTRL & event.mod:
                a.add('ctrl')
            if KMOD_ALT & event.mod:
                a.add('alt')
            a = self.bind.get(frozenset(a))
            if a:
                a()

    # キーバインドを登録する
    def set(self, key, fn):
        self.bind[frozenset(key)] = fn

    def reset(self):
        self.__init__()

    def stop(self):
        self.frozen = True

    def restart(self):
        self.frozen = False


# パス用クラス
class Path:

    def __init__(self, path = '.'):
        self.path = _Path(path).expanduser().resolve()

    def __str__(self):
        return str(self.path.as_posix())

    def __truediv__(self, p):
        return Path(str(self.path / str(p)))

    # as_posixではない文字列パスを返す
    def true_str(self):
        return str(self.path)

    def ext(self):
        return self.path.suffix[1:]

    def is_root(self):
        return str(self.path) == str(self.path.parent)

    def is_exist(self):
        return self.path.exists()

    def parent(self):
        return Path(self.path.parent)

    def name(self):
        return self.path.name

    def mkdir(self):
        self.path.mkdir()

    def rename(self, newpath):
        self.path.rename(_Path(str(newpath)))

    def relative(self, path):
        return os.path.relpath(str(self.path), str(path))

# ファイルリスト
class FilerFileList:

    def __init__(self, side = None, history = None):
        self.filelist = FileList('.')
        self.line = 0
        self.scroll = 0
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

# os.scandirのラッパー？
class FileList:

    def __init__(self, path = '.'):
        self.path = Path(str(path))
        self.permission_error = False

        try:
            self.filelist = list(os.scandir(str(self.path)))
        except PermissionError:
            self.filelist = []
            self.permission_error = True

    def __len__(self):
        return len(self.filelist)

    def __getitem__(self, i):
        return FileListItem(self.filelist[i])

    def is_empty(self):
        return len(self) == 0

# os.scandirの要素のラッパー？
class FileListItem:

    def __init__(self, parent):
        self.item = parent

    def name(self):
        return self.item.name

    def path(self):
        return Path(self.item.path)

    def is_dir(self):
        return self.item.is_dir()

    def ext(self):
        return Path(self.name()).ext()

    def rename(self, newpath):
        self.path().rename(newpath)

    def size(self):
        return self.item.stat().st_size

# 履歴用のクラス
class History:

    def __init__(self, d = dict()):
        self.dict = d

    def set(self, path, line = 0, scroll = 0):
        self.dict[str(path)] = HistoryItem(line, scroll)

    def get(self, path):
        return self.dict.get(str(path))

# 履歴の要素のクラス？
class HistoryItem:

    def __init__(self, line = 0, scroll = 0):
        self.line = line
        self.scroll = scroll

# 拡張子実行用のクラス
class ExtCommand:

    def __init__(self):
        self.dict = dict()

    def set(self, ext, fn):
        self.dict[ext] = fn

    def get(self, ext):
        return self.dict.get(ext)


# infoのフォルダのファイル数やサイズ等の調査のための構造体
class FolderSearch:

    def __init__(self):
        self.size = 0
        self.file_num = 0
        self.folder_num = 0
        self.is_over = False
        self.permission_error = False


# WXのインプットダイアログ
def wx_input_dialog(msg):
    dlg = wx.TextEntryDialog(None, msg)
    result = dlg.ShowModal()
    dlg.Destroy()
    return result != wx.ID_CANCEL and dlg.GetValue()

# WXのYESNOダイアログ
def wx_question_dialog(msg):
    dlg = wx.MessageDialog(None, msg, '', wx.YES_NO | wx.CANCEL)
    val = dlg.ShowModal()
    dlg.Destroy()

    if val == wx.ID_YES:
        return True
    else:
        return False

# windowsかどうか
def is_windows():
    return platform.system() == 'Windows'

# linuxかどうか
def is_linux():
    return platform.system() == 'Linux'

# ファイルサイズのフォーマット
def filesize_format(size):
    # 1TB以上
    if size >= pow(1024, 4):
        a = pow(1024, 4)
        b = 'TB'
    elif size >= pow(1024, 3):
        a = pow(1024, 3)
        b = 'GB'
    elif size >= pow(1024, 2):
        a = pow(1024, 2)
        b = 'MB'
    elif size >= pow(1024, 1):
        a = pow(1024, 1)
        b = 'KB'
    else:
        a = 1
        b = 'B'
    return '%s %s' % (str(round(size / a, 2)), b)

# 文字コードを推測
def charcode(path):
    with open(path, 'rb') as f:
        return chardet.detect(f.read())['encoding']
