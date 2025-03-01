import os

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase

# Initialize the QApplication
app = QApplication([])  # MUST be created before using QFontDatabase

# Get all available font families
font_database = QFontDatabase()
available_fonts = font_database.families()

out_name = os.path.join(os.getcwd(), "font_list.txt")

# Print the list of fonts
print("Available Font Families:")
with open(out_name, "w") as f:
    for font in available_fonts:
        print(font)
        f.write(font + "\n")

# Optional: Exit the app if using QApplication here
app.exit()
