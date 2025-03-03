__author__ = "Leland Green"
__version__ = "0.1.1"
__license__ = "CC0-1.0"

import configparser
import getpass
import socket
import string
import sys

from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QFontDatabase, QFont, QFontMetrics
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QTableWidget,
    QTableWidgetItem, QPushButton, QMessageBox, QFileDialog, QAbstractItemView, QLabel
)
from sortedcontainers import SortedSet


class FontViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.pad = 5
        self.example_string = string.ascii_uppercase + " " + string.ascii_lowercase + " " + string.digits + " " + string.punctuation
        self.all_fonts_table = None
        self.favorites_table = None
        self.font_db = QFontDatabase()
        self.font_size = 16
        self.fonts = self.font_db.families()
        # Get default font to use the metrics for resizing the font name column automatically.
        self.font = QFont()
        self.font_name = self.font.family()
        print (f"Your default font: {self.font_name} Our size: {self.font_size}")
        self.font.setPointSize(self.font_size)
        self.font_metrics = QFontMetrics(self.font)
        self.favorites = SortedSet(["<init>","<stuff>"])
        self.font.setPointSize(self.font_size)
        self.config = configparser.ConfigParser()
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        # Main layout
        self.setWindowTitle("Font Viewer")
        main_layout = QVBoxLayout()

        # Scroll area 1: All Fonts
        self.all_fonts_scroll_area = QScrollArea()
        self.all_fonts_table = QTableWidget()
        self.setup_table(self.all_fonts_table)
        self.all_fonts_scroll_area.setWidget(self.all_fonts_table)
        self.all_fonts_scroll_area.setWidgetResizable(True)

        # Scroll area 2: Favorites
        self.favorites_scroll_area = QScrollArea()
        self.favorites_table = QTableWidget()
        self.setup_table(self.favorites_table)  # Initially empty
        self.favorites_scroll_area.setWidget(self.favorites_table)
        self.favorites_scroll_area.setWidgetResizable(True)

        # Connect double-click signals to the corresponding handlers
        self.all_fonts_table.itemDoubleClicked.connect(self.on_add_to_favorites_double_click)
        self.favorites_table.itemDoubleClicked.connect(self.remove_from_favorites)

        self.all_fonts_table.setFont(self.font)
        self.favorites_table.setFont(self.font)

        # Add scroll areas to the main layout
        main_layout.addWidget(self.create_labeled_section("All Fonts", self.all_fonts_scroll_area))
        main_layout.addWidget(self.create_labeled_section("Favorites", self.favorites_scroll_area))

        # Buttons at the bottom
        buttons_layout = QHBoxLayout()
        save_all_button = QPushButton("Save All")
        save_favorites_button = QPushButton("Save Favorites")
        refresh_button = QPushButton("Refresh")
        add_to_favorites_button = QPushButton("Add to Favorites")

        save_all_button.clicked.connect(self.save_all_fonts)
        save_favorites_button.clicked.connect(self.save_favorites_fonts)
        refresh_button.clicked.connect(self.refresh_all_fonts)
        add_to_favorites_button.clicked.connect(self.add_to_favorites)

        buttons_layout.addWidget(save_all_button)
        buttons_layout.addWidget(save_favorites_button)
        buttons_layout.addWidget(refresh_button)
        buttons_layout.addWidget(add_to_favorites_button)

        main_layout.addLayout(buttons_layout)

        # Set main layout
        self.setLayout(main_layout)
        self.load_fonts(self.all_fonts_table)
        print(f"{self.all_fonts_table.rowCount()} fonts in 'All Fonts' table.")

    def create_labeled_section(self, label_text, scroll_area):
        layout = QVBoxLayout()

        # Create a QLabel for the section title and set its text
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Add the provided scroll area to the layout
        layout.addWidget(scroll_area)

        # Create a container QWidget and set its layout
        container = QWidget()
        container.setLayout(layout)

        return container

    def setup_table(self, table):
        """Set up a table with some default column headers."""
        table.setColumnCount(2)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)  # Optional as per your requirement
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # To prevent editing cells if not needed

        table.setHorizontalHeaderLabels(["Font Name", "Example                                "])
        table.verticalHeader().setVisible(False)  # Hide row numbers
        table.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
        table.setSelectionBehavior(QTableWidget.SelectRows)  # Select by rows

        text_width = self.font_metrics.width(self.font_name)
        size = text_width + self.pad + 40
        table.horizontalHeader().resizeSection(0, size)
        table.setMinimumWidth(size)

    def load_fonts(self, table):
        """Load all available fonts into the specified table."""
        table.setRowCount(len(self.fonts))  # Ensure rows are set

        for row, font_name in enumerate(self.fonts):
            try:
                # Calculate text width
                text_width = self.font_metrics.width(font_name)
                # print(f"Text width for '{font_name}': {text_width}")

                # Resize column if needed
                if text_width + self.pad > table.columnWidth(0):
                    table.horizontalHeader().resizeSection(0, text_width + self.pad)
                    # print(f"Resized column 0 to {text_width + self.pad}")

                # Add font name to column 0
                font_name_item = QTableWidgetItem(font_name)
                table.setItem(row, 0, font_name_item)
                # print(f"Added '{font_name}' to row {row}, column 0.")

                # Add example string to column 1 with custom font
                example_item = QTableWidgetItem(self.example_string)
                font = self.font_db.font(font_name, '', self.font_size)
                if not font:
                    print(f"Failed to generate font for '{font_name}'")
                    continue
                example_item.setFont(font)
                table.setItem(row, 1, example_item)
                # print(f"Added example string for '{font_name}' to row {row}, column 1.")
            except Exception as e:
                print(f"Error processing '{font_name}' at row {row}: {e}")
        # print(f"All fonts in table: {table.rowCount()}")

    def save_table_to_file(self, table, filename, header=None):
        """Save all font names (column 0) from the given table to a file."""
        try:
            font_names = [table.item(row, 0).text() for row in range(table.rowCount())]
            with open(filename, "w") as file:
                if header:
                    file.write(header + "\n")
                file.write("\n".join(font_names))
            QMessageBox.information(self, "Success", f"Fonts saved to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def save_all_fonts(self):
        """Save all fonts (from the All Fonts table) to a file."""
        filename, _ = QFileDialog.getSaveFileName(self, "Save All Fonts", "font_list.txt", "Text Files (*.txt)")
        if filename:
            machine = socket.gethostname()
            self.save_table_to_file(self.all_fonts_table, filename, f"All fonts on {machine}")

    def save_favorites_fonts(self):
        """Save favorite fonts (from the Favorites table) to a file."""
        filename, _ = QFileDialog.getSaveFileName(self, "Save Favorites", "favorites_list.txt", "Text Files (*.txt)")
        if filename:
            header = f"Favorite Fonts of {getpass.getuser()} on {socket.gethostname()}:"
            self.save_table_to_file(self.favorites_table, filename, header)

    def refresh_all_fonts(self):
        """Reload all fonts into the All Fonts table."""
        self.all_fonts_table.setRowCount(0)  # Clear the table
        self.load_fonts(self.all_fonts_table)

    def on_add_to_favorites_double_click (self, item):
        """Add the selected font to favorites when double-clicked."""
        row = item.row()
        font_name = self.all_fonts_table.item(row, 0).text()
        if font_name not in self.favorites:
            self.favorites.add(font_name)
            self.update_favorites_table()

    def remove_from_favorites(self, item):
        """Remove the selected font from favorites when double-clicked."""
        selected_rows = self.favorites_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        font_name = self.favorites_table.item(row, 0).text()
        if font_name in self.favorites:
            self.favorites.discard(font_name)
            self.update_favorites_table()

    def update_favorites_table(self):
        """Update the favorites table to reflect the current favorites."""
        self.favorites_table.setRowCount(0)  # Clear the table
        # print(f"Favorites: {list(self.favorites)}")
        for row, font_name in enumerate(self.favorites):
            text_width = self.font_metrics.width(font_name)
            if text_width + self.pad > self.all_fonts_table.columnWidth(0):
                self.all_fonts_table.horizontalHeader().resizeSection(0, text_width + self.pad)
            self.favorites_table.insertRow(row)
            self.favorites_table.setItem(row, 0, QTableWidgetItem(font_name))
            example_item = QTableWidgetItem(self.example_string)
            example_item.setFont(self.font_db.font(font_name, '', self.font_size))
            self.favorites_table.setItem(row, 1, example_item)
        self.favorites_table.sortItems(0)

    def add_to_favorites(self):
        """Add the selected font from the All Fonts table to the Favorites table."""
        selected_rows = self.all_fonts_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a font to add to favorites.")
            return

        for row in selected_rows:
            font_name = self.all_fonts_table.item(row.row(), 0).text()
            if font_name not in self.favorites:
                text_width = self.font_metrics.width(font_name)
                if text_width + self.pad > self.all_fonts_table.columnWidth(0):
                    self.all_fonts_table.column(0).setMinimumWidth(text_width + self.pad)
                self.favorites.add(font_name)
                example_item = self.all_fonts_table.item(row.row(), 1)
                self.add_font_to_favorites(font_name, example_item)

    def add_font_to_favorites(self, font_name, example_item):
        """Add the specified font to the Favorites table."""
        row_count = self.favorites_table.rowCount()
        self.favorites_table.setRowCount(row_count + 1)
        self.favorites_table.setItem(row_count, 0, QTableWidgetItem(font_name))
        # self.favorites_table.setItem(row_count, 1, example_item)
        example_item = QTableWidgetItem(self.example_string)
        example_item.setFont(self.font_db.font(font_name, '', self.font_size))
        self.favorites_table.setItem(row_count, 1, example_item)

    def save_settings(self):
        """Save the window size, position, and favorites to config.ini."""
        self.config['Settings'] = {
            'window_size': f"{self.size().width()},{self.size().height()}",
            'window_position': f"{self.pos().x()},{self.pos().y()}"
        }

        self.config['Favorites'] = {
            'fonts': ','.join(self.favorites)  # Save favorites as a comma-separated list
        }

        with open("config.ini", "w") as config_file:
            self.config.write(config_file)

    def load_settings(self):
        """Load the window size, position, and favorites from config.ini."""
        self.config.read("config.ini")

        if 'Settings' in self.config:
            # Restore window size and position
            size = self.config['Settings'].get('window_size', '800,600')
            position = self.config['Settings'].get('window_position', '100,100')

            width, height = map(int, size.split(','))
            x, y = map(int, position.split(','))
            screen_size = QApplication.desktop().screenGeometry()
            screen_width = screen_size.width()
            screen_height = screen_size.height()
            if x > screen_width - 40:
                x = screen_width - 40
            if y > screen_height - 40:
                y = screen_height - 40
            if x < 0:
                x = 0
            if y < 0:
                y = 0

            if width + x > screen_width:
                if width >= screen_width:
                    width = screen_width
                    x = 0
                else:
                    x = int((screen_width - width) / 2)

            if height + y > screen_height:
                if height >= screen_height:
                    height = screen_height
                    y = 0
                else:
                    y = int((screen_height - height) / 2)

            if x > screen_width:
                x = int((screen_width - width) / 2)

            if y > screen_height:
                if height >= screen_height:
                    height = screen_height
                    y = 0
                else:
                    y = int((screen_height - height) / 2)

            if y + height > screen_height:
                y = int((screen_height - height) / 2)
            if x + width > screen_width:
                x = int((screen_width - width) / 2)

            self.resize(QSize(width, height))  # Restore window size
            self.move(QPoint(x, y))  # Restore window position

        if 'Favorites' in self.config:
            # Restore favorites
            favorite_fonts = self.config['Favorites'].get('fonts', '')
            self.favorites = set(favorite_fonts.split(',')) if favorite_fonts else set()
            discard_names = []
            for row, font_name in enumerate(self.favorites):
                if font_name not in self.font_db.families():
                    discard_names.append(font_name)

            for font_name in discard_names:
                self.favorites.discard(font_name)
                print(f'Font "{font_name}" is not in system fonts. Will be removed from config.ini on exit. (Cannot add to favorites.)')

            for row, font_name in enumerate(self.favorites):
                self.add_font_to_favorites(font_name, self.all_fonts_table.item(row, 1))

            if len(self.favorites):
                self.update_favorites_table()

    def closeEvent(self, event):
        """Save settings when the application is closed."""
        self.save_settings()
        event.accept()



def main(argc, argv):
    app = QApplication(sys.argv)
    viewer = FontViewer()
    # viewer.resize(900, 600)  # Initial size
    viewer.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)