#PES farmer
###This script does Pro Evolution Soccer myClub SIM matches farming

### Requirements:
To successfully use pes-farmer you will need:
- Windows 10
- [Git bash terminal installed](https://git-scm.com/downloads)
- [Python3 installed](https://www.python.org/downloads/) (this was tested on version 3.8.1)
- tesseract ocr installed (v [3.05.1](https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-setup-3.05.01.exe) from [this source](https://digi.bib.uni-mannheim.de/tesseract/) was used. instalation path should be added to PATH so `tesseract` should be callable from terminal)

### Install
1. Make sure all required applications were installed
2. Clone repository (you'll need to configure git) or download and unpack the archive:
    ```
   git pull git@github.com:MytkoEnko/PES-farming.git
    ```
3. Move to repository, create virtual environment and install script requirements (execute each line one by one in terminal):
    ```
   cd pes-farmer
   python -m venv venv
   source venv/Scripts/Activate
   pip install -r requirements.txt
    ```
### Usage:
