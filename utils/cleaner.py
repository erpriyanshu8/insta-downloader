import os
import time
import threading
from pathlib import Path

class FileCleaner:
    """Automatically cleans old downloaded files"""
    
    def __init__(self, downloads_dir: str, max_age_minutes: int = 30):
        self.downloads_dir = Path(downloads_dir)
        self.max_age_seconds = max_age_minutes * 60
        self.running = False
        self.thread = None
    
    def start_cleanup_thread(self):
        """Starts background cleanup thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self.thread.start()
    
    def stop_cleanup_thread(self):
        """Stops background cleanup thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _cleanup_loop(self):
        """Background loop that cleans old files"""
        while self.running:
            try:
                self.cleanup_old_files()
            except Exception as e:
                print(f"Cleanup error: {e}")
            
            # Run cleanup every 10 minutes
            time.sleep(600)
    
    def cleanup_old_files(self):
        """Removes files older than max_age"""
        current_time = time.time()
        
        # Clean single downloads
        single_dir = self.downloads_dir / 'single'
        if single_dir.exists():
            for file in single_dir.glob('*'):
                if file.is_file():
                    age = current_time - file.stat().st_mtime
                    if age > self.max_age_seconds:
                        file.unlink(missing_ok=True)
        
        # Clean profile downloads
        profiles_dir = self.downloads_dir / 'profiles'
        if profiles_dir.exists():
            for profile_dir in profiles_dir.glob('*'):
                if profile_dir.is_dir():
                    age = current_time - profile_dir.stat().st_mtime
                    if age > self.max_age_seconds:
                        self._remove_directory(profile_dir)
        
        # Clean ZIP files
        zips_dir = self.downloads_dir / 'zips'
        if zips_dir.exists():
            for zip_file in zips_dir.glob('*.zip'):
                if zip_file.is_file():
                    age = current_time - zip_file.stat().st_mtime
                    if age > self.max_age_seconds:
                        zip_file.unlink(missing_ok=True)
    
    def _remove_directory(self, directory: Path):
        """Recursively removes directory"""
        try:
            for item in directory.iterdir():
                if item.is_dir():
                    self._remove_directory(item)
                else:
                    item.unlink(missing_ok=True)
            directory.rmdir()
        except Exception:
            pass
