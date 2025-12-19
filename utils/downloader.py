import os
import time
import uuid
from pathlib import Path
import instaloader

class InstagramDownloader:
    """Handles Instagram content downloading"""
    
    def __init__(self, downloads_dir: str):
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
        
        # Rate limiting delays
        self.loader.context.sleep = True
        self.loader.context.max_connection_attempts = 3
    
    def download_single_post(self, post_input: str) -> dict:
        """
        Downloads a single Instagram post/reel
        Returns: dict with success, filename, caption, error
        """
        try:
            # Extract shortcode from URL
            shortcode = self._extract_shortcode(post_input)
            if not shortcode:
                return {
                    'success': False,
                    'error': 'Invalid post URL'
                }
            
            # Get post
            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
            
            # Check if it's a video
            if not post.is_video:
                return {
                    'success': False,
                    'error': 'This post does not contain a video'
                }
            
            # Generate unique filename
            unique_id = uuid.uuid4().hex[:8]
            filename = f"{post.owner_username}_{shortcode}_{unique_id}.mp4"
            filepath = self.downloads_dir / 'single' / filename
            
            # Download video
            self.loader.download_post(post, target=str(filepath.parent / unique_id))
            
            # Find downloaded video file
            downloaded_files = list((filepath.parent).glob(f"{unique_id}*.mp4"))
            if downloaded_files:
                # Rename to clean filename
                downloaded_files[0].rename(filepath)
                
                # Clean up metadata files
                for f in (filepath.parent).glob(f"{unique_id}*"):
                    if f != filepath:
                        f.unlink(missing_ok=True)
                
                return {
                    'success': True,
                    'filename': filename,
                    'caption': post.caption if post.caption else ''
                }
            
            return {
                'success': False,
                'error': 'Failed to download video'
            }
            
        except instaloader.exceptions.InstaloaderException as e:
            return {
                'success': False,
                'error': f'Instagram error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Download failed: {str(e)}'
            }
    
    def download_profile(self, username: str) -> dict:
        """
        Downloads all public videos from a profile
        Returns: dict with success, download_path, username, post_count, error
        """
        try:
            # Get profile
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            if profile.is_private:
                return {
                    'success': False,
                    'error': 'This profile is private. Only public profiles are supported.'
                }
            
            # Create unique directory for this download
            unique_id = uuid.uuid4().hex[:8]
            download_path = self.downloads_dir / 'profiles' / f"{username}_{unique_id}"
            download_path.mkdir(parents=True, exist_ok=True)
            
            # Download posts
            post_count = 0
            captions_data = []
            
            for post in profile.get_posts():
                if post.is_video:
                    try:
                        # Download with rate limiting
                        time.sleep(2)  # Respect rate limits
                        
                        shortcode = post.shortcode
                        target = download_path / shortcode
                        
                        self.loader.download_post(post, target=str(target))
                        
                        # Track caption
                        caption = post.caption if post.caption else ''
                        video_files = list(download_path.glob(f"{shortcode}*.mp4"))
                        if video_files:
                            captions_data.append({
                                'file': video_files[0].name,
                                'caption': caption
                            })
                        
                        post_count += 1
                        
                        # Limit to prevent abuse
                        if post_count >= 50:
                            break
                            
                    except Exception as e:
                        continue
            
            if post_count == 0:
                return {
                    'success': False,
                    'error': 'No public videos found on this profile'
                }
            
            # Save captions to file
            captions_file = download_path / 'captions.txt'
            with open(captions_file, 'w', encoding='utf-8') as f:
                for item in captions_data:
                    f.write(f"File: {item['file']}
")
                    f.write(f"Caption: {item['caption']}
")
                    f.write('-' * 80 + '

')
            
            # Clean up metadata files
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
            return {
                'success': False,
                'error': 'Profile not found'
            }
        except instaloader.exceptions.InstaloaderException as e:
            return {
                'success': False,
                'error': f'Instagram error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Download failed: {str(e)}'
            }
    
    def _extract_shortcode(self, url: str) -> str:
        """Extract shortcode from Instagram URL"""
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
