from PyQt5.QtWidgets import QDialog
import os
import ui_csv_formatting

class gui_route_data_format(QDialog, ui_csv_formatting.Ui_Dialog):
    def __init__(self, config_object, parent=None):
        super(gui_route_data_format,self).__init__(parent)
        self.setupUi(self)

        self.csv_config = config_object

        """
        Set settings from config in gui, first for required, then not required
        """


        #required
        self.entry_index_wave.setPlainText(self.csv_config['index']['wave'])
        self.entry_index_spectrogram_start.setPlainText(self.csv_config['index']['relative_spectrogram'])
        self.entry_index_score.setPlainText(self.csv_config['index']['detection_confidence'])
        self.entry_index_truth.setPlainText(self.csv_config['index']['expert_class'])

        #optional
        self.entry_predicted_species.setPlainText(self.csv_config['index']['ai_species'])
        self.entry_index_comments.setPlainText(self.csv_config['index']['comment'])
        self.entry_index_ai_correct.setPlainText(self.csv_config['index']['ai_correct'])
        self.entry_index_expertreviewed_flag.setPlainText(self.csv_config['index']['expert_reviewed'])
        self.entry_index_analyst_name.setPlainText(self.csv_config['index']['reviewer'])


        """
        When the entry is changed...
        """
        self.entry_index_wave.textChanged.connect(lambda: self.sanitize_input_update_value('wave',self.entry_index_wave))
        self.entry_index_spectrogram_start.textChanged.connect(lambda: self.sanitize_input_update_value('relative_spectrogram',self.entry_index_spectrogram_start))
        self.entry_index_score.textChanged.connect(lambda: self.sanitize_input_update_value('detection_confidence',self.entry_index_score))
        self.entry_index_truth.textChanged.connect(lambda: self.sanitize_input_update_value('expert_class',self.entry_index_truth))

        # optional
        self.entry_predicted_species.textChanged.connect(lambda: self.sanitize_input_update_value('ai_species',self.entry_predicted_species))
        self.entry_index_comments.textChanged.connect(lambda: self.sanitize_input_update_value('comment',self.entry_index_comments))
        self.entry_index_ai_correct.textChanged.connect(lambda: self.sanitize_input_update_value('ai_correct',self.entry_index_ai_correct))
        self.entry_index_expertreviewed_flag.textChanged.connect(lambda: self.sanitize_input_update_value('expert_reviewed',self.entry_index_expertreviewed_flag))
        self.entry_index_analyst_name.textChanged.connect(lambda: self.sanitize_input_update_value('reviewer',self.entry_index_analyst_name))

    def sanitize_input_update_value(self,field_name, entry_object):
        value = entry_object.toPlainText().strip() #get plain text of whatever value is there, then remove whitespaces

        try:
            value = int(value)
            #set config dict to that value
            self.csv_config['index'][field_name] = value
        except:
            self.show_message(title="Error!", message="Last input not a number!")
            entry_object.clear()

    def update_config_file(self):
        """
        On exit, update the config file
        """
        with open(os.path.join(os.getcwd(),"config","csv_data_format.cfg")) as cfg_file_obj:
            self.csv_config.write(cfg_file_obj)
            self.show_message(title="Updated CSV Config!", message="Updated config saved to disk!")