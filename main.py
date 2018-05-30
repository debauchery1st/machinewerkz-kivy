from os import getcwd, path, listdir
from random import randint, shuffle

from kivy.app import App
from kivy.lang import Builder
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

from audio import load_audio
from game import Borg, Picard, LEFT, RIGHT

Config.set('kivy', 'exit_on_escape', '0')

SU = 50
COLS = 10
ROWS = 18
SCREEN_WIDTH = SU * COLS
SCREEN_HEIGHT = SU * ROWS
DELAY = 50

PLAYLIST = ['data/audio/{}'.format(_) for _ in listdir('data/audio') if _.endswith('.mp3') or _.endswith('.ogg')]
shuffle(PLAYLIST)

__version__ = "0.3.3"


# for debugging on desktop, set window size
if platform in ['linux', 'windows', 'macosx']:
    from kivy.core.window import Window
    Window.size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    Config.window_icon = path.join(getcwd(), 'data/img/steampunk.png')

Config.set('graphics', 'resizable', '0')

Builder.load_string("""

<TileWidget>
    source: self.LIT_IMG if self.LIT else self.DARK_IMG
    allow_stretch: True
    keep_ratio: False
    on_press:
        app.modify_state(self.grid_pos)


<MainMenu>
    orientation: "vertical"
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: "data/img/background.png"
    Label:
        font_name: 'data/fonts/Playfair_Display/PlayfairDisplay-Regular.ttf'
        text: "machine werkz"
        size_hint_y: .03
    Button:
        background_color: 0, 0, 0, 0
        font_name: 'data/fonts/Playfair_Display/PlayfairDisplay-Regular.ttf'
        font_size: '30sp'
        text: "PLAY"
        size_hint_y: .71
        on_press: app.change_screen('game')
    Button:
        background_color: 0, 0, 0, 0
        font_name: 'data/fonts/Playfair_Display/PlayfairDisplay-Regular.ttf'
        font_size: '15sp'
        text: "SETTINGS"
        size_hint_y: .20
        on_press: app.change_screen('settings')
    Label:
        size_hint_y: .03
    Label:
        size_hint_y: .03

<GameGridLayout>


<BoundingBox>:
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: "data/img/background.png"
    orientation: "vertical"
    Label:
        font_name: 'data/fonts/Playfair_Display/PlayfairDisplay-Regular.ttf'
        font_size: '18sp'
        text: app.current_score
        size_hint_y: .03
    GameGridLayout:
        size_hint_y: .97


<GameScreen>:
    BoundingBox:

<MenuScreen>:
    MainMenu:


<SettingsScreen>:
    BoxLayout:
        orientation: "vertical"
        Button:
            text: 'My settings button'
        Button:
            text: 'Back to menu'
            on_press: app.change_screen('menu')
""")


class MenuScreen(Screen):
    pass


class GameScreen(Screen):
    pass


class MainMenu(BoxLayout):
    pass


class BoundingBox(BoxLayout):
    pass


class PuzzleGame(Widget):
    tock = 0
    last_state = None

    def __init__(self, **kwargs):
        super(PuzzleGame, self).__init__(**kwargs)
        app = App.get_running_app()
        Clock.schedule_interval(self.tick, app.fall_speed)
        app = App.get_running_app()
        self.piece = app.piece
        self.board = app.game_board

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
        ok, msg = self.piece.cb_draw(cb=self.draw_method)
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
    music_playlist = []
    music_played = []
    __manager = None
    __knock = 0

    def build(self, **kwargs):
        self.bind(on_start=self.init_device)
        self.music_playlist = [str(_) for _ in PLAYLIST]
        self.play_music()
        self.__manager = ScreenManager()
        self.__manager.add_widget(MenuScreen(name='menu'))
        self.__manager.add_widget(GameScreen(name='game'))
        return self.__manager
        # return BoundingBox()

    def init_device(self, *args):
        self.piece.pause()
        if platform == 'android':
            import android
            android.map.key(android.KEYCODE_BACK, 1001)
        Window.bind(on_keyboard=self.on_kb)

    def on_kb(self, window, key1, key2, txt, modifiers):
        if key1 == 27 or key1 == 1001:
            self.__knock += 1
            if self.__knock > 2:
                return self.stop()
            return self.change_screen('menu')

    def play_music(self):
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
        self.piece.cb_draw(cb=self.game_engine.draw_method)

    def modify_state(self, pos, *kwargs):
        if 11 > pos[0] > 6:
            self.piece.move(RIGHT)
            self.refresh_display()
        elif -1 < pos[0] < 4:
            self.piece.move(LEFT)
            self.refresh_display()
        elif 3 < pos[0] < 7:
            self.piece.rotate()
            self.refresh_display()
        else:
            pass

    def change_screen(self, name):
        last = str(self.__manager.current)
        try:
            self.__manager.current = name
        except Exception as e:
            self.__manager.current = last
        if last != name and name in ['game', 'menu']:
            self.piece.pause()
            self.__knock = 0
        if last != name and name in ['menu', 'settings']:
            self.__knock = 0
        return True

    def widget_reset(self):
        for y in range(len(self.game_board.grid)):
            for x in range(len(self.game_board.grid[0])):
                self.widget_grid[y][x].LIT = [False, True][int(self.game_board.grid[y][x])]
        self.current_score = 'machine werkz'


if __name__ == "__main__":
    MachineWerkz().run()
