from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QShortcut, QFileDialog, QMessageBox, QInputDialog
def generate_default_av_config():
    pass

def generate_default_button_label_code_config():
    pass

def generate_default_csv_format_config():
    pass

def show_message(self, title, message):
    self.dialog = QMessageBox()
    self.dialog.setWindowTitle(title)
    self.dialog.setText(message)
    self.dialog.show()