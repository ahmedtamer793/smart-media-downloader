# 🚀 Smart Media Downloader (YT & FB)

A fast, lightweight, and modern desktop application to download videos and extract audio from **YouTube** and **Facebook** with custom quality options and full Windows audio compatibility.

Built using **Python**, **CustomTkinter**, and **yt-dlp**.

---

## ✨ Features

- **Multi-Platform Support:** Seamless downloading from both YouTube and Facebook.
- **Flexible Quality Selection:**
  - **Video (MP4):** Full stream resolutions (from 144p up to 4K / 60fps) with an intelligent automatic best-quality fallback.
  - **Audio (MP3):** Multi-bitrate extraction ranging from ultra-saver (64 kbps) to studio quality (320 kbps).
- **Windows Audio Compatibility:** Enforces standard **AAC** audio re-encoding during merge operations, preventing unsupported format playback issues (such as Opus in native Windows players).
- **Non-Blocking Multithreaded UI:** Real-time download progress, dynamic speed tracking, and responsive controls without UI freezing.
- **Filesystem Sanitization:** Automatically sanitizes file titles against invalid Windows naming characters (`\ / : * ? " < > |`) and newlines.
- **Standalone Binary:** Can be run directly without pre-installing Python or external dependencies.

---

## 🛠️ Tech Stack

- **GUI Framework:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Modern Dark Theme)
- **Engine:** [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- **Audio/Video Processing:** [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) & FFmpeg
- **Distribution:** [PyInstaller](https://pyinstaller.org/)

---

## 📦 Installation & Setup

### Option 1: Run Pre-built Executable
Download the latest standalone executable (`app.exe`) directly from the **[Releases](../../releases)** tab and run it with a double-click.

### Option 2: Run from Source Code

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/ahmedtamer793/smart-media-downloader.git](https://github.com/ahmedtamer793/smart-media-downloader.git)
   cd smart-media-downloader
Create and activate a virtual environment (recommended):

Bash
python -m venv venv
# On Windows:
venv\Scripts\activate
Install dependencies:

Bash
pip install -r requirements.txt
Launch the app:

Bash
python app.py
🔨 Packaging as Standalone (.exe)
To bundle the application into a single executable binary:

Bash
pip install pyinstaller
pyinstaller --noconsole --onefile --collect-all customtkinter --collect-all imageio_ffmpeg app.py
The output executable will be generated inside the dist/ directory.

📄 License
This project is licensed under the MIT License - feel free to modify and distribute.
