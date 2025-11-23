"""
Redis Client - Caching and session management
Provides fast access to frequently accessed data
"""
import os
import json
from typing import Optional, Any, Dict, List
from dotenv import load_dotenv
import redis
from datetime import timedelta

load_dotenv()


class RedisClient:
    """Redis client wrapper for caching and session management"""
    
    def __init__(self,
                 host: Optional[str] = None,
                 port: int = 6379,
                 password: Optional[str] = None,
                 db: int = 0,
                 decode_responses: bool = True):
        """
        Initialize Redis connection
        
        Args:
            host: Redis host (defaults to REDIS_HOST env var)
            port: Redis port (defaults to 6379)
            password: Redis password (defaults to REDIS_PASSWORD env var)
            db: Redis database number (defaults to 0)
            decode_responses: Decode responses as strings
        """
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", port))
        self.password = password or os.getenv("REDIS_PASSWORD", None)
        self.db = db
        self.decode_responses = decode_responses
        
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                decode_responses=decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.client.ping()
        except redis.ConnectionError as e:
            print(f"Warning: Could not connect to Redis: {e}")
            print("Redis caching will be disabled. App will continue without cache.")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if self.client is None:
            return False
        try:
            self.client.ping()
            return True
        except:
            return False
    
    # ========== Cache Operations ==========
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.is_connected():
            return None
        
        try:
            value = self.client.get(key)
            if value and self.decode_responses:
                try:
                    return json.loads(value)
                except:
                    return value
            return value
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (None for no expiration)
        """
        if not self.is_connected():
            return False
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            elif not isinstance(value, str):
                value = str(value)
            
            if ttl:
                return self.client.setex(key, ttl, value)
            else:
                return self.client.set(key, value)
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.is_connected():
            return False
        
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.is_connected():
            return False
        
        try:
            return bool(self.client.exists(key))
        except:
            return False
    
    # ========== Task Caching ==========
    
    def cache_tasks(self, tasks: List[Dict], ttl: int = 300) -> bool:
        """Cache task list (5 minutes default)"""
        return self.set("tasks:all", tasks, ttl)
    
    def get_cached_tasks(self) -> Optional[List[Dict]]:
        """Get cached task list"""
        return self.get("tasks:all")
    
    def cache_task(self, task_id: int, task: Dict, ttl: int = 600) -> bool:
        """Cache individual task (10 minutes default)"""
        return self.set(f"task:{task_id}", task, ttl)
    
    def get_cached_task(self, task_id: int) -> Optional[Dict]:
        """Get cached task"""
        return self.get(f"task:{task_id}")
    
    def invalidate_task_cache(self, task_id: Optional[int] = None):
        """Invalidate task cache"""
        if task_id:
            self.delete(f"task:{task_id}")
        self.delete("tasks:all")
    
    # ========== Mood Caching ==========
    
    def cache_today_mood(self, mood: Dict, ttl: int = 3600) -> bool:
        """Cache today's mood (1 hour default)"""
        return self.set("mood:today", mood, ttl)
    
    def get_cached_today_mood(self) -> Optional[Dict]:
        """Get cached today's mood"""
        return self.get("mood:today")
    
    def invalidate_mood_cache(self):
        """Invalidate mood cache"""
        self.delete("mood:today")
    
    # ========== Productivity Caching ==========
    
    def cache_productivity(self, date: str, productivity: Dict, ttl: int = 1800) -> bool:
        """Cache productivity entry (30 minutes default)"""
        return self.set(f"productivity:{date}", productivity, ttl)
    
    def get_cached_productivity(self, date: str) -> Optional[Dict]:
        """Get cached productivity entry"""
        return self.get(f"productivity:{date}")
    
    def cache_productivity_trend(self, trend: List[Dict], ttl: int = 1800) -> bool:
        """Cache productivity trend"""
        return self.set("productivity:trend", trend, ttl)
    
    def get_cached_productivity_trend(self) -> Optional[List[Dict]]:
        """Get cached productivity trend"""
        return self.get("productivity:trend")
    
    def invalidate_productivity_cache(self, date: Optional[str] = None):
        """Invalidate productivity cache"""
        if date:
            self.delete(f"productivity:{date}")
        self.delete("productivity:trend")
    
    # ========== Session Management ==========
    
    def set_session(self, session_id: str, data: Dict, ttl: int = 86400) -> bool:
        """Set session data (24 hours default)"""
        return self.set(f"session:{session_id}", data, ttl)
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        return self.get(f"session:{session_id}")
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        return self.delete(f"session:{session_id}")
    
    # ========== Notification Queue ==========
    
    def push_notification(self, notification: Dict) -> bool:
        """Push notification to queue"""
        if not self.is_connected():
            return False
        
        try:
            return bool(self.client.lpush("notifications", json.dumps(notification)))
        except Exception as e:
            print(f"Redis notification error: {e}")
            return False
    
    def pop_notification(self) -> Optional[Dict]:
        """Pop notification from queue"""
        if not self.is_connected():
            return None
        
        try:
            notification = self.client.rpop("notifications")
            if notification:
                return json.loads(notification)
            return None
        except Exception as e:
            print(f"Redis pop notification error: {e}")
            return None
    
    def get_notification_count(self) -> int:
        """Get number of pending notifications"""
        if not self.is_connected():
            return 0
        
        try:
            return self.client.llen("notifications")
        except:
            return 0
    
    # ========== Real-time Data ==========
    
    def publish_event(self, channel: str, event: Dict) -> bool:
        """Publish event to channel (for pub/sub)"""
        if not self.is_connected():
            return False
        
        try:
            return bool(self.client.publish(channel, json.dumps(event)))
        except Exception as e:
            print(f"Redis publish error: {e}")
            return False
    
    def subscribe_channel(self, channel: str):
        """Subscribe to channel (returns pubsub object)"""
        if not self.is_connected():
            return None
        
        try:
            pubsub = self.client.pubsub()
            pubsub.subscribe(channel)
            return pubsub
        except Exception as e:
            print(f"Redis subscribe error: {e}")
            return None
    
    # ========== Utility ==========
    
    def clear_all_cache(self):
        """Clear all cache (use with caution!)"""
        if not self.is_connected():
            return
        
        try:
            self.client.flushdb()
        except Exception as e:
            print(f"Redis flush error: {e}")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        if not self.is_connected():
            return {}
        
        try:
            info = self.client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        except:
            return {}
    
    def close(self):
        """Close Redis connection"""
        if self.client:
            try:
                self.client.close()
            except:
                pass


# Global Redis instance
_redis_instance: Optional[RedisClient] = None


def get_redis_client(**kwargs) -> RedisClient:
    """Get or create global Redis client instance"""
    global _redis_instance
    if _redis_instance is None:
        _redis_instance = RedisClient(**kwargs)
    return _redis_instance

