import re
from urllib.parse import urlparse

class InputValidator:
    """Validates and sanitizes Instagram inputs"""
    
    def __init__(self):
        self.post_patterns = [
            r'instagram.com/p/([A-Za-z0-9_-]+)',
            r'instagram.com/reel/([A-Za-z0-9_-]+)',
            r'instagram.com/tv/([A-Za-z0-9_-]+)'
        ]
        self.profile_patterns = [
            r'instagram.com/([A-Za-z0-9_.]+)/?$'
        ]
        self.username_pattern = r'^[A-Za-z0-9_.]{1,30}$'
    
    def validate_input(self, user_input: str) -> tuple:
        """
        Validates user input
        Returns: (is_valid: bool, error_message: str)
        """
        if not user_input or len(user_input.strip()) == 0:
            return False, 'Input cannot be empty'
        
        if len(user_input) > 500:
            return False, 'Input too long'
        
        # Check for malicious patterns
        dangerous_patterns = ['../', '..\\', '<script', 'javascript:', 'data:']
        for pattern in dangerous_patterns:
            if pattern.lower() in user_input.lower():
                return False, 'Invalid input detected'
        
        return True, ''
    
    def detect_input_type(self, user_input: str) -> str:
        """
        Detects whether input is a post URL, profile URL, or username
        Returns: 'post', 'profile', or 'unknown'
        """
        user_input = user_input.strip()
        
        # Check for post/reel/tv URLs
        for pattern in self.post_patterns:
            if re.search(pattern, user_input):
                return 'post'
        
        # Check for profile URL
        for pattern in self.profile_patterns:
            match = re.search(pattern, user_input)
            if match:
                username = match.group(1)
                # Exclude known non-profile paths
                if username not in ['p', 'reel', 'tv', 'stories', 'explore']:
                    return 'profile'
        
        # Check if it's a plain username
        if re.match(self.username_pattern, user_input):
            return 'profile'
        
        return 'unknown'
    
    def sanitize_input(self, user_input: str) -> str:
        """
        Sanitizes and normalizes input
        Returns clean username or URL
        """
        user_input = user_input.strip()
        
        # Remove @ prefix if present
        if user_input.startswith('@'):
            user_input = user_input[1:]
        
        # If it's a URL, extract the relevant part
        if 'instagram.com' in user_input:
            # Extract shortcode for posts
            for pattern in self.post_patterns:
                match = re.search(pattern, user_input)
                if match:
                    return match.group(0)  # Return full match
            
            # Extract username for profiles
            for pattern in self.profile_patterns:
                match = re.search(pattern, user_input)
                if match:
                    return match.group(1)
        
        # Return as-is if it's a username
        return re.sub(r'[^A-Za-z0-9_.]', '', user_input)
    
    def extract_shortcode(self, url: str) -> str:
        """Extract shortcode from post URL"""
        for pattern in self.post_patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
