import os
import time
import uuid
from pathlib import Path
import instaloader

class InstagramDownloader:
    def __init__(self, downloads_dir):
        self.downloads_dir = Path(downloads_dir)
        self.loader = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            post_metadata_txt_pattern='',
            max_connection_attempts=3
        )
        self.loader.context.sleep = True
        self.loader.context.max_connection_attempts = 3
    
    def download_single_post(self, post_input):
        try:
            shortcode = self._extract_shortcode(post_input)
            if not shortcode:
                return {'success': False, 'error': 'Invalid post URL'}
            
            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
            
            if not post.is_video:
                return {'success': False, 'error': 'This post does not contain a video'}
            
            unique_id = uuid.uuid4().hex[:8]
            filename = post.owner_username + '_' + shortcode + '_' + unique_id + '.mp4'
            filepath = self.downloads_dir / 'single' / filename
            
            self.loader.download_post(post, target=str(filepath.parent / unique_id))
            
            downloaded_files = list((filepath.parent).glob(unique_id + '*.mp4'))
            if downloaded_files:
                downloaded_files[0].rename(filepath)
                
                for f in (filepath.parent).glob(unique_id + '*'):
                    if f != filepath:
                        f.unlink(missing_ok=True)
                
                return {
                    'success': True,
                    'filename': filename,
                    'caption': post.caption if post.caption else ''
                }
            
            return {'success': False, 'error': 'Failed to download video'}
            
        except instaloader.exceptions.InstaloaderException as e:
            return {'success': False, 'error': 'Instagram error: ' + str(e)}
        except Exception as e:
            return {'success': False, 'error': 'Download failed: ' + str(e)}
    
    def download_profile(self, username):
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            if profile.is_private:
                return {'success': False, 'error': 'This profile is private. Only public profiles are supported.'}
            
            unique_id = uuid.uuid4().hex[:8]
            download_path = self.downloads_dir / 'profiles' / (username + '_' + unique_id)
            download_path.mkdir(parents=True, exist_ok=True)
            
            post_count = 0
            captions_data = []
            
            for post in profile.get_posts():
                if post.is_video:
                    try:
                        time.sleep(2)
                        
                        shortcode = post.shortcode
                        target = download_path / shortcode
                        
                        self.loader.download_post(post, target=str(target))
                        
                        caption = post.caption if post.caption else ''
                        video_files = list(download_path.glob(shortcode + '*.mp4'))
                        if video_files:
                            captions_data.append({
                                'file': video_files[0].name,
                                'caption': caption
                            })
                        
                        post_count += 1
                        
                        if post_count >= 50:
                            break
                            
                    except Exception:
                        continue
            
            if post_count == 0:
                return {'success': False, 'error': 'No public videos found on this profile'}
            
            captions_file = download_path / 'captions.txt'
            with open(captions_file, 'w', encoding='utf-8') as f:
                for item in captions_data:
                    f.write('File: ' + item['file'] + '
')
                    f.write('Caption: ' + item['caption'] + '
')
                    f.write('-' * 80 + '

')
            
            for f in download_path.rglob('*.json*'):
                f.unlink(missing_ok=True)
            for f in download_path.rglob('*.txt'):
                if f.name != 'captions.txt':
                    f.unlink(missing_ok=True)
            for f in download_path.rglob('*.jpg'):
                f.unlink(missing_ok=True)
            
            return {
                'success': True,
                'download_path': str(download_path),
                'username': username,
                'post_count': post_count
            }
            
        except instaloader.exceptions.ProfileNotExistsException:
            return {'success': False, 'error': 'Profile not found'}
        except instaloader.exceptions.InstaloaderException as e:
            return {'success': False, 'error': 'Instagram error: ' + str(e)}
        except Exception as e:
            return {'success': False, 'error': 'Download failed: ' + str(e)}
    
    def _extract_shortcode(self, url):
        import re
        patterns = [
            r'/p/([A-Za-z0-9_-]+)',
            r'/reel/([A-Za-z0-9_-]+)',
            r'/tv/([A-Za-z0-9_-]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
