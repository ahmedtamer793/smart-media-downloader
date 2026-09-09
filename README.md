# ⚡ Smart Media Downloader (v2.0)

A high-performance, modern cross-platform desktop application to download videos and extract audio from **YouTube, Spotify, Instagram, Facebook, TikTok, and 1800+ sites**, including direct streaming CDNs.

Built with **Python**, **CustomTkinter**, **yt-dlp**, and **FFmpeg**.

---

## ✨ Features

* **⚡ Ultra-Fast YouTube Fetching:** Uses lightweight endpoints for near-instant title and metadata discovery (sub-second response).
* **🎵 Spotify Support:** Direct Spotify track resolution that searches and extracts high-bitrate MP3s (up to 320 kbps) automatically.
* **📱 WhatsApp & Mobile Compatibility:** Automatically converts video streams with `H.264` codec, `yuv420p` pixel format, and even dimensions to fix "File format not supported" errors on WhatsApp and older media players.
* **🛡️ Single Media Enforcement:** Strips radio and playlist parameters automatically to prevent accidental bulk downloads when copying links.
* **🎬 Generic & CDN Stream Support:** Directly handles `.mp4` URLs and `.m3u8` video streams from external streaming platforms.
* **🎨 Modern UI:** Sleek Dark Mode interface with real-time speed, ETA, and progress tracking.

---

## 📥 Download (Standalone Executable)

No Python or FFmpeg installation required!

1. Go to the [Releases](https://github.com/ahmedtamer793/smart-media-downloader/releases) tab.
2. Download the latest `app.exe` (v2.0.0).
3. Run the executable directly.

---

## 🛠️ Run from Source

### Prerequisites
* Python 3.10+
* Virtual Environment (recommended)

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/ahmedtamer793/smart-media-downloader.git](https://github.com/ahmedtamer793/smart-media-downloader.git)
   cd smart-media-downloader
Create and activate a virtual environment:

Bash
# Windows
python -m venv venv
venv\Scripts\activate
Install dependencies:

Bash
pip install customtkinter yt-dlp imageio-ffmpeg
Run the application:

Bash
python app.py
📦 Building the Executable
To bundle the application into a standalone, single .exe file containing all dependencies and the embedded FFmpeg binary:

Bash
pyinstaller --noconfirm --onefile --windowed --collect-all customtkinter --collect-all imageio_ffmpeg app.py
The output binary will be located in the dist/ directory (~50MB+).

📄 License
This project is open-source and available under the MIT License.
