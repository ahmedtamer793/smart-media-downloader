import os
import re
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

        self.title("Media Downloader | YouTube & Facebook")
        self.geometry("680x670")
        self.resizable(False, False)

        self.video_info = None
        self.available_video_formats = []
        self.audio_formats = [
            {"label": "Ultra Saver (64 kbps - Smallest File)", "value": "64"},
            {"label": "Standard Quality (128 kbps - Balanced)", "value": "128"},
            {"label": "High Quality (192 kbps - Recommended)", "value": "192"},
            {"label": "Very High Quality (256 kbps - Clear Audio)", "value": "256"},
            {"label": "Maximum Quality (320 kbps - Studio Quality)", "value": "320"}
        ]
        
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

        self.setup_ui()

    def setup_ui(self):
        self.lbl_header = ctk.CTkLabel(
            self, 
            text="🚀 Smart Media Downloader (YT & FB)", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.lbl_header.pack(pady=15)

        # URL Input
        self.frm_url = ctk.CTkFrame(self)
        self.frm_url.pack(padx=20, pady=10, fill="x")

        self.ent_url = ctk.CTkEntry(
            self.frm_url, 
            placeholder_text="Paste YouTube or Facebook video link here...",
            height=40
        )
        self.ent_url.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)

        self.btn_fetch = ctk.CTkButton(
            self.frm_url, 
            text="🔍 Fetch Info", 
            width=110, 
            height=40,
            command=self.start_fetch_info_thread
        )
        self.btn_fetch.pack(side="right", padx=(5, 10), pady=10)

        # Title Label
        self.lbl_title = ctk.CTkLabel(
            self, 
            text="Title: No video inspected yet", 
            wraplength=640, 
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="gray"
        )
        self.lbl_title.pack(pady=5)

        # Media Type Selection
        self.frm_type = ctk.CTkFrame(self)
        self.frm_type.pack(padx=20, pady=10, fill="x")

        self.lbl_type = ctk.CTkLabel(self.frm_type, text="Format:", font=ctk.CTkFont(weight="bold"))
        self.lbl_type.pack(side="left", padx=15, pady=10)

        self.media_type_var = ctk.StringVar(value="MP4")
        self.rb_mp4 = ctk.CTkRadioButton(
            self.frm_type, 
            text="Video & Audio (MP4)", 
            variable=self.media_type_var, 
            value="MP4",
            command=self.update_quality_dropdown
        )
        self.rb_mp4.pack(side="left", padx=15)

        self.rb_mp3 = ctk.CTkRadioButton(
            self.frm_type, 
            text="Audio Only (MP3)", 
            variable=self.media_type_var, 
            value="MP3",
            command=self.update_quality_dropdown
        )
        self.rb_mp3.pack(side="left", padx=15)

        # Quality Selection
        self.frm_quality = ctk.CTkFrame(self)
        self.frm_quality.pack(padx=20, pady=10, fill="x")

        self.lbl_quality = ctk.CTkLabel(self.frm_quality, text="Quality & Size:", font=ctk.CTkFont(weight="bold"))
        self.lbl_quality.pack(side="left", padx=15, pady=15)

        self.cmb_quality = ctk.CTkComboBox(
            self.frm_quality, 
            values=["Fetch video first to see formats"], 
            width=420,
            state="disabled"
        )
        self.cmb_quality.pack(side="right", padx=15, pady=15)

        # Save Location
        self.frm_save = ctk.CTkFrame(self)
        self.frm_save.pack(padx=20, pady=10, fill="x")

        self.lbl_save = ctk.CTkLabel(self.frm_save, text="Save To:", font=ctk.CTkFont(weight="bold"))
        self.lbl_save.pack(side="left", padx=15, pady=10)

        self.ent_save_path = ctk.CTkEntry(self.frm_save, height=35)
        self.ent_save_path.pack(side="left", fill="x", expand=True, padx=5, pady=10)
        self.ent_save_path.insert(0, self.download_path)

        self.btn_browse = ctk.CTkButton(
            self.frm_save, 
            text="Browse...", 
            width=90, 
            height=35,
            command=self.browse_save_folder
        )
        self.btn_browse.pack(side="right", padx=(5, 15), pady=10)

        # Progress Bar & Status
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(padx=20, pady=(15, 5), fill="x")
        self.progress_bar.set(0)

        self.lbl_status = ctk.CTkLabel(self, text="Ready", font=ctk.CTkFont(size=12))
        self.lbl_status.pack(pady=5)

        # Download Button
        self.btn_download = ctk.CTkButton(
            self, 
            text="⬇️ Start Download", 
            height=45, 
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#28a745", 
            hover_color="#218838",
            command=self.start_download_thread,
            state="disabled"
        )
        self.btn_download.pack(padx=20, pady=15, fill="x")

    def browse_save_folder(self):
        chosen_dir = filedialog.askdirectory(initialdir=self.download_path)
        if chosen_dir:
            self.download_path = chosen_dir
            self.ent_save_path.delete(0, "end")
            self.ent_save_path.insert(0, chosen_dir)

    def detect_platform(self, url):
        if "youtube.com" in url or "youtu.be" in url:
            return "YouTube"
        elif "facebook.com" in url or "fb.watch" in url:
            return "Facebook"
        return "Unknown"

    def format_size(self, bytes_val):
        if not bytes_val or bytes_val <= 0:
            return "Unknown size"
        mb = bytes_val / (1024 * 1024)
        return f"{mb:.1f} MB"

    def sanitize_filename(self, name):
        clean_name = name.replace("\n", " ").replace("\r", " ")
        clean_name = re.sub(r'[\\/*?:"<>|]', "", clean_name)
        return clean_name.strip()[:100]

    def start_fetch_info_thread(self):
        url = self.ent_url.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a valid link first!")
            return

        platform = self.detect_platform(url)
        if platform == "Unknown":
            messagebox.showerror("Error", "Unsupported platform. Please provide a YouTube or Facebook link.")
            return

        self.btn_fetch.configure(state="disabled")
        self.btn_download.configure(state="disabled")
        self.lbl_status.configure(text=f"Fetching metadata from {platform}...")
        self.progress_bar.start()

        threading.Thread(target=self.fetch_info, args=(url,), daemon=True).start()

    def fetch_info(self, url):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': self.ffmpeg_path
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.video_info = ydl.extract_info(url, download=False)
            
            self.process_formats(self.video_info)
            self.after(0, self.on_fetch_success)
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self.on_fetch_error(error_msg))

    def process_formats(self, info):
        formats = info.get('formats', [])
        
        best_audio_size = 0
        audio_streams = [f for f in formats if f.get('vcodec') == 'none' and f.get('acodec') != 'none']
        if audio_streams:
            best_audio = max(audio_streams, key=lambda x: x.get('abr') or 0)
            best_audio_size = best_audio.get('filesize') or best_audio.get('filesize_approx') or 0

        self.available_video_formats = []
        seen_res = set()

        for f in reversed(formats):
            vcodec = f.get('vcodec')
            height = f.get('height')
            format_id = f.get('format_id')

            if vcodec != 'none' and height:
                res_label = f"{height}p"
                if res_label not in seen_res:
                    seen_res.add(res_label)
                    
                    video_size = f.get('filesize') or f.get('filesize_approx') or 0
                    
                    if f.get('acodec') == 'none' and best_audio_size:
                        total_bytes = video_size + best_audio_size if video_size else 0
                    else:
                        total_bytes = video_size

                    size_str = self.format_size(total_bytes)
                    fps_str = f" @ {f.get('fps')}fps" if f.get('fps') and f.get('fps') > 30 else ""
                    display_text = f"Resolution: {res_label}{fps_str} | Est. Download: {size_str}"

                    self.available_video_formats.append({
                        'label': display_text,
                        'format_id': format_id,
                        'height': height,
                        'is_dash': f.get('acodec') == 'none'
                    })

        self.available_video_formats.sort(key=lambda x: x['height'], reverse=True)

    def on_fetch_success(self):
        self.progress_bar.stop()
        self.progress_bar.set(0)
        self.btn_fetch.configure(state="normal")
        self.btn_download.configure(state="normal")
        
        title = self.video_info.get('title', 'Unknown Title')
        self.lbl_title.configure(text=f"📌 {title}", text_color="white")
        self.lbl_status.configure(text="✅ Info retrieved successfully! Select quality and download.")
        
        self.update_quality_dropdown()

    def on_fetch_error(self, error_msg):
        self.progress_bar.stop()
        self.progress_bar.set(0)
        self.btn_fetch.configure(state="normal")
        self.lbl_status.configure(text="❌ Failed to fetch info.")
        
        if "Private video" in error_msg or "login" in error_msg.lower():
            messagebox.showerror("Error", "This video is private, restricted, or requires login.")
        else:
            messagebox.showerror("Fetch Error", f"Unable to retrieve video info:\n{error_msg[:150]}")

    def update_quality_dropdown(self):
        if not self.video_info:
            return

        media_type = self.media_type_var.get()
        if media_type == "MP4":
            options = ["Best Available Quality (Auto Highest)"]
            if self.available_video_formats:
                options.extend([item['label'] for item in self.available_video_formats])
        else:
            options = [item['label'] for item in self.audio_formats]

        self.cmb_quality.configure(state="normal", values=options)
        self.cmb_quality.set(options[0])

    def start_download_thread(self):
        url = self.ent_url.get().strip()
        media_type = self.media_type_var.get()
        selected_option = self.cmb_quality.get()
        target_folder = self.ent_save_path.get().strip()

        if not os.path.exists(target_folder):
            try:
                os.makedirs(target_folder, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Invalid save folder:\n{e}")
                return

        self.btn_download.configure(state="disabled")
        self.btn_fetch.configure(state="disabled")
        self.progress_bar.set(0)
        self.lbl_status.configure(text="⏳ Initializing download...")

        threading.Thread(
            target=self.download_media, 
            args=(url, media_type, selected_option, target_folder), 
            daemon=True
        ).start()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total_bytes:
                percent = downloaded / total_bytes
                self.progress_bar.set(percent)
                speed = d.get('speed') or 0
                speed_mb = speed / (1024 * 1024) if speed else 0
                self.lbl_status.configure(text=f"Downloading: {percent*100:.1f}% | Speed: {speed_mb:.1f} MB/s")
        elif d['status'] == 'finished':
            self.lbl_status.configure(text="⚙️ Merging & converting media...")

    def download_media(self, url, media_type, selected_option, target_folder):
        try:
            raw_title = self.video_info.get('title', 'media_file') if self.video_info else 'media_file'
            safe_title = self.sanitize_filename(raw_title)

            common_opts = {
                'outtmpl': os.path.join(target_folder, f'{safe_title}.%(ext)s'),
                'windowsfilenames': True,
                'restrictfilenames': False,
                'ffmpeg_location': self.ffmpeg_path,
                'progress_hooks': [self.progress_hook],
            }

            if media_type == "MP3":
                bitrate = "192"
                for item in self.audio_formats:
                    if item['label'] == selected_option:
                        bitrate = item['value']
                        break

                ydl_opts = {
                    **common_opts,
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': bitrate,
                    }],
                }
            else:
                if selected_option.startswith("Best Available"):
                    format_id = 'bestvideo+bestaudio/best'
                else:
                    format_id = 'bestvideo+bestaudio/best'
                    for item in self.available_video_formats:
                        if item['label'] == selected_option:
                            if item['is_dash']:
                                format_id = f"{item['format_id']}+bestaudio/best"
                            else:
                                format_id = item['format_id']
                            break

                ydl_opts = {
                    **common_opts,
                    'format': format_id,
                    'merge_output_format': 'mp4',
                    'postprocessor_args': ['-c:a', 'aac'],
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.after(0, lambda: self.on_download_success(target_folder))
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self.on_download_error(error_msg))

    def on_download_success(self, target_folder):
        self.progress_bar.set(1.0)
        self.lbl_status.configure(text="✅ Download completed successfully!")
        self.btn_download.configure(state="normal")
        self.btn_fetch.configure(state="normal")
        messagebox.showinfo("Success", f"File saved successfully in:\n{target_folder}")

    def on_download_error(self, error_msg):
        self.lbl_status.configure(text="❌ Download failed.")
        self.btn_download.configure(state="normal")
        self.btn_fetch.configure(state="normal")
        messagebox.showerror("Download Error", f"Error occurred during download:\n{error_msg[:150]}")

if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()