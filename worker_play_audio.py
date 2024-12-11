
import matplotlib
from pydub.playback import play, _play_with_simpleaudio
matplotlib.use('QT5Agg')
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, QDir, QRunnable, QThreadPool, QTimer


class worker_play_audio(QObject):
    @pyqtSlot()
    def __init__(self, pause_duration, parent=None):
        super(worker_play_audio, self).__init__()
        print("audio playing thread is alive")
        self.audio_segment = None
        self.continuous_TF = None
        self.pause_duration = pause_duration
        self.play = False
        self.index = 0
        self.db_delta = 0

    def run(self):
        self.play_sound()

    def update_audio_data(self, audio_segment, loop):
        print("updated audio!")
        self.audio_segment = audio_segment
        self.continuous_TF = loop

    def update_db(self, new_db):
        self.db_delta = new_db
        #print("worker got db delta {db_delta}".format(db_delta = self.db_delta))

    def play_sound(self):
        #print('waiting to play sound')

        if self.play == True:
            print("{index} playing sound! Continuous {tf}".format(index = self.index, tf=self.continuous_TF))
            self.index += 1
            #print('current volume boost is {boost}'.format(boost = self.db_delta))
            self.playback = _play_with_simpleaudio(self.audio_segment + self.db_delta)

    def start_playing_sound(self):
        #print('play flag is true')
        self.play = True
        self.play_sound()

    def stop_playing_sound(self):
        #print('play flag is false')
        self.play = False
    def stop_playing_now(self):
        self.playback.stop()


