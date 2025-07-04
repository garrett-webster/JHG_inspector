from functools import partial

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QLabel


class OpenToolDialog(QDialog):
    def __init__(self, parent, gamesets, tools):
        super().__init__(parent)
        self.gameset = None
        self.tool = None
        self.setWindowTitle("OpenTool")

        self.submit_button = QPushButton("Submit")
        self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self.accept)

        self.gamesets_layout = QVBoxLayout()
        self.tools_layout = QVBoxLayout()
        self.header_layout = QHBoxLayout()
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addLayout(self.tools_layout)
        self.buttons_layout.addLayout(self.gamesets_layout)
        self.central_layout = QVBoxLayout()

        self.header_layout.addWidget(QLabel("Select Tool"))
        self.header_layout.addWidget(QLabel("Select Gameset"))

        self.central_layout.addLayout(self.header_layout)
        self.central_layout.addLayout(self.buttons_layout)
        self.central_layout.addWidget(self.submit_button)

        if gamesets and tools:
            for gameset in gamesets:
                button = QPushButton(f"{gameset.name}")
                button.clicked.connect(partial(self.select_gameset, gameset))
                self.gamesets_layout.addWidget(button)

            for tool in tools:
                button = QPushButton(f"{tool.name}")
                button.clicked.connect(partial(self.select_tool, tool))
                self.tools_layout.addWidget(button)

        self.setLayout(self.central_layout)

    def select_tool(self, tool):
        self.tool = tool
        self.set_submit_button_state()

    def select_gameset(self, gameset):
        self.gameset = gameset
        self.set_submit_button_state()

    def set_submit_button_state(self):
        if self.tool and self.gameset:
            self.submit_button.setEnabled(True)
        else:
            self.submit_button.setEnabled(False)


