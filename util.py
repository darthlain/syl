import os, sys, copy, wx, platform, pygame, chardet, unicodedata
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

# ファイルリスト リストそのものではなくファイラー機能的なやつ
class FilerFileList:

    def __init__(self, side = None, history = None):
        self.filelist = FileList('.')
        self.line = 0
        self.scroll = 0
        self.side = side
        self.select = []
        self.history = history
        self.fileinfo_flag = False

    def pos(self):
        return self.scroll + self.line

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


class PygameKeyboardInput:

    def __init__(self):
        self.input = Input()
        self.set_keybind()
        self.reset()

    def reset(self):
        self.data = ''
        self.everyfn = None # タイプの度に呼び出される関数
        self.enterfn = None # enterを押したときに呼び出される関数
        self.bsfn = None    # backspaceを押したときに呼び出される関数

    def backspace(self):
        self.data = self.data[:-1]
        if self.bsfn:
            self.bsfn()

    def call_enterfn(self):
        if self.enterfn:
            self.enterfn()

    def add(self, a):
        self.data += a
        if self.everyfn:
            self.everyfn()

    def set_keybind(self, jp = True):
        self.input.set([K_a], lambda: self.add('a'))
        self.input.set([K_b], lambda: self.add('b'))
        self.input.set([K_c], lambda: self.add('c'))
        self.input.set([K_d], lambda: self.add('d'))
        self.input.set([K_e], lambda: self.add('e'))
        self.input.set([K_f], lambda: self.add('f'))
        self.input.set([K_g], lambda: self.add('g'))
        self.input.set([K_h], lambda: self.add('h'))
        self.input.set([K_i], lambda: self.add('i'))
        self.input.set([K_j], lambda: self.add('j'))
        self.input.set([K_k], lambda: self.add('k'))
        self.input.set([K_l], lambda: self.add('l'))
        self.input.set([K_m], lambda: self.add('m'))
        self.input.set([K_n], lambda: self.add('n'))
        self.input.set([K_o], lambda: self.add('o'))
        self.input.set([K_p], lambda: self.add('p'))
        self.input.set([K_q], lambda: self.add('q'))
        self.input.set([K_r], lambda: self.add('r'))
        self.input.set([K_s], lambda: self.add('s'))
        self.input.set([K_t], lambda: self.add('t'))
        self.input.set([K_u], lambda: self.add('u'))
        self.input.set([K_v], lambda: self.add('v'))
        self.input.set([K_w], lambda: self.add('w'))
        self.input.set([K_x], lambda: self.add('x'))
        self.input.set([K_y], lambda: self.add('y'))
        self.input.set([K_z], lambda: self.add('z'))

        self.input.set([K_a, 'shift'], lambda: self.add('A'))
        self.input.set([K_b, 'shift'], lambda: self.add('B'))
        self.input.set([K_c, 'shift'], lambda: self.add('C'))
        self.input.set([K_d, 'shift'], lambda: self.add('D'))
        self.input.set([K_e, 'shift'], lambda: self.add('E'))
        self.input.set([K_f, 'shift'], lambda: self.add('F'))
        self.input.set([K_g, 'shift'], lambda: self.add('G'))
        self.input.set([K_h, 'shift'], lambda: self.add('H'))
        self.input.set([K_i, 'shift'], lambda: self.add('I'))
        self.input.set([K_j, 'shift'], lambda: self.add('J'))
        self.input.set([K_k, 'shift'], lambda: self.add('K'))
        self.input.set([K_l, 'shift'], lambda: self.add('L'))
        self.input.set([K_m, 'shift'], lambda: self.add('M'))
        self.input.set([K_n, 'shift'], lambda: self.add('N'))
        self.input.set([K_o, 'shift'], lambda: self.add('O'))
        self.input.set([K_p, 'shift'], lambda: self.add('P'))
        self.input.set([K_q, 'shift'], lambda: self.add('Q'))
        self.input.set([K_r, 'shift'], lambda: self.add('R'))
        self.input.set([K_s, 'shift'], lambda: self.add('S'))
        self.input.set([K_t, 'shift'], lambda: self.add('T'))
        self.input.set([K_u, 'shift'], lambda: self.add('U'))
        self.input.set([K_v, 'shift'], lambda: self.add('V'))
        self.input.set([K_w, 'shift'], lambda: self.add('W'))
        self.input.set([K_x, 'shift'], lambda: self.add('X'))
        self.input.set([K_y, 'shift'], lambda: self.add('Y'))
        self.input.set([K_z, 'shift'], lambda: self.add('Z'))

        self.input.set([K_1], lambda: self.add('1'))
        self.input.set([K_2], lambda: self.add('2'))
        self.input.set([K_3], lambda: self.add('3'))
        self.input.set([K_4], lambda: self.add('4'))
        self.input.set([K_5], lambda: self.add('5'))
        self.input.set([K_6], lambda: self.add('6'))
        self.input.set([K_7], lambda: self.add('7'))
        self.input.set([K_8], lambda: self.add('8'))
        self.input.set([K_9], lambda: self.add('9'))
        self.input.set([K_0], lambda: self.add('0'))

        if jp:
            self.input.set([K_1, 'shift'], lambda: self.add('!'))
            self.input.set([K_2, 'shift'], lambda: self.add('"'))
            self.input.set([K_3, 'shift'], lambda: self.add('#'))
            self.input.set([K_4, 'shift'], lambda: self.add('$'))
            self.input.set([K_5, 'shift'], lambda: self.add('%'))
            self.input.set([K_6, 'shift'], lambda: self.add('&'))
            self.input.set([K_7, 'shift'], lambda: self.add('\''))
            self.input.set([K_8, 'shift'], lambda: self.add('('))
            self.input.set([K_9, 'shift'], lambda: self.add(')'))

            self.input.set([K_SEMICOLON],             lambda: self.add(';'))
            self.input.set([K_SEMICOLON, 'shift'],    lambda: self.add('+'))
            self.input.set([K_COLON],                 lambda: self.add(':'))
            self.input.set([K_COLON, 'shift'],        lambda: self.add('*'))
            self.input.set([K_COMMA],                 lambda: self.add(','))
            self.input.set([K_COMMA, 'shift'],        lambda: self.add('<'))
            self.input.set([K_PERIOD],                lambda: self.add('.'))
            self.input.set([K_PERIOD, 'shift'],       lambda: self.add('>'))
            self.input.set([K_SLASH],                 lambda: self.add('/'))
            self.input.set([K_SLASH, 'shift'],        lambda: self.add('?'))
            self.input.set([K_BACKSLASH],             lambda: self.add('\\'))
            self.input.set([K_BACKSLASH, 'shift'],    lambda: self.add('|'))
            self.input.set([K_AT],                    lambda: self.add('@'))
            self.input.set([K_AT, 'shift'],           lambda: self.add('`'))
            self.input.set([K_LEFTBRACKET],           lambda: self.add('['))
            self.input.set([K_LEFTBRACKET, 'shift'],  lambda: self.add('{'))
            self.input.set([K_RIGHTBRACKET],          lambda: self.add(']'))
            self.input.set([K_RIGHTBRACKET, 'shift'], lambda: self.add('}'))
            self.input.set([K_MINUS],                 lambda: self.add('-'))
            self.input.set([K_MINUS, 'shift'],        lambda: self.add('='))
            self.input.set([K_CARET],                 lambda: self.add('^'))
            self.input.set([K_CARET, 'shift'],        lambda: self.add('~'))
            self.input.set([0],                       lambda: self.add('\\'))
            self.input.set([0, 'shift'],              lambda: self.add('_'))

        self.input.set([K_BACKSPACE], lambda: self.backspace())
        self.input.set([K_SPACE], lambda: self.add(' '))
        self.input.set([K_RETURN], lambda: self.call_enterfn())


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


# 一行分
def onerow(s, lim = 80):

    if s == '':
        return ['']

    acc = 0
    acc2 = ''
    acc3 = False
    acc4 = []

    for i in range(len(s)):

        if unicodedata.east_asian_width(s[i]) in 'FWA':
            acc3 = True
        else:
            acc3 = False

        if acc3:
            acc += 2
        else:
            acc += 1

        if lim < acc:
            if acc3:
                acc = 2
            else:
                acc = 1
            acc4.append(acc2)
            acc2 = ''

        acc2 += s[i]

    if acc2 != '':
        acc4.append(acc2)

    return acc4
