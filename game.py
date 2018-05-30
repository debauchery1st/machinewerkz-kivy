from copy import deepcopy
from random import randrange

from shapes import get_shape


UP, DOWN = 1, 2
LEFT, RIGHT = 3, 4


class Picard:
    def __init__(self, **kwargs):
        if Picard.__instance__ is None:
            Picard.__instance__ = Picard.__Picard__(**kwargs)

    class __Picard__:
        display_x, display_y = 0, 0
        grid_x, grid_y = 1, 1
        shape, state, screen, = 0, 0, None
        board, pg = None, None
        swap = None
        fell, score = 0, 0
        game_on = True
        text_score = [""]
        text_pos = [0, 0]
        text_size = 0
        restart_callback = None
        prize, level, __lvct, __ceil = 0, 0, 0, 0

        def __init__(self, **kwargs):
            for k in kwargs.keys():
                self.__dict__[k] = kwargs[k]
            if self.shape is None:
                self.move(RIGHT)
                self.move(RIGHT)
                self.shape = randrange(100) % 7
                print(self.shape)

        def __score_text(self):
            if self.game_on:
                self.text_score = ["TOTAL {}".format(self.score)]
            return self.text_score

        def __draw_board(self, board=None, keeping_score=False, cb=None):
            scr = []
            if board is None:
                board = self.board.grid
            for y in range(len(board)):
                if 0 not in board[y] and keeping_score:
                    scr.append(y)
            if len(scr) > 0:
                board = self.__wipe_rows(scr, board)
                del scr[:]
                self.__draw_board(board=board)
            if cb is not None:
                cb(board)
            return board

        def __wipe_rows(self, rows, grid):
            total = 0
            l = len(grid[0])
            for row in sorted(rows):
                del grid[row]
                grid.insert(0, [0 for _ in range(l)])
                total += l
            if total == l*l:
                print('bonus!')
                total += l*2
            self.score += total
            self.__lvct += total % 100
            if self.__lvct == 0:
                self.level += 1
            self.prize = total
            return grid

        def __translate(self):
            h, i, j, k, _, _, _, _ = get_shape(
                self.grid_x, self.grid_y,
                1, self.state, self.shape)
            return [(_[0], _[1]) for _ in [h, i, j, k] if _[1] >= 0]

        def game_over(self):
            self.text_pos = (100, 200)
            self.text_size = int(self.board.square_unit/1.6)
            self.text_score = ['GAME OVER', 'SCORE {}'.format(self.score)]
            self.game_on = False

        def pause(self):
            unpaused = (self.board.cols * self.board.square_unit) - self.board.square_unit*3
            if self.game_on:
                self.text_pos = (100, 200)
                self.text_size = int(self.board.square_unit / 1.6)
                self.game_on = False
                if 'GAME OVER' in self.text_score:
                    self.restart_game()
                self.text_score = ['PAUSED', 'SCORE {}'.format(self.score)]
            else:
                self.text_pos = (unpaused, 0)
                self.text_size = int(self.board.square_unit / 4)
                self.game_on = True
                if 'GAME OVER' in self.text_score:
                    self.restart_game()

        def restart_game(self):
            print('restarting game')
            x = (self.board.cols * self.board.square_unit) - self.board.square_unit*3
            self.text_size = int(self.board.square_unit / 4)
            self.text_pos = [x, 0]
            self.state = randrange(100) % 5
            self.score = 0
            self.game_on = True
            self.board.reset()
            self.reset()
            if self.restart_callback is not None:
                self.restart_callback()

        def reset(self):
            self.display_x, self.display_y = 0, 0
            self.grid_x, self.grid_y = 0, 0
            self.move(RIGHT)
            self.move(RIGHT)
            self.fell = 0
            self.text_score = self.__score_text()

        def fall(self):
            self.move(DOWN)
            self.fell += 1

        def cb_draw(self, cb=None):
            self.__score_text()
            if not self.game_on:
                self.__draw_board(cb=cb)
                return True, "finished"
            locutus, of_borg = self.replicate(self.board.grid, 2)  # replicate
            z = self.__translate()  # translate
            error, msg = self.in_bounds(locutus, z)
            # are we out of bounds?
            if error == 4:
                # ceiling
                self.__ceil += 1
                if self.__ceil > 4:
                    self.game_over()
            elif error != 0 and error != 4:
                scr = []
                board = self.__draw_board(board=self.swap, keeping_score=True, cb=cb)
                self.swap = board
                del locutus, of_borg
                if error == 3:
                    # have we hit the floor?
                    return False, msg
                return True, msg
            # in bounds,
            try:
                for _x, _y in z:
                    locutus[_y][_x] = 1  # simulate
            except IndexError as e:
                raise e
            # does it overlap ?
            if not self.overlap(of_borg, locutus, z):
                self.swap = self.replicate(locutus, 1)[0]
                self.__draw_board(board=locutus, cb=cb)
                self.__ceil = 0
                result = True, 'ok'
            else:
                if self.fell < 1:
                    self.game_over()
                self.__draw_board(board=self.swap, keeping_score=True, cb=cb)
                result = False, "overlap"
            del locutus, of_borg
            return result

        def swap_grid(self, grid=None):
            if grid is None:
                grid = self.swap
            self.board.grid = self.replicate(grid, 1)[0]

        def shape_shift(self):
            self.shape = randrange(1, 100)

        def rotate(self):
            self.state += 1

        def move(self, n):
            if n in [LEFT, RIGHT, UP, DOWN]:
                if n == LEFT and self.grid_x != 0:
                    self.grid_x -= 1
                    self.display_x -= self.board.square_unit
                elif n == RIGHT and (self.grid_x + 1 < len(self.swap[0])):
                    self.grid_x += 1
                    self.display_x += self.board.square_unit
                elif n == DOWN and self.grid_y < self.board.rows:
                    self.grid_y += 1
                    self.display_y += self.board.square_unit
                elif n == UP and self.grid_y > 0:
                    self.grid_y -= 1
                    self.display_y -= self.board.square_unit

        @staticmethod
        def in_bounds(grid, points):
            result = 0
            msg = "ok"
            for _x, _y in points:
                if _x + 1 > len(grid[0]):
                    result = 9
                    msg = "    wall    |"
                elif _x < 0:
                    result = 6
                    msg = "|   wall"
                if _y + 1 > len(grid):
                    result = 3
                    msg = "___floor___"
                elif _y - 1 < 3:
                    result = 4
                    msg = "ceiling"
            return result, msg

        @staticmethod
        def replicate(item, n=1):
            res = []
            for _ in range(n):
                res.append(deepcopy(item))
            return res

        @staticmethod
        def overlap(grid_one, grid_two, points):
            z = [(grid_one[y][x] + grid_two[y][x]) for x, y in points]
            if 2 in z:
                # print('overlap')
                return True
            return False

    __instance__ = None

    def __getattr__(self, item):
        if Picard.__instance__:
            return getattr(Picard.__instance__, item)

    def __setattr__(self, key, value):
        if Picard.__instance__:
            return setattr(Picard.__instance__, key, value)


class Borg:
    _shared_state = {}

    def __init__(self, **kwargs):
        self.square_unit = 40
        self.cols = 0
        self.rows = 0
        self.__dict__ = self._shared_state
        try:
            for _ in ['square_unit', 'cols', 'rows']:
                assert _ in kwargs.keys()
        except Exception as e:
            print("requires : {}".format(['square_unit', 'cols', 'rows']))
            raise e
        # assimilate primitives
        for prim in kwargs.keys():
            self.__dict__[prim] = kwargs[prim]
        self.width, self.height = self.rows * self.square_unit, self.cols * self.square_unit
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def reset(self):
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
