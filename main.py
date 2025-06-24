#!/usr/bin/env python3
"""
PyQt5 Image Steganography Tool
Cross-platform compatible version using PyQt5
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                            QLineEdit, QFileDialog, QMessageBox, QDialog,
                            QScrollArea, QFrame, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PIL import Image

class ImageSteganography:
    """Core steganography functionality"""
    
    @staticmethod
    def generate_data(pixels, data):
        """Convert data to binary and modify pixels for encoding"""
        # Add delimiter to mark end of data
        data += chr(0)  # NULL character as delimiter
        data_in_binary = []

        for char in data:
            binary_data = format(ord(char), '08b')
            data_in_binary.append(binary_data)

        length_of_data = len(data_in_binary)
        image_data = iter(pixels)

        for i in range(length_of_data):
            try:
                # Get 9 pixel values (3 pixels × 3 RGB values)
                pixel_set = []
                for _ in range(3):
                    pixel = next(image_data)
                    pixel_set.extend(pixel[:3])  # Only RGB, ignore alpha if present
                
                # Modify the LSB of each of the first 8 values
                for j in range(8):
                    if data_in_binary[i][j] == '1':
                        if pixel_set[j] % 2 == 0:
                            pixel_set[j] += 1 if pixel_set[j] < 255 else -1
                    else:  # bit is '0'
                        if pixel_set[j] % 2 == 1:
                            pixel_set[j] -= 1 if pixel_set[j] > 0 else -1

                # Return modified pixels
                yield tuple(pixel_set[:3])
                yield tuple(pixel_set[3:6])
                yield tuple(pixel_set[6:9])
                
            except StopIteration:
                raise Exception("Image is too small to encode this message!")

    @staticmethod
    def encrypt_image(img, data):
        """Encode data into the image"""
        width, height = img.size
        x, y = 0, 0
        
        for pixel in ImageSteganography.generate_data(img.getdata(), data):
            if y >= height:
                raise Exception("Image is too small for this message!")
                
            img.putpixel((x, y), pixel)
            
            x += 1
            if x >= width:
                x = 0
                y += 1
        
        return True

    @staticmethod
    def encode_message(img_path, text, output_path):
        """Main encryption function with error handling"""
        if not img_path or not text or not output_path:
            raise Exception("Please fill in all fields!")
            
        if not os.path.exists(img_path):
            raise Exception("Input image file not found!")
        
        # Open and validate image
        image = Image.open(img_path).convert('RGB')
        
        # Check if image is large enough
        min_pixels_needed = (len(text) + 1) * 3  # +1 for delimiter, *3 for 3 pixels per character
        total_pixels = image.size[0] * image.size[1]
        
        if total_pixels < min_pixels_needed:
            raise Exception(f"Image is too small!\nNeed at least {min_pixels_needed} pixels for this message.\nImage has {total_pixels} pixels.")
        
        # Create new image and encode
        new_image = image.copy()
        ImageSteganography.encrypt_image(new_image, text)
        
        # Ensure output has .png extension
        if not output_path.lower().endswith('.png'):
            output_path += '.png'
        
        new_image.save(output_path, 'PNG')
        return output_path

    @staticmethod
    def decode_message(img_path):
        """Main decryption function with error handling"""
        if not img_path:
            raise Exception("Please select an image file!")
            
        if not os.path.exists(img_path):
            raise Exception("Image file not found!")
        
        image = Image.open(img_path).convert('RGB')
        data = ''
        image_data = iter(image.getdata())

        while True:
            try:
                # Get 9 pixel values (3 pixels × 3 RGB values)
                pixel_set = []
                for _ in range(3):
                    pixel = next(image_data)
                    pixel_set.extend(pixel[:3])

                # Extract binary data from LSBs of first 8 values
                binary_string = ''
                for i in range(8):
                    binary_string += str(pixel_set[i] % 2)

                # Convert binary to character
                char = chr(int(binary_string, 2))
                
                # Check for delimiter (NULL character)
                if ord(char) == 0:
                    break
                    
                data += char
                
            except (StopIteration, ValueError):
                break
        
        if not data:
            raise Exception("No hidden message found in this image!")
        
        return data


class EncodeDialog(QDialog):
    """Dialog for encoding messages into images"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Encode Message into Image")
        self.setFixedSize(700, 600)
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the encoding dialog UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🔒 Encode Message into Image")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #333; margin: 20px;")
        layout.addWidget(title)
        
        # Input image selection
        img_frame = QFrame()
        img_layout = QVBoxLayout()
        
        img_label = QLabel("Select Input Image:")
        img_label.setFont(QFont("Arial", 12, QFont.Bold))
        img_layout.addWidget(img_label)
        
        img_input_layout = QHBoxLayout()
        self.img_path_input = QLineEdit()
        self.img_path_input.setPlaceholderText("Select an image file...")
        self.img_path_input.setMinimumHeight(35)
        img_input_layout.addWidget(self.img_path_input)
        
        browse_img_btn = QPushButton("Browse")
        browse_img_btn.setMinimumSize(80, 35)
        browse_img_btn.clicked.connect(self.browse_input_image)
        browse_img_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        img_input_layout.addWidget(browse_img_btn)
        
        img_layout.addLayout(img_input_layout)
        img_frame.setLayout(img_layout)
        layout.addWidget(img_frame)
        
        # Message input
        msg_frame = QFrame()
        msg_layout = QVBoxLayout()
        
        msg_label = QLabel("Secret Message to Hide:")
        msg_label.setFont(QFont("Arial", 12, QFont.Bold))
        msg_layout.addWidget(msg_label)
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter your secret message here...\nYou can type multiple lines of text.")
        self.message_input.setMinimumHeight(150)
        self.message_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
            }
            QTextEdit:focus {
                border-color: #4CAF50;
            }
        """)
        msg_layout.addWidget(self.message_input)
        
        msg_frame.setLayout(msg_layout)
        layout.addWidget(msg_frame)
        
        # Output file selection
        output_frame = QFrame()
        output_layout = QVBoxLayout()
        
        output_label = QLabel("Output File (will be saved as PNG):")
        output_label.setFont(QFont("Arial", 12, QFont.Bold))
        output_layout.addWidget(output_label)
        
        output_input_layout = QHBoxLayout()
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("Choose where to save the encoded image...")
        self.output_path_input.setMinimumHeight(35)
        output_input_layout.addWidget(self.output_path_input)
        
        browse_output_btn = QPushButton("Browse")
        browse_output_btn.setMinimumSize(80, 35)
        browse_output_btn.clicked.connect(self.browse_output_path)
        browse_output_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        output_input_layout.addWidget(browse_output_btn)
        
        output_layout.addLayout(output_input_layout)
        output_frame.setLayout(output_layout)
        layout.addWidget(output_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        encode_btn = QPushButton("🔒 Encode Image")
        encode_btn.setMinimumSize(150, 45)
        encode_btn.setFont(QFont("Arial", 12, QFont.Bold))
        encode_btn.clicked.connect(self.encode_image)
        encode_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        button_layout.addWidget(encode_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumSize(150, 45)
        cancel_btn.setFont(QFont("Arial", 12, QFont.Bold))
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c41e0f;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def browse_input_image(self):
        """Browse for input image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image files (*.png *.jpg *.jpeg *.gif *.bmp *.tiff);;All files (*.*)"
        )
        if file_path:
            self.img_path_input.setText(file_path)
            
    def browse_output_path(self):
        """Browse for output file path"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Encoded Image As",
            "",
            "PNG files (*.png);;All files (*.*)"
        )
        if file_path:
            self.output_path_input.setText(file_path)
            
    def encode_image(self):
        """Encode the message into the image"""
        try:
            img_path = self.img_path_input.text().strip()
            message = self.message_input.toPlainText().strip()
            output_path = self.output_path_input.text().strip()
            
            if not message:
                QMessageBox.warning(self, "Error", "Please enter a secret message to hide!")
                return
                
            output_file = ImageSteganography.encode_message(img_path, message, output_path)
            QMessageBox.information(self, "Success", 
                f"Message encoded successfully!\nSaved as: {os.path.basename(output_file)}")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class DecodeDialog(QDialog):
    """Dialog for decoding messages from images"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Decode Message from Image")
        self.setFixedSize(700, 650)
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the decoding dialog UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🔓 Decode Message from Image")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #333; margin: 20px;")
        layout.addWidget(title)
        
        # Input image selection
        img_frame = QFrame()
        img_layout = QVBoxLayout()
        
        img_label = QLabel("Select Encoded Image:")
        img_label.setFont(QFont("Arial", 12, QFont.Bold))
        img_layout.addWidget(img_label)
        
        img_input_layout = QHBoxLayout()
        self.img_path_input = QLineEdit()
        self.img_path_input.setPlaceholderText("Select an encoded image file...")
        self.img_path_input.setMinimumHeight(35)
        img_input_layout.addWidget(self.img_path_input)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setMinimumSize(80, 35)
        browse_btn.clicked.connect(self.browse_image)
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        img_input_layout.addWidget(browse_btn)
        
        img_layout.addLayout(img_input_layout)
        img_frame.setLayout(img_layout)
        layout.addWidget(img_frame)
        
        # Decode button
        decode_btn = QPushButton("🔍 Decode Message")
        decode_btn.setMinimumSize(200, 45)
        decode_btn.setFont(QFont("Arial", 12, QFont.Bold))
        decode_btn.clicked.connect(self.decode_message)
        decode_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                margin: 20px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        layout.addWidget(decode_btn, alignment=Qt.AlignCenter)
        
        # Result display
        result_frame = QFrame()
        result_layout = QVBoxLayout()
        
        result_label = QLabel("Decoded Message:")
        result_label.setFont(QFont("Arial", 12, QFont.Bold))
        result_layout.addWidget(result_label)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(200)
        self.result_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
                background-color: #f9f9f9;
            }
        """)
        result_layout.addWidget(self.result_text)
        
        result_frame.setLayout(result_layout)
        layout.addWidget(result_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.copy_btn = QPushButton("📋 Copy Message")
        self.copy_btn.setMinimumSize(150, 45)
        self.copy_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.copy_btn.clicked.connect(self.copy_message)
        self.copy_btn.setEnabled(False)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #F57C00;
            }
            QPushButton:pressed:enabled {
                background-color: #E65100;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        button_layout.addWidget(self.copy_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setMinimumSize(150, 45)
        close_btn.setFont(QFont("Arial", 12, QFont.Bold))
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #546E7A;
            }
            QPushButton:pressed {
                background-color: #455A64;
            }
        """)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def browse_image(self):
        """Browse for encoded image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Encoded Image",
            "",
            "Image files (*.png *.jpg *.jpeg *.gif *.bmp *.tiff);;All files (*.*)"
        )
        if file_path:
            self.img_path_input.setText(file_path)
            
    def decode_message(self):
        """Decode message from the selected image"""
        try:
            img_path = self.img_path_input.text().strip()
            decoded_message = ImageSteganography.decode_message(img_path)
            
            self.result_text.setPlainText(decoded_message)
            self.result_text.setStyleSheet("""
                QTextEdit {
                    border: 2px solid #4CAF50;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 11pt;
                    background-color: #f0fff0;
                    color: black;
                }
            """)
            self.copy_btn.setEnabled(True)
            
        except Exception as e:
            self.result_text.setPlainText(f"Error: {str(e)}")
            self.result_text.setStyleSheet("""
                QTextEdit {
                    border: 2px solid #f44336;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 11pt;
                    background-color: #fff0f0;
                    color: #cc0000;
                }
            """)
            self.copy_btn.setEnabled(False)
            
    def copy_message(self):
        """Copy decoded message to clipboard"""
        message = self.result_text.toPlainText()
        if message and not message.startswith("Error:"):
            clipboard = QApplication.clipboard()
            clipboard.setText(message)
            QMessageBox.information(self, "Copied", "Message copied to clipboard!")


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Steganography Tool")
        self.setFixedSize(500, 400)
        self.setup_ui()
        self.center_window()
        
    def setup_ui(self):
        """Setup the main window UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("Image Steganography Tool")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #333; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Description
        description = QLabel("Hide secret messages in images or extract hidden messages")
        description.setFont(QFont("Arial", 14))
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("color: #666; margin-bottom: 30px;")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Add some spacing
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(20)
        
        # Encode button
        encode_btn = QPushButton("🔒 Encode Message")
        encode_btn.setMinimumSize(300, 60)
        encode_btn.setFont(QFont("Arial", 16, QFont.Bold))
        encode_btn.clicked.connect(self.show_encode_dialog)
        encode_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        button_layout.addWidget(encode_btn, alignment=Qt.AlignCenter)
        
        # Decode button
        decode_btn = QPushButton("🔓 Decode Message")
        decode_btn.setMinimumSize(300, 60)
        decode_btn.setFont(QFont("Arial", 16, QFont.Bold))
        decode_btn.clicked.connect(self.show_decode_dialog)
        decode_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        button_layout.addWidget(decode_btn, alignment=Qt.AlignCenter)
        
        layout.addLayout(button_layout)
        
        # Add spacing at bottom
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Footer
        footer = QLabel("Select an option above to get started")
        footer.setFont(QFont("Arial", 10))
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #888; margin-top: 20px;")
        layout.addWidget(footer)
        
        central_widget.setLayout(layout)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                background-color: #f5f5f5;
            }
        """)
        
    def center_window(self):
        """Center the window on the screen"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
        
    def show_encode_dialog(self):
        """Show the encode dialog"""
        dialog = EncodeDialog(self)
        dialog.exec_()
        
    def show_decode_dialog(self):
        """Show the decode dialog"""
        dialog = DecodeDialog(self)
        dialog.exec_()


def main():
    """Main function to run the application"""
    app = QApplication(sys.argv)
    app.setApplicationName("Image Steganography Tool")
    app.setOrganizationName("Steganography Tools")
    
    # Set application style
    app.setStyle('Fusion')  # Modern cross-platform style
    
    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting application: {e}")
        QMessageBox.critical(None, "Error", f"Failed to start application: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()