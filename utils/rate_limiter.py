import time
from collections import defaultdict
from threading import Lock

class RateLimiter:
    """IP-based rate limiting"""
    
    def __init__(self, max_requests: int = 20, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.lock = Lock()
    
    def allow_request(self, client_ip: str) -> bool:
        """
        Checks if request is allowed based on rate limit
        Returns: True if allowed, False if rate limit exceeded
        """
        with self.lock:
            current_time = time.time()
            
            # Clean old requests
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < self.window_seconds
            ]
            
            # Check if under limit
            if len(self.requests[client_ip]) < self.max_requests:
                self.requests[client_ip].append(current_time)
                return True
            
            return False
    
    def reset(self, client_ip: str):
        """Reset rate limit for IP"""
        with self.lock:
            if client_ip in self.requests:
                del self.requests[client_ip]
