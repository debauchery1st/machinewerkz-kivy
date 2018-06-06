from kivy.core.audio import SoundLoader
from time import sleep
from os import listdir, path


def audio_files(folder=None):
    OK_SOUNDS = ['mp3', 'ogg', 'wav', 'flac']
    if folder is None or not path.exists(folder):
        return []
    result = [path.join(folder, _) for _ in listdir(folder) if _.split('.')[-1] in OK_SOUNDS]
    return result


def music_list(music_dir=None):
    return audio_files(music_dir)


def fx_dict(fx_dir=None):
    if fx_dir is None:
        return None
    res = {}
    fx_list = audio_files(fx_dir)
    for _ in fx_list:
        f_name = path.split(_)[-1].split('.')[0]
        res[f_name] = _
    return res


def load_audio(file):
    sound = SoundLoader.load(file)
    return sound


if __name__ == "__main__":
    from time import time
    test = audio_files('data/audio/fx')
    sound = load_audio(test.pop(0))
    over = sound.length
    print('playing sound for {} seconds'.format(sound.length))
    t = time()
    sound.play()
    cnt = 0
    while cnt < over:
        sleep(.1)
        cnt += .1
    sound.stop()
    del sound
    print(time() - t)
