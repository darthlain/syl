    def command_trash(self, filelist):
        if filelist.is_empty():
            return

        a = self.question_dialog('trash?\n(LAN内ファイルは完全削除されます)')

        if a:
            self.message('trash: %s' % str(filelist.line_item().path()))
            send2trash.send2trash(str(filelist.line_item().path().true_str()))
            filelist.chdir(filelist.path())

    def command_move(self, filelist, filelist2):
        if filelist.is_empty():
            return

        a = self.question_dialog('move?')

        if a:
            try:
                self.message('move: %s -> %s' % (filelist.line_item().path(), filelist2.path()))
                shutil.move(filelist.line_item().path().true_str(), filelist2.path().true_str())
                self.reload(filelist)
                self.reload(filelist2)
            except Exception as e:
                self.message(e.args)

    def command_copy(self, filelist, filelist2):
        if filelist.is_empty():
            return

        a = self.question_dialog('copy?')

        if a:
            if not filelist.select:
                try:
                    self.message('copy: %s -> %s' % (filelist.line_item().path(), filelist2.path()))
                    shutil.copy2(filelist.line_item().path().true_str(), filelist2.path().true_str())
                    self.reload(filelist)
                    self.reload(filelist2)
                except Exception as e:
                    self.message(e.args)
