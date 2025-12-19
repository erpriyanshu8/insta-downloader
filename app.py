import os
import time
import uuid
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.exceptions import RequestEntityTooLarge
from utils.validators import InputValidator
from utils.downloader import InstagramDownloader
from utils.zipper import ZipCreator
from utils.rate_limiter import RateLimiter
from utils.cleaner import FileCleaner

# Flask app factory
def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
    
    # Initialize directories
    base_dir = Path(__file__).parent
    downloads_dir = base_dir / 'downloads'
    (downloads_dir / 'single').mkdir(parents=True, exist_ok=True)
    (downloads_dir / 'profiles').mkdir(parents=True, exist_ok=True)
    (downloads_dir / 'zips').mkdir(parents=True, exist_ok=True)
    
    # Initialize utilities
    validator = InputValidator()
    downloader = InstagramDownloader(str(downloads_dir))
    zipper = ZipCreator()
    rate_limiter = RateLimiter(max_requests=20, window_seconds=60)
    cleaner = FileCleaner(str(downloads_dir), max_age_minutes=30)
    
    # Start background cleaner
    cleaner.start_cleanup_thread()
    
    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')
    
    @app.route('/download', methods=['POST'])
    def download():
        try:
            # Rate limiting
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if not rate_limiter.allow_request(client_ip):
                return jsonify({
                    'success': False,
                    'error': 'Rate limit exceeded. Please wait before trying again.'
                }), 429
            
            # Get and validate input
            data = request.get_json()
            if not data or 'url' not in data:
                return jsonify({
                    'success': False,
                    'error': 'No input provided'
                }), 400
            
            user_input = data['url'].strip()
            
            # Validate and detect input type
            is_valid, error_msg = validator.validate_input(user_input)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 400
            
            input_type = validator.detect_input_type(user_input)
            sanitized_input = validator.sanitize_input(user_input)
            
            # Process based on input type
            if input_type == 'post':
                # Single post download
                result = downloader.download_single_post(sanitized_input)
                
                if not result['success']:
                    return jsonify({
                        'success': False,
                        'error': result['error']
                    }), 400
                
                return jsonify({
                    'success': True,
                    'type': 'single',
                    'caption': result.get('caption', ''),
                    'video_url': f"/serve/{result['filename']}",
                    'filename': result['filename'],
                    'message': 'Download ready!'
                })
            
            elif input_type == 'profile':
                # Profile bulk download
                result = downloader.download_profile(sanitized_input)
                
                if not result['success']:
                    return jsonify({
                        'success': False,
                        'error': result['error']
                    }), 400
                
                # Create ZIP file
                zip_result = zipper.create_profile_zip(
                    result['download_path'],
                    result['username']
                )
                
                if not zip_result['success']:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to create ZIP file'
                    }), 500
                
                return jsonify({
                    'success': True,
                    'type': 'profile',
                    'zip_url': f"/serve/{zip_result['filename']}",
                    'filename': zip_result['filename'],
                    'post_count': result.get('post_count', 0),
                    'message': f'Downloaded {result.get("post_count", 0)} posts!'
                })
            
            else:
                return jsonify({
                    'success': False,
                    'error': 'Invalid input type'
                }), 400
                
        except RequestEntityTooLarge:
            return jsonify({
                'success': False,
                'error': 'Request too large'
            }), 413
            
        except Exception as e:
            app.logger.error(f'Unexpected error: {str(e)}')
            return jsonify({
                'success': False,
                'error': 'An unexpected error occurred. Please try again.'
            }), 500
    
    @app.route('/serve/<filename>', methods=['GET'])
    def serve_file(filename):
        try:
            # Sanitize filename to prevent directory traversal
            safe_filename = Path(filename).name
            
            # Check in single downloads
            single_path = downloads_dir / 'single' / safe_filename
            if single_path.exists() and single_path.is_file():
                return send_file(
                    single_path,
                    as_attachment=True,
                    download_name=safe_filename
                )
            
            # Check in zips
            zip_path = downloads_dir / 'zips' / safe_filename
            if zip_path.exists() and zip_path.is_file():
                return send_file(
                    zip_path,
                    as_attachment=True,
                    download_name=safe_filename
                )
            
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
            
        except Exception as e:
            app.logger.error(f'File serve error: {str(e)}')
            return jsonify({
                'success': False,
                'error': 'Error serving file'
            }), 500
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': int(time.time())
        })
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
