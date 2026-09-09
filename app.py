import os
import re
import json
import urllib.request
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
import yt_dlp
import imageio_ffmpeg

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Universal Media Downloader (v2.0)")
        self.geometry("680x700")
        self.resizable(False, False)

        self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        self.download_path = None

        self.setup_ui()

    def setup_ui(self):
        # Header
        self.title_label = ctk.CTkLabel(
            self, 
            text="Universal Media Downloader", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_label.pack(pady=(15, 5))

        self.sub_label = ctk.CTkLabel(
            self, 
            text="Fast download from YouTube, Spotify, Facebook, X, TikTok, and 1800+ sites", 
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.sub_label.pack(pady=(0, 10))

        # URL Frame
        self.url_frame = ctk.CTkFrame(self)
        self.url_frame.pack(fill="x", padx=25, pady=5)

        self.url_entry = ctk.CTkEntry(
            self.url_frame, 
            placeholder_text="Paste your link here...", 
            height=40
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)

        self.fetch_btn = ctk.CTkButton(
            self.url_frame, 
            text="Fetch Info", 
            width=100, 
            height=40, 
            command=self.start_fetch_info
        )
        self.fetch_btn.pack(side="right", padx=(5, 10), pady=10)

        # Info Frame
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(fill="x", padx=25, pady=10)

        self.info_title = ctk.CTkLabel(
            self.info_frame, 
            text="Title: Waiting for URL...", 
            anchor="w", 
            wraplength=620,
            justify="left",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.info_title.pack(fill="x", padx=15, pady=(10, 5))

        self.info_platform = ctk.CTkLabel(
            self.info_frame, 
            text="Platform: -", 
            anchor="w", 
            text_color="gray"
        )
        self.info_platform.pack(fill="x", padx=15, pady=(0, 10))

        # Media Type Frame
        self.type_frame = ctk.CTkFrame(self)
        self.type_frame.pack(fill="x", padx=25, pady=10)

        self.type_label = ctk.CTkLabel(self.type_frame, text="Format:", font=ctk.CTkFont(size=14, weight="bold"))
        self.type_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.media_type_var = ctk.StringVar(value="video")
        self.video_radio = ctk.CTkRadioButton(
            self.type_frame, 
            text="Video (MP4)", 
            variable=self.media_type_var, 
            value="video", 
            command=self.update_quality_options
        )
        self.video_radio.grid(row=0, column=1, padx=15, pady=10)

        self.audio_radio = ctk.CTkRadioButton(
            self.type_frame, 
            text="Audio Only (MP3)", 
            variable=self.media_type_var, 
            value="audio", 
            command=self.update_quality_options
        )
        self.audio_radio.grid(row=0, column=2, padx=15, pady=10)

        # Quality Frame
        self.quality_frame = ctk.CTkFrame(self)
        self.quality_frame.pack(fill="x", padx=25, pady=10)

        self.quality_label = ctk.CTkLabel(self.quality_frame, text="Quality:", font=ctk.CTkFont(size=14, weight="bold"))
        self.quality_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.quality_menu = ctk.CTkOptionMenu(
            self.quality_frame, 
            values=["Best Available (Up to 1080p)", "1080p (Full HD)", "720p (HD)", "480p (SD)", "360p (Low)"], 
            width=290
        )
        self.quality_menu.grid(row=0, column=1, padx=15, pady=10, sticky="w")

        # Save Path Frame
        self.path_frame = ctk.CTkFrame(self)
        self.path_frame.pack(fill="x", padx=25, pady=10)

        self.path_label = ctk.CTkLabel(
            self.path_frame, 
            text="Save Location: Please select an output folder", 
            anchor="w", 
            text_color="#e5a50a",
            wraplength=480
        )
        self.path_label.pack(side="left", padx=15, pady=10, expand=True, fill="x")

        self.browse_btn = ctk.CTkButton(
            self.path_frame, 
            text="Browse", 
            width=100, 
            command=self.browse_path
        )
        self.browse_btn.pack(side="right", padx=15, pady=10)

        # Progress & Status Frame
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(fill="x", padx=25, pady=(15, 5))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self, text="Ready", text_color="gray", font=ctk.CTkFont(size=13))
        self.status_label.pack(pady=(0, 10))

        # Download Button
        self.download_btn = ctk.CTkButton(
            self, 
            text="Start Download", 
            height=45, 
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.start_download
        )
        self.download_btn.pack(fill="x", padx=25, pady=(5, 15))

    def browse_path(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.download_path = folder
            self.path_label.configure(
                text=f"Save Location: {self.download_path}", 
                text_color="white"
            )

    def is_youtube_url(self, url):
        return bool(re.search(r'(youtube\.com|youtu\.be)', url))

    def is_spotify_url(self, url):
        return bool(re.search(r'spotify\.com/(?:[a-zA-Z-]+/)?track/', url))

    def get_spotify_track_info(self, url):
        try:
            match = re.search(r'(https?://open\.spotify\.com/(?:[a-zA-Z-]+/)?track/[a-zA-Z0-9]+)', url)
            clean_track_url = match.group(1) if match else url
            oembed_url = f"https://open.spotify.com/oembed?url={clean_track_url}"
            req = urllib.request.Request(oembed_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                title = data.get('title', 'Unknown Track')
                return title
        except Exception:
            return None

    def clean_url(self, url):
        # إزالة بارامترات قوائم التشغيل لمنع تحميل القائمة كاملة
        if "youtube.com/watch" in url:
            url = re.sub(r'&list=[^&]+', '', url)
            url = re.sub(r'&index=[^&]+', '', url)
            url = re.sub(r'&start_radio=[^&]+', '', url)
        return url.strip()

    def update_quality_options(self):
        m_type = self.media_type_var.get()
        if m_type == "audio":
            audio_qualities = [
                "320 kbps (Studio Quality)",
                "256 kbps (High Quality)",
                "192 kbps (Standard Quality)",
                "128 kbps (Medium Quality)",
                "64 kbps (Low Quality / Podcast)"
            ]
            self.quality_menu.configure(values=audio_qualities)
            self.quality_menu.set(audio_qualities[0])
        else:
            video_qualities = [
                "Best Available (Up to 1080p)",
                "1080p (Full HD)",
                "720p (HD)",
                "480p (SD)",
                "360p (Low)"
            ]
            self.quality_menu.configure(values=video_qualities)
            self.quality_menu.set(video_qualities[0])

    def start_fetch_info(self):
        raw_url = self.url_entry.get().strip()
        if not raw_url or not (raw_url.startswith("http://") or raw_url.startswith("https://")):
            messagebox.showwarning("Warning", "Please enter a valid URL starting with http:// or https://")
            return

        url = self.clean_url(raw_url)
        self.status_label.configure(text="Fetching details...", text_color="#3B8ED0")
        self.fetch_btn.configure(state="disabled")

        threading.Thread(target=self._fetch_info_thread, args=(url,), daemon=True).start()

    def _fetch_info_thread(self, url):
        try:
            # 1. حالة Spotify
            if self.is_spotify_url(url):
                track_info = self.get_spotify_track_info(url)
                title = track_info if track_info else "Spotify Track"
                extractor = "Spotify"
                # تفعيل الصوت تلقائياً لسبوتيفاي
                self.media_type_var.set("audio")

            # 2. حالة YouTube السريعة (oEmbed)
            elif self.is_youtube_url(url):
                try:
                    oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
                    req = urllib.request.Request(oembed_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        data = json.loads(resp.read().decode('utf-8'))
                        title = data.get('title', 'YouTube Video')
                        extractor = "YouTube"
                except Exception:
                    title = "YouTube Video"
                    extractor = "YouTube"

            # 3. باقي المنصات ومواقع الأفلام
            else:
                ydl_opts = {'quiet': True, 'skip_download': True, 'no_warnings': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False, process=False)
                    title = info.get('title', 'Unknown Media')
                    extractor = info.get('extractor_key', info.get('extractor', 'Generic'))

            self.info_title.configure(text=f"Title: {title}")
            self.info_platform.configure(text=f"Platform: {extractor}")
            self.status_label.configure(text="Ready to download", text_color="green")
            self.update_quality_options()

        except Exception as e:
            self.info_title.configure(text="Title: Ready (Manual Info)")
            self.info_platform.configure(text="Platform: Detected")
            self.status_label.configure(text="Ready to download", text_color="green")
        finally:
            self.fetch_btn.configure(state="normal")

    def clean_text(self, text):
        return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            
            speed = self.clean_text(d.get('_speed_str', 'N/A')).strip()
            eta = self.clean_text(d.get('_eta_str', 'N/A')).strip()

            if total:
                ratio = downloaded / total
                self.progress_bar.set(ratio)
                percent = int(ratio * 100)
                self.status_label.configure(
                    text=f"Downloading: {percent}%  |  Speed: {speed}  |  ETA: {eta}",
                    text_color="#3B8ED0"
                )
            else:
                self.status_label.configure(
                    text=f"Downloading... Speed: {speed}", 
                    text_color="#3B8ED0"
                )
        elif d['status'] == 'finished':
            self.progress_bar.set(1.0)
            self.status_label.configure(text="Converting audio/video via FFmpeg...", text_color="orange")

    def start_download(self):
        raw_url = self.url_entry.get().strip()
        if not raw_url:
            messagebox.showwarning("Warning", "Please enter a URL first!")
            return

        url = self.clean_url(raw_url)

        if not self.download_path:
            self.browse_path()
            if not self.download_path:
                messagebox.showwarning("Warning", "You must choose a folder before starting!")
                return

        self.download_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Starting download...", text_color="#3B8ED0")

        threading.Thread(target=self._download_thread, args=(url,), daemon=True).start()

    def _download_thread(self, url):
        m_type = self.media_type_var.get()
        selected_q = self.quality_menu.get()

        outtmpl = os.path.join(self.download_path, '%(title)s.%(ext)s')

        # لو الرابط سبوتيفاي يتم تحويل التارجت لبحث دقيق عن الصوت
        if self.is_spotify_url(url):
            track_info = self.get_spotify_track_info(url)
            search_query = track_info if track_info else "audio track"
            target_url = f"ytsearch1:{search_query} audio"
            m_type = "audio"
        else:
            target_url = url

        ydl_opts = {
            'outtmpl': outtmpl,
            'noplaylist': True,  # إيقاف تحميل القوائم وتنزيل تراك واحد فقط
            'windowsfilenames': True,
            'progress_hooks': [self.progress_hook],
            'ffmpeg_location': self.ffmpeg_path,
            'quiet': True,
            'no_warnings': True
        }

        if m_type == "audio":
            bitrate = "192"
            match = re.search(r'(\d+)\s*kbps', selected_q)
            if match:
                bitrate = match.group(1)

            # سحب مسار الصوت المباشر بدون تقطيع لتحويله فوراً لـ MP3
            ydl_opts.update({
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': bitrate,
                }]
            })
        else:
            # Video settings - Max 1080p مع إصلاح أبعاد الواتساب الزوجية وكوديك H.264
            res_match = re.search(r'(\d+)p', selected_q)
            max_res = res_match.group(1) if res_match else "1080"

            format_str = f'bestvideo[height<={max_res}]+bestaudio/best[height<={max_res}]/best'

            ydl_opts.update({
                'format': format_str,
                'merge_output_format': 'mp4',
                'postprocessor_args': {
                    'merger': [
                        '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p',
                        '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
                        '-c:a', 'aac'
                    ]
                }
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([target_url])
            self.status_label.configure(text="Completed successfully!", text_color="green")
            messagebox.showinfo("Success", f"Download finished successfully!\nSaved to:\n{self.download_path}")
        except Exception as e:
            self.status_label.configure(text="Download failed", text_color="red")
            messagebox.showerror("Download Error", f"An error occurred while downloading:\n{str(e)}")
        finally:
            self.download_btn.configure(state="normal")

if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()