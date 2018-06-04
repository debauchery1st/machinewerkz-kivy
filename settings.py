from os import path, getcwd

from kivy.logger import Logger
from kivy.config import Config
from kivy.utils import platform
from kivy.core.window import Window

from audio import music_list, fx_dict


def load_default_config(from_file=False):
    Config.window_icon = path.join(getcwd(), 'data/img/steampunk.png')
    Config.set('kivy', 'exit_on_escape', '0')
    Config.set('graphics', 'resizable', '0')

    try:
        Logger.info('[MachineWerkz] setting defaults')
        default_config = {
            'fx_folder': path.join(getcwd(), 'data/audio/fx'),
            'music_folder': path.join(getcwd(), 'data/audio/music'),
            'cols': "10", 'rows': "18", 'square_unit': "50"
        }
    except Exception as e:
        raise e

    square_unit = int(default_config['square_unit'])
    rows = int(default_config['rows'])
    cols = int(default_config['cols'])
    ini = path.join(getcwd(), 'machinewerkz.ini')

    if path.isfile(ini) and from_file is True:
        Config.read(ini)
        Logger.info('[MachineWerkz] loading configuration')
        playlist = music_list(Config.get('machinewerkz', 'music_folder'))
        fx = fx_dict(Config.get('machinewerkz', 'fx_folder'))
        rows = int(Config.get('machinewerkz', 'rows'))
        cols = int(Config.get('machinewerkz', 'cols'))
    else:
        playlist = music_list(default_config['music_folder'])
        fx = fx_dict(default_config['fx_folder'])

    return {'square_unit': square_unit, 'rows': rows, 'cols': cols, 'music': playlist, 'fx': fx}


def default_settings(from_file=False):
    local_default = load_default_config(from_file=from_file)
    if platform in ['linux', 'window', 'mac']:
        w = local_default['square_unit'] * local_default['cols']
        h = local_default['square_unit'] * local_default['rows']
        Window.size = (w, h)  # resize the window
    return local_default
