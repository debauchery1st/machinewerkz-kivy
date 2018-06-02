from os import getcwd, path, listdir
from time import time
from random import randint, shuffle
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics.vertex_instructions import Rectangle
from kivy.config import Config
from kivy.clock import Clock, mainthread
from kivy.properties import StringProperty
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

from audio import load_audio, music_list, fx_dict
from game import PuzzlePiece, GameBoard, LEFT, RIGHT

Config.set('kivy', 'exit_on_escape', '0')


# this will all be in the config file. ignore the broad exception for now.
try:
    FX = fx_dict(path.join(getcwd(), 'data/audio/fx'))
except Exception as e:
    FX = {}

try:
    PLAYLIST = music_list(path.join(getcwd(), 'data/audio/music'))
except Exception as e:
    PLAYLIST = []

SU = 50
COLS = 10
ROWS = 18
SCREEN_WIDTH = SU * COLS
SCREEN_HEIGHT = SU * ROWS
DELAY = 50


shuffle(PLAYLIST)

__version__ = "0.5.0"

# for debugging on desktop, set window size
if platform in ['linux', 'windows', 'macosx']:
    from kivy.core.window import Window
    Window.size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    Config.window_icon = path.join(getcwd(), 'data/img/steampunk.png')

Config.set('graphics', 'resizable', '0')


class FileBox(BoxLayout):
    pass


class FileBrowserScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class MenuScreen(Screen):
    pass


class GameScreen(Screen):
    pass


class SettingsMenu(BoxLayout):
    pass


class MainMenu(BoxLayout):
    pass


class BoundingBox(BoxLayout):
    pass


class PuzzleGameWidget(Widget):
    tock = 0
    last_state = None
    event = None
    LIT_IMG = StringProperty("data/img/steampunk.png")
    DARK_IMG = StringProperty("data/img/empty.png")
    texture = Image(source="data/img/steampunk.png").texture
    piece_group = None
    last_t = 0
    test_event = None

    def __init__(self, **kwargs):
        super(PuzzleGameWidget, self).__init__(**kwargs)
        app = App.get_running_app()
        self.piece = app.piece
        self.board = app.game_board
        self.piece_group = InstructionGroup()
        self.canvas.add(self.piece_group)
        Clock.schedule_interval(self.next_state, .1)

    def on_touch_down(self, touch):
        app = App.get_running_app()
        su = get_square_unit(COLS)
        _x, _y = touch.pos
        x, y = _x/su, _y/su
        app.modify_state([int(x), int(y)])

    @mainthread
    def draw_method(self, grid):
        # update InstructionGroup() for widget canvas
        self.piece_group.clear()
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                lit = [False, True][int(grid[y][x])]
                if lit:
                    rx = x * self.board.square_unit
                    ry = Window.height - y * self.board.square_unit
                    self.piece_group.add(
                        Rectangle(texture=self.texture, pos=(rx, ry),
                                  size=[self.board.square_unit, self.board.square_unit])
                    )
        return grid

    @mainthread
    def next_state(self, dt):
        app = App.get_running_app()
        ok, msg = self.piece.cb_draw(cb=self.draw_method, acb=app.audio_callback)
        if not ok:
            self.piece.swap_grid()
            self.piece.shape_shift()
            self.piece.reset()
            app.current_score = self.piece.text_score[0]
            # check if
            return True
        elapsed = time() - self.last_t
        if elapsed >= app.fall_speed and self.piece.game_on:
            self.piece.fall()
            self.last_t = time()


def screen_grid(rows, cols):
    res = []
    u = Window.size[0] / float(cols)
    for y in range(rows):
        res.append([])
        for _ in range(cols):
            res[y].append([u*_, Window.size[1] - u*y])
    return res


def get_square_unit(cols):
    return Window.size[0] / float(cols)


class GameBoardLayout(BoxLayout):
    cols = COLS
    rows = ROWS
    screen_su = None

    def __init__(self, **kwargs):
        super(GameBoardLayout, self).__init__(**kwargs)
        app = App.get_running_app()
        game_board = GameBoard(cols=COLS, rows=ROWS, square_unit=get_square_unit(COLS))
        app.game_board = game_board
        self.screen_su = get_square_unit(self.cols)
        app.widget_grid = screen_grid(self.rows, self.cols)
        piece = PuzzlePiece(square_unit=SU, shape=randint(0, 6), state=True,
                       board=app.game_board, restart_callback=app.widget_reset)
        app.piece = piece
        app.game_engine = PuzzleGameWidget()


class MachineWerkz(App):
    lit = list()
    game_board, piece, game_engine = None, None, None
    widget_grid = None
    fall_speed = .9
    current_score = StringProperty('machine werkz')
    current_song = None
    music_state = True
    music_location = 'default'
    music_playlist = []
    music_played = []
    event = None
    spinner = None
    __manager = None
    __knock = 0

    def build(self, **kwargs):
        self.bind(on_start=self.init_device)
        self.music_playlist = [str(_) for _ in PLAYLIST]
        self.__manager = ScreenManager()
        self.__manager.add_widget(MenuScreen(name='menu'))
        self.__manager.add_widget(GameScreen(name='game'))
        self.__manager.add_widget(SettingsScreen(name='settings'))
        self.__manager.add_widget(FileBrowserScreen(name='file_box'))
        self.play_music()
        return self.__manager

    def init_device(self, *args):
        self.piece.pause()
        Window.bind(on_keyboard=self.on_kb)

    def on_kb(self, window, key1, key2, txt, modifiers):
        if key1 == 27 or key1 == 1001:
            self.__knock += 1
            if self.__knock > 2:
                return self.stop()
            return self.change_screen('menu')

    def audio_callback(self, audio_type, audio_name, extra=None):
        # print('Audio Callback: ', audio_type, audio_name, extra)
        if audio_type in ['fx', 'FX']:
            try:
                _ = load_audio(FX[audio_name])
                _.play()
                del _
            except KeyError:
                pass

    def toggle_music(self):
        self.music_state = not self.music_state
        self.play_music()

    def play_music(self):
        if not self.music_state:
            try:
                self.current_song.stop()
            except TypeError:
                pass
            except AttributeError as e:
                if 'NoneType' in e:
                    pass
                raise e
            return "MUSIC OFF"
        # music for menus
        if self.__manager is not None and (self.__manager.current not in ['game']):
            try:
                s = FX['intro']
            except KeyError:
                return
        else:
            try:
                s = self.music_playlist.pop()
            except IndexError as e:
                self.music_playlist = [str(_) for _ in self.music_played]
                del self.music_played[:]
                s = self.music_playlist.pop()
        self.current_song = load_audio(s)
        self.music_played.append(str(s))
        self.current_song.play()

    def refresh_display(self):
        if self.current_song is not None:
            if self.current_song.state == 'stop':
                self.play_music()
        self.piece.cb_draw(cb=self.game_engine.draw_method, acb=self.audio_callback)

    def modify_state(self, pos, *kwargs):
        if 11 > pos[0] > 6:
            self.piece.move(RIGHT)
            self.refresh_display()
            self.audio_callback(audio_type='fx', audio_name='tick')
        elif -1 < pos[0] < 4:
            self.piece.move(LEFT)
            self.refresh_display()
            self.audio_callback(audio_type='fx', audio_name='tick')
        elif 3 < pos[0] < 7:
            self.piece.rotate()
            self.refresh_display()
            self.audio_callback(audio_type='fx', audio_name='rotate')
        else:
            pass

    def change_screen(self, name, angle="right"):
        self.__manager.transition.direction = angle
        last = str(self.__manager.current)
        try:
            self.__manager.current = name
        except Exception as e:
            self.__manager.current = last
        if last == 'settings':
            return True
        if last != name and name in ['menu', 'game']:
            self.piece.pause()
            if self.music_state:
                if self.current_song:
                    self.current_song.stop()
                    self.play_music()
            self.__knock = 0
        return True

    def widget_reset(self):
        self.game_board.reset()
        self.current_score = 'machine werkz'
        self.piece.pause()

    def change_speed(self, t):
        try:
            res = {
                'Rolling/Packing': ('play whilst otherwise occupied', 0.9),
                'Smoking/Vaping': ('play while one hand is occupied', 0.8),
                'Chilling': ('just chilling', 0.7),
                'L': ('good luck', 0.3)
            }[t]
            self.fall_speed = res[1]
        except KeyError:
            return ""
        return "{}".format(res[0])

    def on_stop(self):
        if self.current_song:
            try:
                print('stopping music')
                self.current_song.stop()
            except TypeError as e:
                print('TYPE ERROR: ', e)

    def file_select(self, selection, p):
        available = []
        if len(selection) > 0:
            print("Selected : {}".format(selection))
            for _ in selection:
                if _[-4:] in ['.mp3', '.ogg']:
                    available.append(path.join(p, _))
        else:
            for _ in listdir(p):
                if _[-4:] in ['.mp3', '.ogg']:
                    available.append(path.join(p, _))
        if len(available) > 0:
            try:
                print('stopping music')
                self.current_song.stop()
            except TypeError as e:
                print('TYPE ERROR: ', e)
            self.music_state = False
            self.music_playlist = available
            self.music_played = [PLAYLIST]
            try:
                self.toggle_music()
            except TypeError:
                pass
            return True
        return False

    def reset_music(self):
        try:
            print('stopping music')
            self.current_song.stop()
        except TypeError as e:
            print('TYPE ERROR: ', e)
        self.music_playlist = [str(_) for _ in PLAYLIST]
        shuffle(self.music_playlist)
        if not self.music_state:
            self.toggle_music()


if __name__ == "__main__":
    MachineWerkz().run()
