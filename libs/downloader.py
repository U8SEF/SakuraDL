import os
import shutil
import subprocess
import time
from urllib.parse import urlparse

import requests

ARIA2C_PATH = "bin/aria2c.exe"

class media_downloader:
    def __init__(self):
        self.aria2c_path = self._find_aria2c()

    def _find_aria2c(self):
        candidates = [ARIA2C_PATH, shutil.which("aria2c")]
        for path in candidates:
            if path and os.path.exists(path):
                return path
        return None

    def _resolve_output_filename(self, output_title, url):
        if "%(ext)s" in output_title:
            parsed_url = urlparse(url)
            ext = os.path.splitext(parsed_url.path)[1].lower()
            if not ext:
                ext = ".mp4"
            return output_title.replace("%(ext)s", ext.lstrip("."))
        return output_title

    def _get_remote_file_size(self, url):
        try:
            response = requests.head(url, allow_redirects=True, timeout=20)
            content_length = response.headers.get("Content-Length")
            if content_length:
                return int(content_length)
        except Exception:
            pass

        try:
            response = requests.get(url, stream=True, timeout=20)
            response.close()
            content_length = response.headers.get("Content-Length")
            if content_length:
                return int(content_length)
        except Exception:
            pass

        return None

    def download(self, url, output_path="downloads", anime_name="Unknown", output_title="%(title)s.SAKURA-DL.%(ext)s"):
        if not self.aria2c_path:
            return {
                "success": False,
                "error": "aria2c not found. Put aria2c.exe in bin/ or make it available on PATH."
            }

        output_dir = os.path.join(output_path, anime_name)
        os.makedirs(output_dir, exist_ok=True)

        file_name = self._resolve_output_filename(output_title, url)
        file_path = os.path.join(output_dir, file_name)
        total_size = self._get_remote_file_size(url)
        command = [
            self.aria2c_path,
            "-q",
            "--summary-interval=0",
            "--console-log-level=error",
            "-x",
            "16",
            "-s",
            "16",
            "-k",
            "1M",
            "--max-connection-per-server=16",
            "--split=16",
            "--min-split-size=1M",
            "--continue=true",
            "--file-allocation=none",
            "--allow-overwrite=true",
            "--auto-file-renaming=false",
            "-d",
            output_dir,
            "-o",
            file_name,
            url,
        ]

        try:
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            last_line = ""
            last_size = 0
            last_update = time.time()
            total_downloaded = 0

            while True:
                if process.poll() is not None:
                    break

                if os.path.exists(file_path):
                    downloaded = os.path.getsize(file_path)
                    now = time.time()
                    if downloaded > last_size:
                        delta = downloaded - last_size
                        elapsed = max(now - last_update, 1)
                        speed = delta / elapsed / (1024 * 1024)
                        last_size = downloaded
                        last_update = now
                        total_downloaded = downloaded
                    else:
                        speed = 0.0

                    if total_size:
                        percent = min(100.0, (downloaded / total_size) * 100)
                        stalls = int(now - last_update)
                        status = "WAITING" if stalls >= 8 else "RUNNING"
                        line = f"Progress: {percent:.1f}% ({downloaded / (1024 * 1024):.1f}MB/{total_size / (1024 * 1024):.1f}MB) | Speed: {speed:.2f}MB/s | {status}"
                    else:
                        line = f"Progress: {downloaded / (1024 * 1024):.1f}MB downloaded | Speed: {speed:.2f}MB/s"

                    if line != last_line:
                        print(f"\r{line}", end="", flush=True)
                        last_line = line
                time.sleep(1)

            if last_line:
                print(f"\r{last_line}", end="\n", flush=True)

            if process.returncode != 0:
                return {
                    "success": False,
                    "error": f"Download failed with exit code {process.returncode}"
                }

            return {
                "success": True,
                "message": "Download completed successfully."
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Download failed with exit code {e.returncode}"
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "aria2c not found."
            }

