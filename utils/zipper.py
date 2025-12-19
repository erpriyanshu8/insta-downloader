import os
import zipfile
import uuid
from pathlib import Path

class ZipCreator:
    """Creates ZIP files for bulk downloads"""
    
    def create_profile_zip(self, source_dir: str, username: str) -> dict:
        """
        Creates a ZIP file from profile download directory
        Returns: dict with success, filename, filepath, error
        """
        try:
            source_path = Path(source_dir)
            if not source_path.exists():
                return {
                    'success': False,
                    'error': 'Source directory not found'
                }
            
            # Create ZIP in zips directory
            zips_dir = source_path.parent.parent / 'zips'
            zips_dir.mkdir(parents=True, exist_ok=True)
            
            unique_id = uuid.uuid4().hex[:8]
            zip_filename = f"{username}_{unique_id}.zip"
            zip_filepath = zips_dir / zip_filename
            
            # Create ZIP file
            with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(source_path)
                        zipf.write(file_path, arcname)
            
            return {
                'success': True,
                'filename': zip_filename,
                'filepath': str(zip_filepath)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to create ZIP: {str(e)}'
            }
