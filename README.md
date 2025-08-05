# Guardian

Guardian is a modern, stylish, and simple antivirus application built with Python and PySide6. It allows you to scan files for known malware by comparing their SHA256 hashes against a local database.

## Features
- Beautiful and modern dark-themed user interface
- Fast file scanning with progress indicator
- Uses a separate thread for scanning to keep the UI responsive
- Alerts you if a file is detected as malicious
- Easy file selection and scanning

## Requirements
- Python 3.8+
- All dependencies in `requirements.txt`

## Installation
1. Clone this repository or download the source code.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Make sure you have a SHA256 hash database at `Database/full_sha256.txt` (one hash per line).

## Usage
1. Run the application:
   ```bash
   python Guardian.py
   ```
2. Click **Select Location** to choose a file you want to scan.
3. Click **Scan** to start scanning. The progress and result will be displayed in the interface.

## How it works
- The selected file's SHA256 hash is calculated.
- The hash is compared line by line with the hashes in `Database/full_sha256.txt`.
- If a match is found, the file is flagged as a virus.
- All scanning is done in a background thread for a smooth user experience.

## Customization
- You can update the hash database by replacing `Database/full_sha256.txt` with your own list of SHA256 hashes.
- The UI can be further customized in `Guardian.py` inside the `Ui_MainWindow` class.

## License
This project is for educational purposes. Use at your own risk.

---
Made with ❤️ using Python and PySide6.
