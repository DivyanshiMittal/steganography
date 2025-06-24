🖼️ Image Steganography Tool (PyQt5)
A simple yet powerful desktop application to hide secret text inside images using steganography techniques. Built with Python and PyQt5, this tool allows secure and discreet communication by embedding hidden messages within image files.

📦 Features
✅ Hide secret text inside images (Encoding)
✅ Extract hidden text from images (Decoding)
✅ User-friendly graphical interface using PyQt5
✅ Cross-platform support (Windows, Linux, Mac)
✅ No noticeable changes in image appearance

🔧 Technologies Used
Python 3

PyQt5 (GUI development)

PIL (Pillow) for image processing

Steganography Algorithm: Least Significant Bit (LSB) manipulation

🚀 Installation
Clone the repository:

bash
Copy
Edit
git clone https://github.com/your-username/image-steganography-tool.git
cd image-steganography-tool
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
If requirements.txt is not present, manually install:

bash
Copy
Edit
pip install PyQt5 Pillow
Run the application:

bash
Copy
Edit
python main.py
🛠️ How It Works
➤ Encoding Process
Select the image file using the GUI.

Enter the secret message to hide.

The tool embeds the message into the image pixels using LSB technique.

The modified image with hidden message is saved.

➤ Decoding Process
Select the image containing the hidden message.

The tool extracts the hidden message by analyzing pixel data.

The hidden text is displayed.

📷 Screenshots
(You can add screenshots here after running the tool and taking snapshots.)

🎯 Future Enhancements
Support for hiding other file types (audio, documents)

Integration with encryption for added security

Mobile version (Android/iOS)

Enhanced robustness against image compression

📄 License
This project is open-source and available under the MIT License.

🤝 Acknowledgements
PyQt5 Documentation

Pillow Documentation

Wikipedia - Steganography

Feel free to fork, contribute, and improve this project!
