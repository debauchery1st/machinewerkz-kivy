from kivy.core.audio import SoundLoader
from time import sleep


def load_audio(file):
    sound = SoundLoader.load(file)
    if sound:
        print("Sound found at %s" % sound.source)
        print("Sound is %.3f seconds" % sound.length)

    return sound


if __name__ == "__main__":
    sound = load_audio('data/audio/intro.ogg')
    sound.play()
    while True:
        sleep(.000001)

