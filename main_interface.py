import csv

import math
import matplotlib
import pydub
matplotlib.use('QT5Agg')
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QShortcut, QFileDialog, QMessageBox, QInputDialog
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, QDir, QRunnable, QThreadPool, QTimer, Qt
from PyQt5 import QtGui
from configparser import ConfigParser
import os

import traceback
import pylab

import ui_dart

from worker_play_audio import worker_play_audio
from _core import generate_default_csv_format_config, generate_default_av_config, generate_default_button_label_code_config
from button_change_gui import gui_update_button
def setup_configs():
    config_folder = os.path.join("config", os.getcwd())
    # There are several configs, let's instantiate

    # get AV config
    path_to_av_config = os.path.join(config_folder, 'av_settings.cfg')
    if os.path.exists(path_to_av_config):
        av_config = ConfigParser()
        av_config.read(path_to_av_config)
    else:
        generate_default_av_config()

    # get default button config
    path_to_button_config = os.path.join(config_folder, 'button_label_code.cfg')
    if os.path.exists(path_to_button_config):
        button_config = ConfigParser()
        button_config.read(path_to_button_config)
    else:
        generate_default_button_label_code_config()

    # get CSV definition config
    path_to_csv_format_config = os.path.join(config_folder, "csv_data_format.cfg")
    if os.path.exists(path_to_csv_format_config):
        csv_config = ConfigParser()
        csv_config.read(path_to_csv_format_config)
    else:
        generate_default_csv_format_config()
    return av_config, button_config,csv_config

class dart_gui(QMainWindow, ui_dart.Ui_MainWindow):

    def __init__(self, parent=None):
        super(dart_gui, self).__init__(parent)
        self.setupUi(self)

        self.data_is_loaded = False
        self.current_index = 1
        self.detection_classification_correct = None
        self.play_flag = False

        self.timer = QTimer()

        try:

            #on initial load
            self.check_data_loaded_enable_controls()


            #load configs
            self.av_config, self.button_config, self.csv_config = setup_configs()

            #get stuff from AV config
            self.spectrogram_detection_size = eval(self.av_config['parameters']['spectrogram_detection_size_inches'])
            self.spectrogram_context_size = eval(self.av_config['parameters']['spectrogram_context_size_inches'])
            self.spectrogram_detection_duration = int(self.av_config['parameters']['spectrogram_detection_window_duration'])
            self.spectrogram_context_duration = int(self.av_config['parameters']['spectrogram_context_window_duration'])
            self.spectrogram_nfft = int(self.av_config['parameters']['nfft'])
            self.spectrogram_loop_playback_pause = int(self.av_config['playback']['playback_continuous_loop_pause_seconds'])

            #set button labels to what is in the file
            self.button_correction_A1.setText(self.button_config["button_label_code"]["A1"]["label"])
            self.button_correction_A2.setText(self.button_config["button_label_code"]["A2"]["label"])
            self.button_correction_A3.setText(self.button_config["button_label_code"]["A3"]["label"])
            self.button_correction_A4.setText(self.button_config["button_label_code"]["A4"]["label"])
            self.button_correction_A5.setText(self.button_config["button_label_code"]["A5"]["label"])

            self.button_correction_B1.setText(self.button_config["button_label_code"]["B1"]["label"])
            self.button_correction_B2.setText(self.button_config["button_label_code"]["B2"]["label"])
            self.button_correction_B3.setText(self.button_config["button_label_code"]["B3"]["label"])
            self.button_correction_B4.setText(self.button_config["button_label_code"]["B4"]["label"])


            #start playback thread
            self.start_playback_thread()

            #menu bar to load csv file and populate table
            self.actionLoad_Detections.triggered.connect(self.get_and_load_csv_manifest)

            self.actionSave_Current_File.triggered.connect(self.save_model_to_csv)

            #button to generate full detection context
            #now automatic
            #self.button_generate_context.clicked.connect(self.generate_full_context_data)

            #buttons that increase or decrease current position
            self.button_prediction_previous.clicked.connect(lambda: self.change_index_buttons(0))
            self.button_prediction_next.clicked.connect(lambda: self.change_index_buttons(1))

            #CSV and TABLE STUFF

            self.detection_table.clicked.connect(self.table_click_get_row)

            #classification:
            self.button_prediction_ai_correct.clicked.connect(lambda: self.update_rowdict(self.row_dict,"detection_ai_correct", "1", ai_is_correct=True))
            self.button_prediction_ai_incorrect.clicked.connect(lambda: self.update_rowdict(self.row_dict,"detection_ai_correct", "0", ai_is_correct=False))

            #correction
            """
            self.button_correction_A1.clicked.connect(lambda: self.update_rowdict(self.row_dict,
                                                                                  key="detection_expert_classification",
                                                                                  new_value= self.button_config["button_label_code"]["A1"]["code"], #from the button config, for the specified button, get the code (value) of the dict
                                                                                  change_species_label=True))

            self.button_correction_A2.connect(lambda: self.update_rowdict(self.row_dict,
                                                                                  key="detection_expert_classification",
                                                                                  new_value= self.button_config["button_label_code"]["A2"]["code"], #from the button config, for the specified button, get the code (value) of the dict
                                                                                  change_species_label=True))

            self.button_correction_A3.connect(lambda: self.update_rowdict(self.row_dict,
                                                                                  key="detection_expert_classification",
                                                                                  new_value= self.button_config["button_label_code"]["A3"]["code"], #from the button config, for the specified button, get the code (value) of the dict
                                                                                  change_species_label=True))

            self.button_correction_A4.connect(lambda: self.update_rowdict(self.row_dict,
                                                                                  key="detection_expert_classification",
                                                                                  new_value= self.button_config["button_label_code"]["A4"]["code"], #from the button config, for the specified button, get the code (value) of the dict
                                                                                  change_species_label=True))

            self.button_correction_A5.connect(lambda: self.update_rowdict(self.row_dict,
                                                                                  key="detection_expert_classification",
                                                                                  new_value= self.button_config["button_label_code"]["A5"]["code"], #from the button config, for the specified button, get the code (value) of the dict
                                                                                  change_species_label=True))

            self.button_correction_B1.connect(lambda: self.update_rowdict(self.row_dict,
                                                                                  key="detection_expert_classification",
                                                                                  new_value= self.button_config["button_label_code"]["B1"]["code"], #from the button config, for the specified button, get the code (value) of the dict
                                                                                  change_species_label=True))

            self.button_correction_B2.connect(lambda: self.update_rowdict(self.row_dict,
                                                                                  key="detection_expert_classification",
                                                                                  new_value= self.button_config["button_label_code"]["B2"]["code"], #from the button config, for the specified button, get the code (value) of the dict
                                                                                  change_species_label=True))

            self.button_correction_B3.connect(lambda: self.update_rowdict(self.row_dict,
                                                                                  key="detection_expert_classification",
                                                                                  new_value= self.button_config["button_label_code"]["B3"]["code"], #from the button config, for the specified button, get the code (value) of the dict
                                                                                  change_species_label=True))

            self.button_correction_B4.connect(lambda: self.update_rowdict(self.row_dict,
                                                                                  key="detection_expert_classification",
                                                                                  new_value= self.button_config["button_label_code"]["B4"]["code"], #from the button config, for the specified button, get the code (value) of the dict
                                                                                  change_species_label=True))

            self.textedit_enter_other.textChanged.connect(lambda: self.update_rowdict(self.row_dict,
                                                                                      key="detection_expert_classification",
                                                                                      new_value=self.textedit_enter_other.toPlainText(),
                                                                                      change_species_label=True))
            
            """

            self.button_correction_A1.clicked.connect(lambda:self.handle_button(self.button_correction_A1, "A1"))
            self.button_correction_A2.clicked.connect(lambda: self.handle_button(self.button_correction_A1, "A2"))
            self.button_correction_A3.clicked.connect(lambda: self.handle_button(self.button_correction_A1, "A3"))
            self.button_correction_A4.clicked.connect(lambda: self.handle_button(self.button_correction_A1, "A4"))
            self.button_correction_A5.clicked.connect(lambda: self.handle_button(self.button_correction_A1, "A5"))
            self.button_correction_B1.clicked.connect(lambda: self.handle_button(self.button_correction_B1, "B1"))
            self.button_correction_B2.clicked.connect(lambda: self.handle_button(self.button_correction_B2, "B2"))
            self.button_correction_B3.clicked.connect(lambda: self.handle_button(self.button_correction_B3, "B3"))
            self.button_correction_B4.clicked.connect(lambda: self.handle_button(self.button_correction_B4, "B4"))

            #Once done making changes, this commits the changes to
            self.button_update_detection_row.clicked.connect(self.update_model_with_new_data)

            #update dict comment after comment box is updated
            #self.textedit_insert_comment.editingFinished.connect(lambda: self.update_rowdict(self.row_dict, "detection_comment_existing", str(self.textedit_insert_comment.text())))
            self.textedit_insert_comment.textChanged.connect(lambda: self.update_rowdict(self.row_dict, "detection_comment_existing", str(self.textedit_insert_comment.toPlainText()), verbose=False))

            #play audio
            self.button_play_repeat.clicked.connect(self.play_audio_continuous)
            self.button_detection_play_once.clicked.connect(self.play_audio_once)
            self.button_play_context.clicked.connect(self.play_context_once)
            self.button_stop_context.clicked.connect(self.stop_context_play)

            #set up the timer
            self.timer.timeout.connect(self.playback_worker.play_sound)

            #audio decibel change
            self.slider_decibel_change.valueChanged.connect(self.db_dial_changed)
        except:
            self.show_message("Something went wrong", "Please send contents of black box to Ben")
            traceback.print_exc()

    def handle_button(self, button, button_id):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            self.gui_update_button_code = gui_update_button(button, self.self.button_config, button_id)

            self.gui_update_button_code.exec()

            self._new_button_label = self.gui_update_button_code.new_labelL
            self._new_button_code = self.gui_update_button_code.new_code

            button.setText(self._new_button_label)

            #need to update config
            self._new_config = str({"label":self._new_button_label, "code": self._new_button_code})
            print(self._new_config)
            self.button_label_code_config["button_label_code"][button_id] = self._new_config
            print(self.button_label_code_config["button_label_code"][button_id])
            self.update_label_species_code_config()

        else:
            print('Clicked {}'.format(button_id))


    def db_dial_changed(self):
        self.db_now = self.slider_decibel_change.value()
        self.label_decibel_current.setText("Changing audio playback by {db} dB".format(db = str(self.db_now)))
        self.playback_worker.update_db(self.db_now)

    def stop_context_play(self):
        self.playback_worker.stop_playing_now()

    def set_ai_incorrect_(self, dict, key, new_value, ai_is_correct):
        #pass this through
        #self.update_rowdict(dict, key, new_value, ai_is_correct)
        pass

    def update_rowdict(self, dict, key, new_value, change_species_label=False, ai_is_correct=False, verbose=True):
        if isinstance(new_value, str): new_value = new_value.replace(",", ";")
        dict[key] = new_value
        if verbose == True: print("set {key} to {value}".format(key=key, value=new_value))

        if change_species_label == True:
            self.label_new_expert_species.setText(str(self.row_dict['detection_expert_classification']))
            self.row_dict['detection_ai_correct'] = "0"
        if ai_is_correct == True:
            self.row_dict['detection_expert_classification'] = self.predicted_species
            self.check_correction_group()
        if ai_is_correct == False:
            self.check_correction_group()

    def check_correction_group(self):
        #print('current toggle:', self.row_dict['detection_ai_correct'])
        if self.row_dict['detection_ai_correct'] == "1":
            self.groupbox_species_correction.setDisabled(True)
            #print('disabled species correction')

        elif self.row_dict['detection_ai_correct'] == "0":
            self.groupbox_species_correction.setEnabled(True)
            #print('enabling species correction')
        else:
            self.groupbox_species_correction.setDisabled(True)
            #print('disabled species correction for fresh row')

    def play_audio_once(self):
        self.playback_worker.update_audio_data(self.audio_detection_clip, loop=False)
        self.playback_worker.start_playing_sound()
        self.timer.start()
        self.playback_worker.stop_playing_sound()
        self.timer.stop()

    def play_context_once(self):
        try:
            self.playback_worker.update_audio_data(self.audio_context_clip, loop=False)
            self.playback_worker.start_playing_sound()
            self.timer.start()
            self.playback_worker.stop_playing_sound()
            self.timer.stop()
        except:
            self.show_message("Error","Please generate context first!")

    def play_audio_continuous(self):
        if self.button_play_repeat.isChecked() == True:
            print('loop play button is checked')
            self.playback_worker.update_audio_data(self.audio_detection_clip, loop=True)
            self.playback_worker.start_playing_sound()
            self.timer.start(spectrogram_loop_playback_pause*1000) #to ms

        if self.button_play_repeat.isChecked() == False:
            print('loop play button is not checked')
            self.playback_worker.stop_playing_sound()
            self.timer.stop()
            print('stopped playing sound continuous loop')

    def start_playback_thread(self):
        """
        Very simple function to start the audio worker thread.
        """
        self.playback_thread = QThread()
        self.playback_worker = worker_play_audio(spectrogram_loop_playback_pause)
        self.playback_worker.moveToThread(self.playback_thread)
        self.playback_thread.started.connect(self.playback_worker.run)

        self.playback_thread.start()

    def hide_extra_columns(self):
        self.column_indices_to_hide = [0,2,3,4,6,8,9]
        for i in self.column_indices_to_hide:
            self.detection_table.hideColumn(i)

    def check_data_loaded_enable_controls(self):
        """
        This method is concerned with checking whether data is loaded.
        If we have a CSV loaded, we want to do a series of things,
        such as enabling buttons!

        """
        self.list_of_things_to_enable_disable = [self.button_prediction_previous,
                                                 self.button_prediction_next,
                                                 self.button_prediction_ai_correct,
                                                 self.button_prediction_ai_incorrect,
                                                 self.button_detection_play_once,
                                                 self.button_play_repeat,
                                                 self.button_stop_context,
                                                 self.textedit_insert_comment,
                                                 self.button_update_detection_row,
                                                 self.button_play_context,
                                                 self.button_correction_beluga,
                                                 self.button_correction_false,
                                                 self.button_correction_gray,
                                                 self.button_correction_humpback,
                                                 self.button_correction_killerwhale,
                                                 self.button_correction_lag,
                                                 self.button_correction_minke,
                                                 self.button_correction_pinniped,
                                                 self.button_correction_seabird,
                                                 self.button_correction_unknown,
                                                 self.textedit_enter_other]
        #removed #self.button_generate_context

        #disable those objects
        if self.data_is_loaded == False:
            for object in self.list_of_things_to_enable_disable:
                object.setDisabled(True)
        #enable those objects
        elif self.data_is_loaded == True:
            for object in self.list_of_things_to_enable_disable:
                object.setEnabled(True)

    def update_model_with_new_data(self):
        """
        Update the model with new data
        """

        #first, set human review to true
        self.update_rowdict(self.row_dict, "detection_expert_reviewed", "1")

        self.generic_log_response_to_model(self.detection_row, 12, self.row_dict["detection_expert_classification"])
        self.generic_log_response_to_model(self.detection_row, 13, self.row_dict["detection_comment_existing"])
        self.generic_log_response_to_model(self.detection_row, 14, self.row_dict["detection_ai_correct"])
        self.generic_log_response_to_model(self.detection_row, 15, self.row_dict["detection_expert_reviewed"])
        self.generic_log_response_to_model(self.detection_row, 16, self.row_dict["reviewer"])

    def save_model_to_csv(self):
        try:

            #already reviewed by this person
            if "-".join(["reviewed", self.str_reviewer_initials]) in self.filename:
                #keep the original filename...
                self.output_filename = self.filename
            else:

                self.output_filename = "-".join([os.path.splitext(os.path.basename(self.filename))[0],
                                                 "reviewed", self.str_reviewer_initials+".csv"])
                print('proposed_output_filename: ', self.output_filename)

            self.output_dir = os.path.dirname(self.filename)
            self.output_filepath = os.path.join(self.output_dir, self.output_filename)
            print("Saving to file {file}".format(file = self.output_filepath))

            with open(self.output_filepath, "w",newline="") as self.output_csv_obj:
                self.output_writer = csv.writer(self.output_csv_obj)
                self.output_writer.writerow(self.headers)

                for row in range(self.model.rowCount()):
                    self._output_row = []
                    for column in range(self.model.columnCount()):
                        self._output_row.append(self.model.index(row, column).data())
                    #print(self._output_row)
                        #self._output_row = ",".join(self._output_row)
                    self.output_writer.writerow(self._output_row)
                print('Done saving')
                self.show_message('Finished Saving Output CSV', "Your edits have been saved to {out_filename}".format(out_filename = self.output_filepath))
                self.filename = self.output_filename
        except:
            self.show_message("Failed to save!", "Failed to save, check your traceback...")
            traceback.print_exc()

    def generic_log_response_to_model(self,row_index,target_column, new_value):
        """
        After hitting the update button, we need to propagate data stored as variables to the model



        """
        print("updating row {row} column {col} with {value}".format(row = row_index, col =  target_column, value= new_value))
        self.__before = self.model.data(self.model.index(row_index,target_column))
        self.model.setData(self.model.index(row_index,target_column),new_value)
        print("before:", self.__before, "after", self.model.data(self.model.index(row_index,target_column)))

    def change_index_buttons(self, increase_decrease):
        # 1 means increase
        if increase_decrease == 1:
            self.current_index += 1

        # 0 means decrease, but not if its already at index 1
        elif increase_decrease == 0:
            if self.current_index == 1:
                pass
            else:
                self.current_index -= 1
        print("current index: %d" % self.current_index)
        self.button_click_get_row(self.current_index)

    def test(self):
        print("clicked!")

    def show_message(self, title, message):
        self.dialog = QMessageBox()
        self.dialog.setWindowTitle(title)
        self.dialog.setText(message)
        self.dialog.show()

    def update_app(self):
        """
        We have multiple elements on the screen that rely on freshly loaded data
        After we get new data, we need to refresh everything!
        """

        self.textedit_insert_comment.clear()

        self.check_data_loaded_enable_controls()

        #check to see if the correction group should be enabled
        self.check_correction_group()

        #we want to track the index!
        self.current_index = self.detection_index

        #groupbox for detection details
        self.label_prediction_index_value.setText(str(self.detection_index+1))
        self.label_prediction_species_value.setText(self.predicted_species)
        print('setting label prediction species', self.predicted_species)
        self.label_prediction_confidence_value.setText("{:.2f}".format(100*self.detection_confidence))
        self.label_prediction_wavefile_name.setText("Current File: {file}".format(file = os.path.basename(self.wave_filename)))
        self.label_new_expert_species.clear()


        #correction groupbox
        self.textedit_existing_comment.setText(self.detection_comment_existing)

        #render the spectrogram

        self.generate_wave_data(self.detection_spectrogram_start,
                                self.wave_file_path,
                                spectrogram_detection_duration,
                                spectrogram_context_duration)
                                #self.detection_time_wave_file,
                                #self.spectrogram_filepath,
                                #spectrogram_detection_duration,
                                #spectrogram_context_duration)

        self.generate_full_context_data()

    def retrieve_model_data(self, index):
        """
        Given an row, retrieve the data from the CSV QModel
        Then call for updating the GUI
        """

        try:
            self.detection_row = index
            # making new dict for this selected row
            self.row_dict = dict()
            self.detection_index = self.detection_row  # we get this from either selection of the table, OR some other source
            self.spectrogram_filepath = self.model.data(self.model.index(self.detection_row, 0))
            self.wave_filename = self.model.data(self.model.index(self.detection_row, 1))
            #self.wave_file_path = self.model.data(self.model.index(self.detection_row, 2))
            self.detection_spectrogram_start = self.model.data(self.model.index(self.detection_row, 5))
            self.spectrogram_absolute_start_time = self.model.data(self.model.index(self.detection_row, 7))
            self.detection_confidence = float(self.model.data(self.model.index(self.detection_row, 10)))
            self.predicted_species = self.model.data(self.model.index(self.detection_row, 11))

            self.detection_expert_classification = self.model.data(self.model.index(self.detection_row, 12))
            self.detection_comment_existing = self.model.data(self.model.index(self.detection_row, 13))
            self.detection_ai_correct = self.model.data(self.model.index(self.detection_row, 14))
            self.detection_expert_reviewed = self.model.data(self.model.index(self.detection_row, 15))

            self.wave_file_path = os.path.normpath(os.path.join(self.wave_directory, self.wave_filename))
            print("looking for wave file at", self.wave_file_path )

            self.row_dict = {"index": self.detection_index,
                             "filepath": self.spectrogram_filepath,
                             "detection_wave_file": self.wave_file_path,
                             "detection_time_absolute": self.spectrogram_absolute_start_time,
                             "detection_confidence": self.detection_confidence,
                             "detection_expert_classification": self.detection_expert_classification,
                             "detection_comment_existing": self.detection_comment_existing,
                             "detection_ai_correct": self.detection_ai_correct,
                             "detection_expert_reviewed": self.detection_expert_reviewed,
                             "reviewer": self.str_reviewer_initials}
            #print(self.row_dict)
            self.update_app()

        except:
            traceback.print_exc()
            self.show_message("CSV Row Load Failed!", "Check your CSV and make sure the paths are right!")


    def table_click_get_row(self, index):
        """
        On clicking a row for the Qtableview, get the selected row, and pass it to the data retriever method
        """
        #print('current index:', self.current_index)

        #print(index, index.row())
        self._clicked_table_row = index.row()

        self.retrieve_model_data(self._clicked_table_row)

        #print('table method to get new row')

    def button_click_get_row(self, index):
        self.retrieve_model_data(index)
        self.detection_table.selectRow(index)
        #print("button method to get new row")

    def get_and_load_csv_manifest(self):
        self.model = QtGui.QStandardItemModel()

        self.filename = QFileDialog.getOpenFileName(self, 'Open File Name', QDir.homePath(), "Comma-Separated Values (*.csv)")[0]
        print("Selected file {file}".format(file = self.filename))

        #if no file is selected...
        if self.filename == "":
            self.show_message("No CSV Loaded!", "Either no file was selected, or not a CSV")

        #but if you got one
        else:
            try:

                with open(self.filename, "r") as self.csv_file:
                    self.reader = csv.reader(self.csv_file)
                    self.headers = next(self.reader)
                    #print('headers', self.headers)
                    for row in self.reader:
                        items = [QtGui.QStandardItem(field) for field in row]
                        self.model.appendRow(items)
                        self.detection_table.setModel(self.model)
                        self.data_is_loaded = True
                self.model.setHorizontalHeaderLabels(self.headers)
                self.hide_extra_columns()
                #self.csv_file_object = csv.reader(self.csv_file)

                #now we need to ask where the image director is
                self.wave_directory = QFileDialog.getExistingDirectory(self, "Select where your WAVs are for the deployment", QDir.homePath())
                print(self.wave_directory)

                #now we need to know who is reviewing the spectrograms
                while 1:
                    self.str_reviewer_initials, self.ok = QInputDialog.getText(self, 'Reviewer Initials', "Enter your initials: ")
                    self.str_reviewer_initials = self.str_reviewer_initials.upper()
                    if self.ok:
                        print("Reviewer is: ", self.str_reviewer_initials)
                        self.label_reviewer_initials.setText("Reviewer: "+self.str_reviewer_initials)
                        self.show_message("FYI", "If your initials are wrong, please reload CSV. "
                                                 "Your initials are used to name the export, and embedded into your review. ")
                        break
                    else:
                        pass


            except:
                self.show_message("Failed to Load CSV", "We didn't get a CSV!")
                traceback.print_exc()

    def generate_wave_data(self, seconds_into_spectrogram, wave_file_path, spectrogram_duration, context_window):
        """

        This method is something we always do for a new entry.
        Specifically we load the wave file, generate the time window values necessary to develop spectrograms and wav clips.

        It then calls for the detection spectrogram to be generated. We do this because we always want the current detection loaded.


        """
        try:
            print('\nLoading %s' % wave_file_path)
            self.full_wave = pydub.AudioSegment.from_file(file=wave_file_path, format="wav")
            #self.full_wave = wave.open(wave_file_path, mode='rb')
            print('Done loading %s' % wave_file_path)

            self.full_wave_length_s = self.full_wave.duration_seconds
            #self.full_wave_length_s = self.full_wave.getnframes()/self.full_wave.getframerate()

            print('Opened wave {file} of {length} seconds length'.format(file=os.path.basename(wave_file_path),
                                                                       length = self.full_wave_length_s))
            #number of seconds into the wave
            self.detection_spectrogram_start = int(float(seconds_into_spectrogram))
            #length of wave
            #print(seconds_into_spectrogram, type(seconds_into_spectrogram), spectrogram_duration, type(spectrogram_duration))
            #by default, spectrograms are 2 seconds long, but let's calculate that in case we change our mind
            self.detection_spectrogram_end = self.detection_spectrogram_start + spectrogram_duration

            #if the detection is within 10 seconds of the start, let's
            if self.detection_spectrogram_start < context_window:
                self.context_start_time = 0
            else:
                self.context_start_time = self.detection_spectrogram_start - context_window

            if self.detection_spectrogram_start + context_window > self.full_wave_length_s:
                self.context_end_time = math.floor(self.full_wave_length_s)

            else:
                self.context_end_time = self.detection_spectrogram_start + context_window
            print("The spectrogram starts at {start}, ends at {end}".format(start = self.detection_spectrogram_start,
                                                                            end = self.detection_spectrogram_end))
            print("The spectrogram context starts at {start}, ends at {end}".format(start = self.context_start_time,
                                                                                    end = self.context_end_time))
            self.frames = self.full_wave.raw_data
            self.frame_rate = self.full_wave.frame_rate
            self.sound_info = pylab.frombuffer(self.frames, 'int16')

            #print("pydub:", self.frame_rate, self.sound_info)
        except:

            self.show_message("Failed to find wav",
                              "Looking for {wave_name} at {wave_path}, but failed. "
                              "Did you select the right folder?".format(wave_name = self.wave_filename,
                                                                        wave_path = self.wave_file_path))
            traceback.print_exc()
        #we always generate the small detection data
        try:
            self.generate_detection_data()
        except:
            self.show_message("Failed to find wav",
                              "Looking for {wave_name} at {wave_path}, but failed. "
                              "Did you select the right folder?".format(wave_name = self.wave_filename,
                                                                        wave_path = self.wave_file_path))

    def generate_detection_data(self):
        """
        method called by generate wave data for generating detection spectrogram
        Note! Generate spectrograms updates the GUI too!
        """

        self.generate_spectrograms(self.canvas_spectrogram_detection,
                                   self.detection_spectrogram_start,
                                   self.detection_spectrogram_end,
                                   spectrogram_detection_size)
        self.audio_detection_clip = self.generate_audio_clips("detection",
                                                              self.full_wave,
                                                              self.detection_spectrogram_start,
                                                              self.detection_spectrogram_end)

    def generate_full_context_data(self):
        """
        Called by context button in gui
        """
        self.generate_spectrograms(self.canvas_spectrogram_context,
                                   self.context_start_time,
                                   self.context_end_time,
                                   spectrogram_context_size)


        self.audio_context_clip = self.generate_audio_clips("context",
                                                            self.full_wave,
                                                            self.context_start_time,
                                                            self.context_end_time)

    def generate_spectrograms(self, canvas_object, start_seconds, end_seconds, tuple_figure_size_inches):

        #canvas_object.clear_canvas()
        print('Generating spectrogram of {w} x {h} of duration {d} with nfft {nfft}'.format(w=tuple_figure_size_inches[0],
                                                                                            h = tuple_figure_size_inches[1],
                                                                                            d = end_seconds-start_seconds,
                                                                                            nfft = spectrogram_nfft))

        #"plot it on the canvas"
        canvas_object.plot_specgram(self.sound_info[(self.frame_rate * start_seconds): (self.frame_rate * end_seconds)],
                                    spectrogram_nfft,
                                    self.frame_rate)

    def generate_audio_clips(self,audio_clip_type, audio_file,  start_seconds, end_seconds):
        print('generating wave clip from {start} to {end} seconds from {file}'.format(start = start_seconds,
                                                                                         end = end_seconds,
                                                                                         file = audio_file))

        #pydub works in milliseconds
        self.__slice_start_ms = start_seconds * 1000
        self.__slice_end_ms = end_seconds * 1000
        self.__audio_slice = audio_file[self.__slice_start_ms:self.__slice_end_ms]

        #print('generated {clip_type}'.format(clip_type = audio_clip_type))
        return self.__audio_slice

    def get_data(self):
        return self.spectrogram_detection_plot, self.audio_detection_clip, self.spectrogram_context_plot, self.audio_context_clip
