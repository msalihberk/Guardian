# Guardian

Guardian is a modern, stylish, and simple antivirus application built with Python and PySide6. It allows you to scan files for known malware by comparing their SHA256 hashes against a local database.

## Features
- Beautiful and modern dark-themed user interface
- Fast file scanning with progress indicator (progress updates every 5%)
- Uses a separate thread (QThread) for scanning to keep the UI responsive
- Alerts you if a file is detected as malicious
- Easy file selection and scanning
- **Report Virus**: You can report a file as a virus, which adds its hash to a local JSON and the database
- **Add to Whitelist**: You can add a file to the whitelist, removing its hash from the reported list and database

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
2. Click **Select File** to choose a file you want to scan.
3. Click **Scan** to start scanning. The progress will update every 5% and the result will be displayed in the interface.
4. To report a file as a virus, click **Report** after selecting a file. Confirm the dialog to add its hash to the database and report list.
5. To add a file to the whitelist, click **Whitelist** after selecting a file. This will remove its hash from the reported list and database if present.

## Build
1. Build with pyinstaller:
   ```bash
   pyinstaller Guardian.py --noconsole --icon Images/icon.ico
   ```
2. Copy the Database folder to the app directory.

## How it works
- The selected file's SHA256 hash is calculated.
- The hash is compared line by line with the hashes in `Database/full_sha256.txt`.
- If a match is found, the file is flagged as a virus.
- All scanning is done in a background thread (QThread) for a smooth user experience.
- Progress is only updated every 5% to keep the UI fast and responsive, even with large databases.
- When you report a virus, its hash is added to `Database/saves.json` and the main database.
- When you add to whitelist, the hash is removed from the reported list and the main database.

## Customization
- You can update the hash database by replacing `Database/full_sha256.txt` with your own list of SHA256 hashes.
- The UI can be further customized in `Guardian.py` inside the `Ui_MainWindow` class.
- Threading and progress logic can be found in the `HashCheckThread` class in `Guardian.py`.

## License
This project is for educational purposes. Use at your own risk.

---
Made with ❤️ using Python and PySide6.
