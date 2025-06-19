import os

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog, \
    QSizePolicy, QScrollArea, QWidget


class NewGamesetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Gameset")
        self.setFixedWidth(250)

        self.directory_path = None
        self.name = None

        self.name_input = QLineEdit(self)
        self.name_input.textChanged.connect(self.on_text_changed)
        load_files_button = QPushButton("Load Files", self)
        load_files_button.clicked.connect(self.load_files)

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.on_submit)
        self.submit_button.setDisabled(True)

        self.path_label = QLabel(self)
        self.path_label.setWordWrap(True)

        clear_button = QPushButton("Clear", self)
        clear_button.clicked.connect(self.clear_directory)
        scroll_area_container = QWidget(self)
        scroll_area_layout = QVBoxLayout()
        scroll_area_layout.addWidget(clear_button)
        scroll_area_layout.addWidget(self.path_label)
        scroll_area_container.setLayout(scroll_area_layout)

        self.path_scroll_area = QScrollArea(self)
        self.path_scroll_area.setMinimumHeight(100)
        self.path_scroll_area.setWidget(scroll_area_container)
        self.path_scroll_area.setVisible(False)
        self.path_scroll_area.setWidgetResizable(True)


        layout = QVBoxLayout()
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Name"))
        row1.addWidget(self.name_input)
        row2 = QHBoxLayout()
        row2.addWidget(load_files_button)
        row2.addWidget(self.submit_button)

        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addWidget(self.path_scroll_area)

        self.setLayout(layout)

    def load_files(self):
        self.directory_path = QFileDialog.getExistingDirectory(self)
        if self.directory_path:
            self.path_label.setText(self.directory_path)
            self.path_scroll_area.setVisible(True)
            self.submit_button.setDisabled(False)

            if not self.name_input.text():
                self.name = os.path.basename(self.directory_path)
                self.name_input.setText(self.name)

    def on_text_changed(self, text:str):
        if not text:
            self.submit_button.setDisabled(True)
            self.name = text
        else:
            self.submit_button.setDisabled(False)

    def clear_directory(self):
        if self.directory_path is not None and self.name_input.text() == os.path.basename(self.directory_path):
            self.name_input.setText("")
            self.name = None
            self.submit_button.setDisabled(True)

        self.directory_path = None
        self.path_label.setText("")
        self.path_scroll_area.setVisible(False)
        self.adjustSize()

    def on_submit(self):
        self.name = self.name_input.text()
        self.accept()

