from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QFileDialog
)
import sys

from rd_loader import load_merged_data
from logic import calculate_primary
from excel_export import export_excel


class PrimaryGUI(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hemas Primary Allocation Tool")

        layout = QVBoxLayout()

        # Load merged data
        self.df = load_merged_data()

        # Distributor dropdown
        self.dist_box = QComboBox()
        dists = sorted(self.df["distributor_id"].unique())
        for d in dists:
            self.dist_box.addItem(str(d))

        layout.addWidget(QLabel("Select Distributor"))
        layout.addWidget(self.dist_box)

        # Enter primary target
        layout.addWidget(QLabel("Enter Target Primary"))
        self.primary_input = QLineEdit()
        layout.addWidget(self.primary_input)

        # Generate output
        btn = QPushButton("Generate Excel")
        btn.clicked.connect(self.generate_excel)
        layout.addWidget(btn)

        # Status text
        self.status = QLabel("")
        layout.addWidget(self.status)

        self.setLayout(layout)


    def generate_excel(self):
        dist = self.dist_box.currentText()
        target = float(self.primary_input.text())

        df_filtered = self.df[self.df["distributor_id"] == dist].copy()
        result = calculate_primary(df_filtered, target)

        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Output File", f"primary_{dist}.xlsx"
        )

        if filename:
            export_excel(result, dist, filename)
            self.status.setText("Excel Generated Successfully!")


def launch_app():
    app = QApplication(sys.argv)
    win = PrimaryGUI()
    win.show()
    sys.exit(app.exec())
