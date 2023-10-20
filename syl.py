import os, sys, pygame, wx
from pygame.locals import *

from util import Input
from util import Input, FileList
from filer import FilerFileList, History, ImageDraw, ExtCommand

# infoのフォルダのファイル数やサイズ等の調査のための構造体
class FolderSearch:

    def __init__(self):
        self.size = 0
        self.file_num = 0
        self.folder_num = 0
        self.is_over = False
        self.permission_error = False

class Main:

    def __init__(self):

        # Options
        self.color_bg     = (0,0,0)
        self.color_fg     = (255,255,255)
        self.color_folder = (0,255,255)
        self.color_line   = (255,255,255)
        self.color_mark   = (0,0,255)
        self.color_path   = (0,255,0)
        self.color_info   = (0,255,0)
        self.color_frame  = (255,255,255)

        self.scrolloff = 5
        self.font_name = 'C:/Windows/Fonts/msgothic.ttc'
        self.font_size = 12
        self.open_command = None
        self.temp = os.environ['TEMP']
        self.shell = 'nyagos -c'
        # img_ext = ['bmp', 'png', 'jpg', 'jpeg', 'gif']
        self.img_ext = []
        self.init_path = '~/Desktop'
        self.message_show = 4

        self.mode_filer_str = 'NORMAL'
        self.mode_image_str = 'IMAGE'

        self.upinfo_show = 2 # ファイルリスト上の情報の行数
        self.downinfo_show = 1

        #
        pygame.init()
        self.screen_set_mode((600, 400))
        pygame.key.set_repeat(500, 35)
        self.clock = pygame.time.Clock()
        self.set_font(self.font_name, self.font_size)
        self.wx_app = wx.App()
        self.input = Input()
        self.set_keybind()
        self.set_filer_keybind()
        self.history = History()
        self.left_filelist = FilerFileList(mode = self.mode_filer_str, side = 'left', history = self.history)
        self.right_filelist = FilerFileList(mode = self.mode_filer_str, side = 'right', history = self.history)
        self.side = 'left'
        self.image = ImageDraw()
        self.ext = ExtCommand()
        self.set_imgext()

        if self.init_path:
            self.left_filelist.chdir(self.init_path)

    def quit(self):
        pygame.quit()
        sys.exit()

    def main(self):
        while 1:
            self.fill(self.color_bg)

            self.display_filer()

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit()

                if event.type == KEYDOWN:
                    self.input.get(event)

            self.clock.tick(60)

    def screen_set_mode(self, *args):
        self.screen = pygame.display.set_mode(*args, RESIZABLE)

    def screen_size(self):
        return pygame.display.get_surface().get_size()

    def half_screen_size(self):
        return self.screen_size()[0] // 2, self.screen_size()[1] // 2

    def _font_size(self):
        return self.font_size // 2, self.font_size

    # 画面の文字の表示件数
    def char_show(self):
        return self.screen_size()[0] // self._font_size()[0], \
               self.screen_size()[1] // self.font_size

    # ファイルリストの画面の表示件数
    def filelist_show(self):
        return self.char_show()[1] - self.upinfo_show - self.downinfo_show - self.message_show

    def filelist_x_show(self):
        return self.half_screen_size()[0] // self._font_size()[0]

    def set_font(self, name, size):
        self.font = pygame.font.Font(name, size)

    def echo(self, color, pos, s):
        text = self.font.render(s, True, color)
        self.screen.blit(text, pos)

    def fill(self, color):
        self.screen.fill(color)

    def square(self, color, pos, size):
        pygame.draw.rect(self.screen, color, pos + size)

    def line(self, color, fr, to, depth = 1):
        pygame.draw.line(self.screen, color, fr, to, depth)

    def echo_filelist(self, filelist):

        for i in range(self.filelist_show()):
            a = filelist.displayed_item(i)

            if filelist.side == 'right':
                p = self.half_screen_size()[0] + 1
            else:
                p = 0

            if a:
                if a.is_dir():
                    c = self.color_folder
                else:
                    c = self.color_fg

                self.echo(c, (p, self.font_size * (i + self.upinfo_show)), a.name())

    def fileitem_str(self, item):
        pass

    def filelist_left0pos(self, filelist):
        if filelist.side == 'left':
            return 0
        else:
            return self.half_screen_size()[0] + 1

    def filelist_left0pos2(self, side):
        if side == 'left':
            return 0
        else:
            return self.half_screen_size()[0] + 1

    def filelist_linepos(self, i, filelist):
        return self.font_size * (i + self.upinfo_show)

    def filelist_y0pos(self):
        return self.font_size * 2

    def display_filelist_line(self, filelist):
        p = self.filelist_left0pos(filelist)

        self.line(self.color_line,
                  (p, self.font_size * (filelist.line + 1 + self.upinfo_show)),
                  (p + self.half_screen_size()[0], self.font_size * (filelist.line + 1 + self.upinfo_show)))

    def echo_select(self, filelist):
        for i in range(self.filelist_show()):
            n = filelist.displayed_item(i)
            if not n:
                return
            elif n.name() in filelist.select:
                self.square(self.color_mark,
                            (self.filelist_left0pos(filelist), self.filelist_linepos(i, filelist)),
                            (self.half_screen_size()[0], self.font_size))

    def current_filelist(self):
        if self.side == 'left':
            return self.left_filelist
        else:
            return self.right_filelist

    def nocurrent_filelist(self):
        if self.side == 'left':
            return self.right_filelist
        else:
            return self.left_filelist

    def opposite_filelist(self, filelist):
        if filelist.side == 'left':
            return self.right_filelist
        else:
            return self.left_filelist

    # downで使うやつ
    def _scrolloff(self):
        return min(self.scrolloff, self.filelist_show() // 2)

    # ファイラ画面の描写
    def display_filer(self):
        self.fill(self.color_bg)
        self.echo(self.color_path, (0, 0), str(self.left_filelist.path()))
        self.echo_select(self.left_filelist)
        self.echo_filelist(self.left_filelist)
        self.square(self.color_bg,
                    (self.half_screen_size()[0], 0),
                    (self.half_screen_size()[0], self.screen_size()[1]))
        self.echo(self.color_path,
                  (self.half_screen_size()[0] + 1, 0),
                  str(self.right_filelist.path()))
        # 中央縦線
        self.line(self.color_frame,
                  (self.half_screen_size()[0], 0),
                  (self.half_screen_size()[0], self.screen_size()[1] - self.font_size * (self.downinfo_show + self.message_show)))
        self.line(self.color_frame,
                  (0, self._font_size()[1] * 2),
                  (self.screen_size()[0], self._font_size()[1] * 2))
        # ファイルリスト下線
        self.line(self.color_frame,
                  (0, self.screen_size()[1] - self.font_size * (self.downinfo_show + self.message_show)),
                  (self.screen_size()[0], self.screen_size()[1] - self.font_size * (self.downinfo_show + self.message_show)))
        # メッセージ下線
        self.square((240,240,240),
                    (0, self.screen_size()[1] - self.font_size * self.downinfo_show),
                    (self.screen_size()[0], self.screen_size()[1]))
        # 最下インフォ ファイル名
        if not self.current_filelist().is_empty():
            self.echo(self.color_bg,
                      (0, self.screen_size()[1] - self.font_size),
                      self.current_filelist().line_item().name())

        self.echo_select(self.right_filelist)
        self.echo_filelist(self.right_filelist)
        self.display_filelist_line(self.current_filelist())

        if self.current_filelist().mode == self.mode_image_str:
            self.display_filelist_line(self.nocurrent_filelist())

        if self.left_filelist.fileinfo_flag:
            self.display_fileinfo(self.left_filelist, self.right_filelist)
        if self.right_filelist.fileinfo_flag:
            self.display_fileinfo(self.right_filelist, self.left_filelist)

        self.image_draw()

    def display_fileinfo(self, filelist_info, filelist_view):
        if filelist_info.is_empty():
            return
        x0 = self.filelist_left0pos(filelist_view) + 1
        y0 = self.font_size * 2 + 1

        self.square(self.color_bg, (x0, y0), (self.half_screen_size()[0], self.font_size * self.filelist_show()))

        self.echo(self.color_fg, (x0, y0), filelist_info.line_item().name())
        self.echo(self.color_fg, (x0, y0 + self.font_size), '場所: %s' % str(filelist_info.line_item().path().parent()))

        size = self.filelist_item_size(filelist_info.line_item())

        if size:
            size_format = self.filesize_format(size)
        else:
            size_format = '不明'

        self.echo(self.color_fg, (x0, y0 + self.font_size * 2), 'サイズ: %s' % size_format)

    def fileinfo_list(self, filelist):
        lst = []
        lst.append('名前: %s' % filelist.line_item().name())
        lst.append('場所: %s' % str(filelist.line_item().path().parent()))

        searched = self.filelist_item_size(filelist.line_item())

        if searched.is_over:
            size_format = '不明'
        else:
            size_format = self.filesize_format(searched.size)

        if not searched.permission_error:
            lst.append('サイズ: %s' % size_format)

        if not searched.permission_error and not searched.is_over and filelist.line_item().is_dir():
            lst.append('ファイル数: %s' % searched.file_num)
            lst.append('フォルダー数: %s' % searched.folder_num)

        if searched.permission_error:
            lst.append('アクセス不可')

        return lst

    # ラインを指定のファイル名まで移動する
    def line_move(self, filelist, name):
        if filelist.is_empty():
            return

        filelist.line = 0
        filelist.scroll = 0
        for i in filelist:
            if i.name() == name:
                break
            else:
                self.down(filelist)

    def reload(self, filelist):
        p = not filelist.is_empty()
        if p:
            a = filelist.line_item().name()
        filelist.chdir(filelist.path())
        if p:
            self.line_move(filelist, a)

    def message(self, s):
        print(s)

    # ファイル操作のコマンドを作るときに使う
    def make_question_command(self, filelist, filelist2, name, fn, msg = ''):
        if filelist.is_empty():
            return

        if len(filelist.select) == 0:
            dlgmsg = name + '?' + msg
        else:
            dlgmsg = name + ' selects?' + msg

        a = util.wx_question_dialog(dlgmsg)
        
        if a:
            for i in filelist.select if filelist.select != [] else [filelist.line_item().name()]:
                try:
                    if filelist2 == None:
                        fn(filelist.path() / i)

                    s = name + ': ' + str(filelist.path() / i)

                    if filelist2 != None:
                        fn(filelist.path() / i, filelist2.path())
                        s += ' -> '
                        try:
                            s += filelist2.path().relative((filelist.path() / i).parent())
                        except ValueError:
                            s += str(filelist2.path())

                    self.message(s)
                    self.reload(filelist)
                    if filelist2 != None:
                        self.reload(filelist2)
                except shutil.SameFileError:
                    self.message(name + ': 送り先に同盟のファイルが既に存在します')
                except shutil.Error:
                    self.message(name + ': エラー')
                except Exception as e:
                    self.message(name + ': %s' % e)

    def filelist_item_size(self, item):
        acc = FolderSearch()
        count = 0
        _max = 9999
        maxover = False
    
        def f(item, first = True):
            nonlocal acc, count, _max, maxover
            if maxover:
                return
            if count == _max:
                maxover = True
                return

            count += 1

            if item.is_dir():
                a = FileList(item.path())
                if first and a.permission_error:
                    acc.permission_error = True
                for i in a:
                    f(i, False)
                if not first:
                    acc.folder_num += 1
            else:
                acc.size += item.size()
                acc.file_num += 1

        f(item)
        if maxover:
            acc.is_over = True
        return acc

    def filesize_format(self, size):
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

    def set_mode_keybind(self, filelist):
        self.input.reset()
        self.set_keybind()

        if filelist.mode == self.mode_filer_str:
            self.set_filer_keybind()
        if filelist.mode == self.mode_image_str:
            self.set_image_keybind()

    # 拡張子の画像をファイラで開けるようにする
    def set_imgext(self):
        for i in self.img_ext:
            self.ext.set(i, lambda p: self.enter_image_mode(self.current_filelist()))

    def image_load(self, filelist):
        if filelist.line_item().ext() in self.img_ext:
            self.image.image = pygame.image.load(str(filelist.line_item().path())).convert_alpha()
            self.image.look_filelist = self.opposite_filelist(filelist)
            # self.path = filelist.line_item()

            self.image_resize_aspect(filelist)

    def image_quit(self):
        self.image.__init__()

    def enter_image_mode(self, filelist):
        self.image_load(filelist)
        self.opposite_filelist(filelist).mode = self.mode_image_str
        self.sidetoggle()

    def quit_image_mode(self, filelist):
        filelist.mode = self.mode_filer_str
        self.image_quit()
        self.sidetoggle()

    def image_resize_aspect(self, filelist):
        a = self.half_screen_size()[0]
        b = self.image.image.get_rect()
        self.image.resize = pygame.transform.scale(self.image.image, (a, int(a * b[3] / b[2])))

    def image_draw(self):
        if not self.image.image:
            return

        if self.image.resize:
            a = self.image.resize
        else:
            a = self.image.image

        pos = (self.filelist_left0pos2(self.image.look_filelist.side), self.filelist_y0pos())
        self.screen.blit(a, pos)

    def set_keybind(self):
        self.input.set([K_ESCAPE],              self.quit)

    def set_filer_keybind(self):
        self.input.set([K_TAB],                 lambda: self.sidetoggle()) 
        self.input.set([K_j],                   lambda: self.down(self.current_filelist())) 
        self.input.set([K_k],                   lambda: self.up(self.current_filelist())) 
        self.input.set([K_g],                   lambda: self.top(self.current_filelist())) 
        self.input.set([K_g, 'shift'],          lambda: self.bottom(self.current_filelist())) 
        self.input.set([K_h],                   lambda: self.back(self.current_filelist())) 
        self.input.set([K_l],                   lambda: self.enter(self.current_filelist())) 
        self.input.set([K_g, 'ctrl'],           lambda: self.goto(self.current_filelist())) 
        self.input.set([K_v],                   lambda: self.open(self.current_filelist())) 
        self.input.set([K_o],                   lambda: self.sideopen()) 
        self.input.set([K_w],                   lambda: self.mkdir(self.current_filelist())) 
        self.input.set([K_r],                   lambda: self.rename(self.current_filelist())) 
        self.input.set([K_d, 'shift'],          lambda: self.duplicate(self.current_filelist())) 
        self.input.set([K_d],                   lambda: self.trash(self.current_filelist())) 
        self.input.set([K_m],                   lambda: self.move(self.current_filelist(), self.nocurrent_filelist())) 
        self.input.set([K_c],                   lambda: self.copy(self.current_filelist(), self.nocurrent_filelist())) 
        self.input.set([K_SPACE],               lambda: self.select_down(self.current_filelist())) 
        self.input.set([K_SPACE, 'shift'],      lambda: self.select_up(self.current_filelist())) 
        self.input.set([K_x],                   lambda: self.select_clear(self.current_filelist())) 
        self.input.set([K_a, 'shift'],          lambda: self.select_all(self.current_filelist())) 
        self.input.set([K_a],                   lambda: self.select_all_file(self.current_filelist())) 
        self.input.set([K_SEMICOLON],           lambda: self.linearg_command(self.current_filelist())) 
        self.input.set([K_SEMICOLON, 'shift'],  lambda: self.command()) 
        self.input.set([K_i],                   lambda: self.fileinfo_dialog(self.current_filelist())) 
        self.input.set([K_h, 'shift'],          lambda: self.screen_top(self.current_filelist())) 
        self.input.set([K_m, 'shift'],          lambda: self.screen_middle(self.current_filelist())) 
        self.input.set([K_l, 'shift'],          lambda: self.screen_bottom(self.current_filelist())) 

    def set_image_keybind(self):
        self.input.set([K_TAB],                 lambda: self.sidetoggle()) 
        self.input.set([K_j],                   lambda: self.image_down(self.current_filelist())) 
        self.input.set([K_k],                   lambda: self.image_up(self.current_filelist())) 
        self.input.set([K_h],                   lambda: self.image_back(self.current_filelist())) 

    def down(self, filelist):
        a = False

        if filelist.line + filelist.scroll < len(filelist) - 1:
            filelist.line += 1
            a = True
        
        if filelist.scroll + self.filelist_show() >= len(filelist):
            return a

        if self.filelist_show() < filelist.line + self._scrolloff() + 1:
            filelist.scroll += 1
            filelist.line -= 1
            a = True

        return a

    def up(self, filelist):
        a = False

        if filelist.line + filelist.scroll > 0:
            filelist.line -= 1
            a = True

        if filelist.scroll == 0:
            return a

        if self._scrolloff() > filelist.line:
            filelist.scroll -= 1
            filelist.line += 1
            a = True

        return a

    def top(self, filelist):
        filelist.line = 0
        filelist.scroll = 0

    def bottom(self, filelist):
        filelist.line = min(self.filelist_show() - 1, len(filelist) - 1)
        filelist.scroll = max(len(filelist) - self.filelist_show(), 0)

    def screen_top(self, filelist):
        if filelist.scroll == 0:
            filelist.line = 0
        else:
            filelist.line = self.scrolloff

    def screen_middle(self, filelist):
        filelist.line = self.filelist_show() // 2

    def screen_bottom(self, filelist):
        if filelist.scroll == len(filelist) - self.filelist_show():
            filelist.line = self.filelist_show() - 1
        else:
            filelist.line = self.filelist_show() - self.scrolloff - 1

    def back(self, filelist):
        if not filelist.path().is_root():
            a = filelist.path().name()
            filelist.chdir(filelist.path().parent())
            self.line_move(filelist, a)

    def enter(self, filelist):
        if filelist.is_empty():
            return
        if filelist.line_item().is_dir():
            filelist.chdir(str(filelist.line_item().path()))
        else:
            a = self.ext.get(filelist.line_item().ext())
            if a:
                a(filelist.line_item())

    def goto(self, filelist):
        a = util.wx_input_dialog('goto?')

        if a:
            path = Path(a)

            if path.is_exist():
                filelist.chdir(path)
            else:
                # TODO 失敗メッセージ
                pass

    def open(self, filelist):
        p = platform.system()

        if self.open_command: a = open_command
        elif  p == 'Windows': a = 'start ""'
        elif    p == 'Linux': a = 'xdg-open'
        else:                 a = 'open'

        a = a + ' "' + str(filelist.line_item().path()) + '"'
        subprocess.run(a, shell=True)

    def sidetoggle(self):
        if self.side == 'left':
            self.side = 'right'
        else:
            self.side = 'left'

        self.set_mode_keybind(self.current_filelist())

    def sideopen(self):
        self.nocurrent_filelist().chdir(self.current_filelist().path())

    def mkdir(self, filelist):
        a = util.wx_input_dialog('mkdir?')

        if a:
            f = filelist.path() / a
            self.message('mkdir: %s' % str(f))
            f.mkdir()
            # filelist.chdir(f)
            self.reload(filelist)
            self.line_move(filelist, a)

    def rename(self, filelist):
        if filelist.is_empty():
            return

        a = util.wx_input_dialog('rename?')

        if a:
            self.message('rename: %s -> %s' % (str(filelist.line_item().path()), a))
            filelist.line_item().rename(filelist.path() / a)
            filelist.chdir(filelist.path())
            self.line_move(filelist, a)

    def duplicate(self, filelist):
        if filelist.is_empty():
            return

        a = util.wx_input_dialog('duplicate?')

        if a:
            self.message('duplicate: %s -> %s' % (str(filelist.line_item().path()), a))
            n = filelist.line_item().path().name()
            shutil.copy2(filelist.line_item().path().true_str(), self.temp)
            (Path(self.temp) / n).rename(filelist.path() / a)
            self.reload(filelist)

    def trash(self, filelist):
        self.make_question_command(filelist, None, 'trash', lambda x: send2trash.send2trash(x.true_str()),
                                   '\n(LAN内ファイルは完全削除されます)')

    def move(self, filelist, filelist2):
        self.make_question_command(filelist, filelist2, 'move', lambda x, y: shutil.move(x.true_str(), y.true_str()))

    def copy(self, filelist, filelist2):
        self.make_question_command(filelist, filelist2, 'copy', lambda x, y: shutil.copy2(x.true_str(), y.true_str()))

    def select(self, filelist):
        if filelist.is_empty():
            return

        a = filelist.line_item()

        if a.name() in filelist.select:
            filelist.select.remove(a.name())
        else:
            filelist.select.append(a.name())

    def select_down(self, filelist):
        self.select(filelist)
        self.down(filelist)

    def select_up(self, filelist):
        self.select(filelist)
        self.up(filelist)

    def select_clear(self, filelist):
        filelist.select = []

    def select_all(self, filelist):
        filelist.select = [i.name() for i in filelist.get_all()]

    def select_all_file(self, filelist):
        filelist.select = [i.name() for i in filelist.get_all() if not i.is_dir()]

    def command(self):
        a = util.wx_input_dialog('command?')
        if a:
            s = subprocess.run('%s %s' % (self.shell, a), capture_output=True)
            self.message(s.stdout)

    def linearg_command(self, filelist):
        a = util.wx_input_dialog('linearg_command?')
        if a:
            s = subprocess.run('%s %s %s' % (self.shell, a, filelist.line_item().path()), capture_output=True)
            self.message(s.stdout)

    def fileinfo_toggle(self, filelist):
        filelist.fileinfo_flag = not filelist.fileinfo_flag

    def fileinfo(self, filelist):
        for i in self.fileinfo_list(filelist):
            self.message(i)

    def fileinfo_dialog(self, filelist):
        self.question_dialog('\n'.join(self.fileinfo_list(filelist)))

    def image_down(self, filelist):
        if self.down(self.opposite_filelist(filelist)):
            self.image_load(self.opposite_filelist(filelist))

    def image_up(self, filelist):
        if self.up(self.opposite_filelist(filelist)):
            self.image_load(self.opposite_filelist(filelist))

    def image_back(self, filelist):
        self.quit_image_mode(filelist)

a = Main()

a.main()
