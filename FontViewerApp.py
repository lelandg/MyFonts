import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QHeaderView,
    QAbstractItemView,
)
from PyQt5.QtGui import QFontDatabase, QFont


class FontViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Font Viewer")

        # Set up the main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        main_layout = QVBoxLayout(self.main_widget)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)

        # Table Widget to display fonts
        self.table = QTableWidget()
        self.scroll_area.setWidget(self.table)

        # Prepare the table with headers
        self.setup_table()

        # Load font information into the table
        self.load_fonts()

        # QTimer.singleShot(50, self.resize_middle_column)


    def setup_table(self):
        """Set up the table widget with proper headers."""
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Font Name", "Font Example"])

        # Allow manual resizing for all columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # Set a default row height for better font visibility
        # default_row_height = 50  # Set the height in pixels
        # self.table.verticalHeader().setDefaultSectionSize(default_row_height)
        self.table.verticalHeader().setVisible(False)

        # Enable pixel-perfect scrolling
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

    def load_fonts(self):
        """Load available fonts into the table."""
        font_database = QFontDatabase()
        families = font_database.families()

        # Sentence to demonstrate fonts
        example_sentence = "The quick brown fox jumps over the lazy dog. 0123456789 !@#$%^&*()?"

        # Add fonts to the table
        for family in families:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            # Font name
            font_name_item = QTableWidgetItem(family)
            self.table.setItem(row_position, 0, font_name_item)

            # Font example
            example_label = QLabel(example_sentence)
            example_font = QFont(family)
            example_font.setPointSize(16)  # Set the font size
            example_label.setFont(example_font)
            self.table.setCellWidget(row_position, 1, example_label)

        # Adjust row heights based on font sizes
        self.adjust_row_heights()

    def adjust_row_heights(self):
        """Adjust row heights to match the displayed font examples."""
        for row in range(self.table.rowCount()):
            example_widget = self.table.cellWidget(row, 1)
            if example_widget:
                self.table.setRowHeight(row, example_widget.sizeHint().height())

    def resize_middle_column(self):
        """Resize the middle column to fill the remaining space."""
        # Set fixed widths for the first and last columns
        column_0_width = 200  # Width for the first column (Font Name)
        # column_2_width = 150  # Width for the third column (Font File Path)
        self.table.setColumnWidth(0, column_0_width)
        # self.table.setColumnWidth(2, column_2_width)
        width = self.window().size().width()
        scrollbar_width = self.scroll_area.verticalScrollBar().width()
        # print(f"Window width: {width} Scrollbar Width: {scrollbar_width}")
        # Calculate the available width for the middle column
        remaining_width = (
                width
                - column_0_width
                # - column_2_width
                - 40  # Account for padding/margins
                # - (int(scrollbar_width / 2))  # Account for scrollbar width, if visible
        )

        if remaining_width > 0:
            self.table.setColumnWidth(1, remaining_width)  # Adjust the middle column width to fill space

    def resizeEvent(self, event):
        """Handle window resize events to adjust the middle column."""
        super().resizeEvent(event)
        self.resize_middle_column()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = FontViewer()
    viewer.resize(900, 600)  # Initial size
    viewer.show()
    sys.exit(app.exec())
