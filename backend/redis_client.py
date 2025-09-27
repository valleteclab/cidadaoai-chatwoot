# Redis client for caching and session management
import redis
import json
import os
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        try:
            self.client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Error connecting to Redis: {str(e)}")
            raise
    
    async def set_cache(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set a value in cache with TTL
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            serialized_value = json.dumps(value) if not isinstance(value, str) else value
            result = self.client.setex(key, ttl, serialized_value)
            return result
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
            return False
    
    async def get_cache(self, key: str) -> Optional[Any]:
        """
        Get a value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            value = self.client.get(key)
            if value is None:
                return None
            
            # Try to parse as JSON, fallback to string
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            logger.error(f"Error getting cache: {str(e)}")
            return None
    
    async def delete_cache(self, key: str) -> bool:
        """
        Delete a key from cache
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting cache: {str(e)}")
            return False
    
    async def set_session(self, session_id: str, data: dict, ttl: int = 86400) -> bool:
        """
        Set session data
        
        Args:
            session_id: Session identifier
            data: Session data dictionary
            ttl: Session TTL in seconds (default: 24 hours)
            
        Returns:
            True if successful, False otherwise
        """
        session_key = f"session:{session_id}"
        return await self.set_cache(session_key, data, ttl)
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """
        Get session data
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None if not found
        """
        session_key = f"session:{session_id}"
        return await self.get_cache(session_key)
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete session data
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        session_key = f"session:{session_id}"
        return await self.delete_cache(session_key)
    
    async def increment_counter(self, key: str, ttl: Optional[int] = None) -> int:
        """
        Increment a counter
        
        Args:
            key: Counter key
            ttl: Optional TTL for the counter
            
        Returns:
            New counter value
        """
        try:
            pipe = self.client.pipeline()
            pipe.incr(key)
            if ttl:
                pipe.expire(key, ttl)
            results = pipe.execute()
            return results[0]
        except Exception as e:
            logger.error(f"Error incrementing counter: {str(e)}")
            return 0

# Global Redis service instance
redis_service = RedisService()
