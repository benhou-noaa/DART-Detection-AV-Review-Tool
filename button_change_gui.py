from PyQt5.QtWidgets import QDialog
import ui_change_button_label_code
import ast
class gui_update_button(QDialog, ui_change_button_label_code.Ui_Dialog):
    def __init__(self, button, button_config, button_id, parent=None):
        super(gui_update_button, self).__init__(parent)
        self.setupUi(self)

        self.target_button = button
        self.button_config = button_config
        self._button_dict = ast.literal_eval(self.button_config["button_label_code"][button_id])
        self.current_label = self._button_dict["label"]
        self.current_code = self._button_dict["code"]

        """
        Set value to whatever it should be
        """
        self.text_entry_set_button_label.setPlainText(self.current_label)
        self.text_entry_set_button_code.setPlainText(self.current_code)

        """
        Instantiate new values
        """
        self.new_label = None
        self.new_code = None
        """
        If the value is updated, sanitize the input and update variable
        """
        self.text_entry_set_button_label.textChanged.connect(lambda: self.set_new_label(self.text_entry_set_button_label.toPlainText()))
        self.text_entry_set_button_code.textChanged.connect(lambda: self.set_new_code(self.text_entry_set_button_code.toPlainText()))

    def set_new_label(self, value):
        self.new_label = value.replace(" ","_").strip().upper()
    def set_new_code(self, value):
        self.new_code = value.replace(" ","_").strip().upper()
