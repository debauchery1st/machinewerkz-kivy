from os import getcwd, path, listdir
from random import randint, shuffle
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.button import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.config import Config
from kivy.clock import Clock, mainthread
from kivy.properties import StringProperty, BooleanProperty
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

from audio import load_audio, music_list, fx_dict
from game import Borg, Picard, LEFT, RIGHT

Config.set('kivy', 'exit_on_escape', '0')

FX = fx_dict(path.join(getcwd(), 'data/audio/fx'))
PLAYLIST = music_list(path.join(getcwd(), 'data/audio/music'))

SU = 50
COLS = 10
ROWS = 18
SCREEN_WIDTH = SU * COLS
SCREEN_HEIGHT = SU * ROWS
DELAY = 50


shuffle(PLAYLIST)

__version__ = "0.4.3"

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


class PuzzleGame(Widget):
    tock = 0
    last_state = None
    event = None

    def __init__(self, **kwargs):
        super(PuzzleGame, self).__init__(**kwargs)
        app = App.get_running_app()
        self.piece = app.piece
        self.board = app.game_board
        self.set_interval(app.fall_speed)

    def set_interval(self, speed):
        if self.event is not None:
            self.event.cancel()
        self.event = Clock.schedule_interval(self.tick, speed)

    def tick(self, *args):
        self.tock += 1
        if self.piece.game_on:
            self.piece.fall()
        self.next_state()

    @mainthread
    def draw_method(self, grid, *args, **kwargs):
        # "set" changed tiles
        app = App.get_running_app()
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                app.widget_grid[y][x].LIT = [False, True][int(grid[y][x])]
        return grid

    @mainthread
    def next_state(self):
        app = App.get_running_app()
        ok, msg = self.piece.cb_draw(cb=self.draw_method, acb=app.audio_callback)
        if not ok:
            self.piece.swap_grid()
            self.piece.shape_shift()
            self.piece.reset()
            app.current_score = self.piece.text_score[0]
            # check if
            return True
        try:
            for y in range(len(self.piece.board.grid)):
                for x in range(len(self.piece.board.grid[0])):
                    app.widget_grid[y][x].LIT = [False, True][int(self.piece.board.grid[y][x])]
        except Exception as e:
            raise e


class TileWidget(ButtonBehavior, Image):
    grid_id = StringProperty()
    grid_pos = (0, 0)
    CURRENT = StringProperty()
    LIT_IMG = StringProperty("data/img/steampunk.png")
    DARK_IMG = StringProperty("data/img/empty.png")
    LIT = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(TileWidget, self).__init__(**kwargs)

    def pressed_(self, *args, **kwargs):
        app = App.get_running_app()
        app.modify(self.grid_pos)


class GameGridLayout(GridLayout):
    cols = COLS
    rows = ROWS

    def __init__(self, **kwargs):
        super(GameGridLayout, self).__init__(**kwargs)
        app = App.get_running_app()
        game_board = Borg(cols=COLS, rows=ROWS, square_unit=SU)
        app.widget_grid = []
        # point <--> widget
        for y in range(game_board.rows):
            app.widget_grid.append([])
            for x in range(game_board.cols):
                t = TileWidget()
                t.grid_id = "x{}y{}".format(str(y), str(x))
                t.grid_pos = (x, y)
                self.add_widget(t)
                app.widget_grid[y].append(t)
        app.game_board = game_board
        piece = Picard(square_unit=SU, shape=randint(0, 6), state=True,
                       board=app.game_board, restart_callback=app.widget_reset)
        app.piece = piece
        app.game_engine = PuzzleGame()
        app.widget_grid = app.widget_grid


class MachineWerkz(App):
    lit = list()
    game_board, piece, game_engine = None, None, None
    widget_grid = None
    fall_speed = 0.7
    current_score = StringProperty('machine werkz')
    current_song = None
    music_state = True
    music_location = 'default'
    music_playlist = []
    music_played = []
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
        if self.music_state:
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
                raise e
            return "MUSIC OFF"
        # music for menus
        if self.__manager is not None and (self.__manager.current not in ['game']):
            s = FX['intro']
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
        for y in range(len(self.game_board.grid)):
            for x in range(len(self.game_board.grid[0])):
                self.widget_grid[y][x].LIT = [False, True][int(self.game_board.grid[y][x])]
        self.current_score = 'machine werkz'

    def change_speed(self, t):
        try:
            res = {
                'Rolling/Packing': ('play whilst otherwise occupied', 0.7),
                'Smoking/Vaping': ('play while one hand is occupied', 0.6),
                'Chilling': ('just chilling', 0.5),
                'L': ('good luck', 0.3)
            }[t]
            if res[1] != self.fall_speed:
                # change speed
                self.fall_speed = res[1]
                self.game_engine.set_interval(self.fall_speed)
        except KeyError:
            return ""
        return "{}".format(res[0])

    def on_stop(self):
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
