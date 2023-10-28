
### だいなファイラのパクリ

### 重要な関数リスト
# set_keybind
# current_filelist().line_item()
# display_filer 描写


# テキストビュワー執筆中 やる気がわかない

# Win+d2回押したあとに操作するとエラー音がうるさい

# 半透明できないかなあ ウインドウの縁を巻き込みたくないが難しそう

# 権限がないフォルダにアクセスすると落ちる

# シンボリックリンクなどの挙動

# 内蔵ビュワー gifを開くと落ちる




################################################################################

# 標準
import os, sys, subprocess, shutil

# 外部ライブラリ
import pygame, wx, send2trash
from pygame.locals import *

#
import util

class Syl:

    def set_keybind(self):
        self.always_input.set([K_ESCAPE],              self.quit)

        self.normal_input.set([K_TAB],                 lambda: self.sidetoggle())
        self.normal_input.set([K_j],                   lambda: self.down(self.current_filelist()))
        self.normal_input.set([K_k],                   lambda: self.up(self.current_filelist()))
        self.normal_input.set([K_g],                   lambda: self.top(self.current_filelist()))
        self.normal_input.set([K_g, 'shift'],          lambda: self.bottom(self.current_filelist()))
        self.normal_input.set([K_h],                   lambda: self.back(self.current_filelist()))
        self.normal_input.set([K_l],                   lambda: self.enter(self.current_filelist()))
        self.normal_input.set([K_g, 'ctrl'],           lambda: self.goto(self.current_filelist()))
        self.normal_input.set([K_v],                   lambda: self.open(self.current_filelist()))
        self.normal_input.set([K_o],                   lambda: self.sideopen())
        self.normal_input.set([K_w],                   lambda: self.mkdir(self.current_filelist()))
        self.normal_input.set([K_r],                   lambda: self.rename(self.current_filelist()))
        self.normal_input.set([K_d, 'shift'],          lambda: self.duplicate(self.current_filelist()))
        self.normal_input.set([K_d],                   lambda: self.trash(self.current_filelist()))
        self.normal_input.set([K_m],                   lambda: self.move(self.current_filelist(), self.nocurrent_filelist()))
        self.normal_input.set([K_c],                   lambda: self.copy(self.current_filelist(), self.nocurrent_filelist()))
        self.normal_input.set([K_SPACE],               lambda: self.select_down(self.current_filelist()))
        self.normal_input.set([K_SPACE, 'shift'],      lambda: self.select_up(self.current_filelist()))
        self.normal_input.set([K_x],                   lambda: self.select_clear(self.current_filelist()))
        self.normal_input.set([K_a, 'shift'],          lambda: self.select_all(self.current_filelist()))
        self.normal_input.set([K_a],                   lambda: self.select_all_file(self.current_filelist()))
        self.normal_input.set([K_SEMICOLON],           lambda: self.linearg_command(self.current_filelist()))
        self.normal_input.set([K_SEMICOLON, 'shift'],  lambda: self.command())
        self.normal_input.set([K_i],                   lambda: self.fileinfo_dialog(self.current_filelist()))
        self.normal_input.set([K_h, 'shift'],          lambda: self.screen_top(self.current_filelist()))
        self.normal_input.set([K_m, 'shift'],          lambda: self.screen_middle(self.current_filelist()))
        self.normal_input.set([K_l, 'shift'],          lambda: self.screen_bottom(self.current_filelist()))

        # self.image_input.set([K_j],                    lambda: self.image_down(self.current_filelist()))
        # self.image_input.set([K_k],                    lambda: self.image_up(self.current_filelist()))
        self.image_input.set([K_h],                    lambda: self.image_back())

        self.textview_input.set([K_h],                 lambda: self.textview_back())

    # 事前にいじれる変数 オプション
    def __init__(self):

        self.color_bg     = (0,0,0)
        self.color_fg     = (255,255,255)
        self.color_folder = (0,255,255)
        self.color_line   = (255,255,255)
        self.color_mark   = (0,0,255)
        self.color_path   = (0,255,0)
        self.color_info   = (0,255,0)
        self.color_frame  = (255,255,255)
        self.color_stbar  = (240,240,240) # ステータスバー

        self.debug = True
        self.scrolloff = 5
        self.font_name = 'C:/Windows/Fonts/msgothic.ttc'
        self.font_size = 12
        self.open_command = None
        self.temp = os.environ['TEMP']
        self.shell = 'nyagos -c'

        # イメージビューワを使うかどうか
        self.flag_img_mode = True

        # イメージビューワの拡張子
        self.img_ext = ['bmp', 'png', 'jpg', 'jpeg', 'gif']

        # テキストビューワを使うかどうか
        self.flag_txt_mode = True

        # テキストビューワの拡張子
        self.txt_ext = ['txt', 'ini', 'html', 'htm']

        self.init_path = '~/Desktop'
        self.message_show = 4

        self.mode_normal_str = 'NORMAL'
        self.mode_image_str = 'IMAGE'
        self.mode_textview_str = 'TEXTVIEW'

        self.upinfo_show = 2 # ファイルリスト上の情報の行数
        self.downinfo_show = 1

    # メイン
    def main(self):

        pygame.init()
        self.mode = self.mode_normal_str
        self.screen = pygame.display.set_mode((600, 400), RESIZABLE)
        pygame.key.set_repeat(500, 35)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(self.font_name, self.font_size)
        self.wx_app = wx.App()
        self.always_input = util.Input()
        self.normal_input = util.Input()
        self.image_input = util.Input()
        self.textview_input = util.Input()
        self.ext = util.ExtCommand()
        self.ext_do_init()
        self.set_keybind()
        self.input = self.always_input + self.normal_input
        self.history = util.History()
        self.left_filelist = util.FilerFileList(side = 'left', history = self.history)
        self.right_filelist = util.FilerFileList(side = 'right', history = self.history)
        self.side = 'left'

        if self.init_path:
            self.left_filelist.chdir(self.init_path)

        while 1:
            self.fill(self.color_bg)

            self.display_filer()

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit()

                if event.type == KEYDOWN:
                    self.input.get(event)

                    # ここで時間がかかるイベント中に入力されたキーイベントを枯らす
                    pygame.event.get()

            # これがないとCPUが暴走する
            self.clock.tick(60)

    # 拡張子に応じてなんらかのアクションを取る機能のinit
    def ext_do_init(self):
        if self.flag_img_mode:
            for i in self.img_ext:
                self.ext.set(i, self.image_mode)

        if self.flag_txt_mode:
            for i in self.txt_ext:
                self.ext.set(i, self.textview_mode)




################################################################################
# ここまで更新される可能性が高いもの
################################################################################






    # 終了するときに起動するやつ
    def quit(self):
        pygame.quit()
        sys.exit()

    # ウインドウサイズを取得
    def screen_size(self):
        return pygame.display.get_surface().get_size()

    # ウインドウサイズの半分
    def half_screen_size(self):
        return self.screen_size()[0] // 2, self.screen_size()[1] // 2

    # フォントサイズ取得 横用に半分に
    def _font_size(self):
        return self.font_size // 2, self.font_size

    # 画面の文字の表示件数
    def char_show(self):
        return self.screen_size()[0] // self._font_size()[0], \
               self.screen_size()[1] // self.font_size

    # ファイルリストの画面の表示件数
    def filelist_show(self):
        return self.char_show()[1] - self.upinfo_show - self.downinfo_show - self.message_show

    # ファイルリスト横の画面の表示文字数
    def filelist_x_show(self):
        return self.half_screen_size()[0] // self._font_size()[0]

    # ウィンドウに文字を表示する
    def echo(self, color, pos, s):
        text = self.font.render(s, True, color)
        self.screen.blit(text, pos)

    # ウィンドウをその色に染める 画面初期化に使う
    def fill(self, color):
        self.screen.fill(color)

    # 中身を塗りつぶした四角を表示する
    def square(self, color, pos, size):
        pygame.draw.rect(self.screen, color, pos + size)

    # 線を表示する
    def line(self, color, fr, to, depth = 1):
        pygame.draw.line(self.screen, color, fr, to, depth)

    # ファイルリストを表示する
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

    # ファイルリストのxが0の位置
    def filelist_left0pos(self, side):
        if side == 'left':
            return 0
        else:
            return self.half_screen_size()[0] + 1

    # ファイルリストのラインの位置
    def filelist_linepos(self, i):
        return self.font_size * (i + self.upinfo_show)

    # ファイルリストのyが0の位置
    # + 1 は後付でとりあえず入れておいたがどうだろうか
    def filelist_y0pos(self):
        return self.font_size * self.upinfo_show + 1

    # ファイルリストのyの最後+1の位置 要するに線の位置
    def filelist_yepos(self):
        return self.screen_size()[1] - self.font_size * (self.downinfo_show + self.message_show)

    # 画面上の行の位置 下から
    def display_ycharpos_end(self, i):
        return self.screen_size()[1] - self.font_size * i

    # ファイルリストのラインを表示する
    def display_filelist_line(self, filelist):
        p = self.filelist_left0pos(filelist.side)
        y = filelist.line + self.upinfo_show + 1

        self.line(self.color_line,
                  (p, self.font_size * y),
                  (p + self.half_screen_size()[0], self.font_size * y))

    # ファイルリストの選択を表示する 四角
    def echo_select(self, filelist):
        for i in range(self.filelist_show()):
            n = filelist.displayed_item(i)
            if not n:
                return
            elif n.name() in filelist.select:
                self.square(self.color_mark,
                            (self.filelist_left0pos(filelist.side), self.filelist_linepos(i)),
                            (self.half_screen_size()[0], self.font_size))

    # アクティブな方のファイルリストを返す
    def current_filelist(self):
        if self.side == 'left':
            return self.left_filelist
        else:
            return self.right_filelist

    # アクティブでない方のファイルリストを返す
    def nocurrent_filelist(self):
        if self.side == 'left':
            return self.right_filelist
        else:
            return self.left_filelist

    # 引数のファイルリストでない方のファイルリストを返す
    # これ多分いらないんじゃないかと思う
    def opposite_filelist(self, filelist):
        if filelist.side == 'left':
            return self.right_filelist
        else:
            return self.left_filelist

    # ファイラ画面の描写
    # 条件分岐とかしてデカくなるか あるいは他に関数を作るのかは今のところわからない
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

        d = self.font_size * (self.downinfo_show + self.message_show)

        # 中央縦線
        self.line(self.color_frame,
                  (self.half_screen_size()[0], 0), (self.half_screen_size()[0], self.screen_size()[1] - d))
        self.line(self.color_frame,
                  (0, self._font_size()[1] * 2), (self.screen_size()[0], self._font_size()[1] * 2))
        # ファイルリスト下線
        self.line(self.color_frame,
                  (0, self.screen_size()[1] - d), (self.screen_size()[0], self.screen_size()[1] - d))
        # メッセージ下線
        self.square(self.color_stbar,
                    (0, self.screen_size()[1] - self.font_size * self.downinfo_show),
                    (self.screen_size()[0], self.screen_size()[1]))
        # 最下インフォ ファイル名
        if not self.current_filelist().is_empty():
            self.echo(self.color_bg,
                      (0, self.screen_size()[1] - self.font_size), self.current_filelist().line_item().name())

        self.echo_select(self.right_filelist)
        self.echo_filelist(self.right_filelist)
        self.display_filelist_line(self.current_filelist())

        if self.left_filelist.fileinfo_flag:
            self.display_fileinfo(self.left_filelist, self.right_filelist)
        if self.right_filelist.fileinfo_flag:
            self.display_fileinfo(self.right_filelist, self.left_filelist)

        if self.mode == self.mode_image_str:
            self.image_view()

        if self.mode == self.mode_textview_str:
            self.textview_view()

    # 非アクティブのファイルリストがあるところにファイル情報を表示するらしい
    # 下のと被ってるし いらないんじゃないか
    def display_fileinfo(self, filelist_info, filelist_view):
        if filelist_info.is_empty():
            return
        x0 = self.filelist_left0pos(filelist_view.side) + 1
        y0 = self.font_size * 2 + 1

        self.square(self.color_bg, (x0, y0), (self.half_screen_size()[0], self.font_size * self.filelist_show()))

        self.echo(self.color_fg, (x0, y0), filelist_info.line_item().name())
        self.echo(self.color_fg, (x0, y0 + self.font_size), '場所: %s' % str(filelist_info.line_item().path().parent()))

        size = self.filelist_item_size(filelist_info.line_item())

        if size:
            size_format = util.filesize_format(size)
        else:
            size_format = '不明'

        self.echo(self.color_fg, (x0, y0 + self.font_size * 2), 'サイズ: %s' % size_format)

    # ファイル情報のリストらしい
    def fileinfo_list(self, filelist):
        lst = []
        lst.append('名前: %s' % filelist.line_item().name())
        lst.append('場所: %s' % str(filelist.line_item().path().parent()))

        searched = self.filelist_item_size(filelist.line_item())

        if searched.is_over:
            size_format = '不明'
        else:
            size_format = util.filesize_format(searched.size)

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

    # 該当のファイルリストを再読み込みする
    def reload(self, filelist):
        p = not filelist.is_empty()
        if p:
            a = filelist.line_item().name()
        filelist.chdir(filelist.path())
        if p:
            self.line_move(filelist, a)

    # 仮置き
    # 画面上に表示のほか ファイル出力も考えてる
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
                    self.message(name + ': 送り先に同名のファイルが既に存在します')
                except shutil.Error:
                    self.message(name + ': エラー')
                except Exception as e:
                    self.message(name + ': %s' % e)

    # よくわからない ファイルサイズを図るやつだろうが
    def filelist_item_size(self, item):
        acc = util.FolderSearch()
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
                a = util.FileList(item.path())
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

    # ファイル操作のキーバインドを設定
    def set_normal_keybind(self):
        self.input = self.always_input + self.normal_input

    # 画像ビューワのキーバインドを設定
    def set_image_keybind(self):
        self.input = self.always_input + self.image_input

    def set_textview_keybind(self):
        self.input = self.always_input + self.textview_input

    # up downで使うやつ
    def _scrolloff(self):
        return min(self.scrolloff, self.filelist_show() // 2)

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
                a()

    def goto(self, filelist):
        a = util.wx_input_dialog('goto?')

        if a:
            path = util.Path(a)

            if path.is_exist():
                filelist.chdir(path)
            else:
                # TODO 失敗メッセージ
                self.message('goto: Directory Not Found')

    # ファイルリストの該当のファイルを開く
    def open(self, filelist):
        if self.open_command:   a = open_command
        elif util.is_windows(): a = 'start ""'
        elif util.is_linux():   a = 'xdg-open'
        else:                   a = 'open'

        a = a + ' "' + str(filelist.line_item().path()) + '"'
        subprocess.run(a, shell=True)

    def sidetoggle(self):
        if self.side == 'left':
            self.side = 'right'
        else:
            self.side = 'left'

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
            (util.Path(self.temp) / n).rename(filelist.path() / a)
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
        util.wx_question_dialog('\n'.join(self.fileinfo_list(filelist)))

    # 画像読み込み
    def image_load(self, path):
        self.pygame_image = pygame.image.load(path)

    def image_size(self):
        return self.pygame_image.get_rect().size

    # 画像領域のサイズ
    def image_zone_size(self):
        return self.half_screen_size()[0], self.filelist_yepos()

    # 画像領域の0の位置
    def image_zone_0pos(self):
        return self.filelist_left0pos(self.nocurrent_filelist().side), 0

    # 画像表示
    def image_view(self):
        self.square(self.color_bg, self.image_zone_0pos(), self.image_zone_size())
        self.screen.blit(self.pygame_image, self.image_pos)

    # 画像モードに移行
    def image_mode(self):
        if self.debug:
            self.message('debug: image mode on')

        self.mode = self.mode_image_str
        self.set_image_keybind()
        self.image_load(str(self.current_filelist().line_item().path()))

        a = self.image_size()
        b = self.image_zone_size()
        x0 = self.filelist_left0pos(self.nocurrent_filelist().side)
        x1 = self.screen_size()[0] // 4
        y1 = self.filelist_yepos() // 2

        # 画像が画像領域サイズより小さいか同じ場合
        if a[0] <= b[0] and a[1] <= b[1]:
            pass
        # 大きい場合はリサイズする
        else:
            # 画像 横のほうが大きい場合
            if self.image_size()[0] >= self.image_size()[1]:
                r = self.image_zone_size()[0] / self.image_size()[0]
            else:
                r = self.image_zone_size()[1] / self.image_size()[1]

            new = self.image_size()[0] * r, self.image_size()[1] * r

            self.pygame_image = pygame.transform.smoothscale(self.pygame_image, new) 

        x2 = self.image_size()[0] // 2
        y2 = self.image_size()[1] // 2

        self.image_pos = x0 + x1 - x2, y1 - y2

    # 画像モードから抜ける
    def image_back(self):
        self.mode = self.mode_normal_str
        self.set_normal_keybind()
        if self.debug:
            self.message('debug: image mode off')

    # テキストビュワーに入る
    def textview_mode(self):
        if self.debug:
            self.message('debug: textview mode on')

        self.mode = self.mode_textview_str
        self.set_textview_keybind()

        self.textview_path = self.current_filelist().line_item().path()
        self.textview_charcode = util.charcode(str(self.textview_path))
        with open(str(self.textview_path), encoding = self.textview_charcode) as f:
            self.textview_text = f.readlines()
        self.textview_line = 0
        self.textview_num = len(self.textview_text)

    # テキストビュワーから抜ける
    def textview_back(self):
        self.mode = self.mode_normal_str
        self.set_normal_keybind()
        if self.debug:
            self.message('debug: textview mode off')

    # テキストビュワー テキスト部の表示行数
    def textview_mainshow(self):
        return self.charshow()[1] - 1

    def textview_view(self):
        self.fill(self.color_bg)
        self.square(self.color_stbar, 
                    (0, self.screen_size()[1] - self.font_size),
                    (self.screen_size()[0], self.font_size))

if __name__ == '__main__':
    a = Syl()
    a.main()
