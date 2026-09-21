"""Custom in-memory rate limiter."""
import time
from collections import defaultdict
from fastapi import Request, HTTPException, status, Depends
from app.core.config import get_settings, Settings

class InMemoryRateLimiter:
    def __init__(self):
        # Maps client_identifier -> list of timestamps
        self.history: dict[str, list[float]] = defaultdict(list)
        
    def check_rate_limit(self, identifier: str, limit_per_hour: int):
        now = time.time()
        cutoff = now - 3600.0
        
        # Cleanup old entries
        self.history[identifier] = [t for t in self.history[identifier] if t > cutoff]
        
        if len(self.history[identifier]) >= limit_per_hour:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
            
        self.history[identifier].append(now)

# Global instance
_limiter = InMemoryRateLimiter()

def rate_limit_dependency(request: Request, settings: Settings = Depends(get_settings)):
    """Dependency to apply rate limiting based on API Key or IP."""
    # Exempt health endpoint
    if request.url.path.endswith("/health") or request.url.path == "/":
        return
        
    api_key = request.headers.get("X-API-Key")
    client_ip = request.client.host if request.client else "127.0.0.1"
    
    # Identify client by API Key if present, otherwise IP
    identifier = api_key if api_key else client_ip
    
    _limiter.check_rate_limit(identifier, settings.rate_limit_int)
