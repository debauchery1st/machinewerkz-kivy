from kivy.core.audio import SoundLoader
from time import sleep
from os import listdir, path


OK_SOUNDS = ['mp3', 'ogg', 'wav']


def music_list(music_dir=None):
    if music_dir is None:
        return None
    return [path.join(music_dir, _) for _ in listdir(music_dir) if str(_)[-3:] in OK_SOUNDS]


def fx_dict(fx_dir=None):
    if fx_dir is None:
        return None
    res = {}
    fx_list = [path.join(fx_dir, _) for _ in listdir(fx_dir) if str(_)[-3:] in OK_SOUNDS]
    for _ in fx_list:
        f_name = path.split(_)[-1].split('.')[0]
        res[f_name] = _
    return res


def load_audio(file):
    sound = SoundLoader.load(file)
    # if not sound:
    #     print("NO Sound found at %s" % sound.source)
    # else:
    #     print("Sound is %.3f seconds" % sound.length)
    return sound


if __name__ == "__main__":
    sound = load_audio('data/audio/notintro.ogg')
    sound.play()
    while True:
        sleep(.000001)
