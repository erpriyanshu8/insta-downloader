import os
import time
import uuid
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(24).hex()
    
    base_dir = Path(__file__).parent
    downloads_dir = base_dir / 'downloads'
    (downloads_dir / 'single').mkdir(parents=True, exist_ok=True)
    (downloads_dir / 'profiles').mkdir(parents=True, exist_ok=True)
    (downloads_dir / 'zips').mkdir(parents=True, exist_ok=True)
    
    # Import here to avoid startup errors
    try:
        import instaloader
        loader = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        INSTALOADER_AVAILABLE = True
    except:
        INSTALOADER_AVAILABLE = False
        loader = None
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/download', methods=['POST'])
    def download():
        if not INSTALOADER_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Instagram downloader is not available. Please contact support.'
            }), 500
        
        try:
            data = request.get_json()
            if not data or 'url' not in data:
                return jsonify({'success': False, 'error': 'No URL provided'}), 400
            
            url = data['url'].strip()
            
            # Extract shortcode
            import re
            patterns = [r'/p/([A-Za-z0-9_-]+)', r'/reel/([A-Za-z0-9_-]+)', r'/tv/([A-Za-z0-9_-]+)']
            shortcode = None
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    shortcode = match.group(1)
                    break
            
            if not shortcode:
                return jsonify({'success': False, 'error': 'Invalid Instagram URL'}), 400
            
            # Download post
            post = instaloader.Post.from_shortcode(loader.context, shortcode)
            
            if not post.is_video:
                return jsonify({'success': False, 'error': 'This post does not contain a video'}), 400
            
            uid = uuid.uuid4().hex[:8]
            username = post.owner_username
            filename = username + '_' + shortcode + '_' + uid + '.mp4'
            filepath = downloads_dir / 'single' / filename
            
            # Download with timeout
            loader.download_post(post, target=str(filepath.parent / uid))
            
            # Find downloaded video
            files = list(filepath.parent.glob(uid + '*.mp4'))
            if files:
                files[0].rename(filepath)
                
                # Cleanup
                for f in filepath.parent.glob(uid + '*'):
                    if f != filepath:
                        try:
                            f.unlink()
                        except:
                            pass
                
                caption = ''
                try:
                    caption = post.caption if post.caption else ''
                except:
                    pass
                
                return jsonify({
                    'success': True,
                    'type': 'single',
                    'caption': caption,
                    'video_url': '/serve/' + filename,
                    'filename': filename,
                    'message': 'Download ready!'
                })
            
            return jsonify({'success': False, 'error': 'Failed to download video'}), 500
            
        except Exception as e:
            return jsonify({'success': False, 'error': 'Error: ' + str(e)}), 500
    
    @app.route('/serve/<filename>')
    def serve_file(filename):
        try:
            safe_filename = Path(filename).name
            filepath = downloads_dir / 'single' / safe_filename
            
            if filepath.exists() and filepath.is_file():
                return send_file(filepath, as_attachment=True, download_name=safe_filename)
            
            return jsonify({'error': 'File not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'instaloader': INSTALOADER_AVAILABLE,
            'timestamp': int(time.time())
        })
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
