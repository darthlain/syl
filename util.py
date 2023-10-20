import os, sys, copy, wx
from pygame.locals import *
from pathlib import Path as _Path


class Input:

    def __init__(self):
        self.bind = {}
        self.frozen = False

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


def wx_input_dialog(msg):
    dlg = wx.TextEntryDialog(None, msg)
    result = dlg.ShowModal()
    dlg.Destroy()
    return result != wx.ID_CANCEL and dlg.GetValue()

def wx_question_dialog(msg):
    dlg = wx.MessageDialog(None, msg, '', wx.YES_NO | wx.CANCEL)
    val = dlg.ShowModal()
    dlg.Destroy()

    if val == wx.ID_YES:
        return True
    else:
        return False
