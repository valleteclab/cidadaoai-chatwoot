# PostgreSQL database client and operations
import asyncpg
import os
from typing import Dict, Any, List, Optional
import logging
import json

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql://cidadaoai_user:sua_senha@localhost:5432/cidadaoai")
        self.pool = None
    
    async def connect(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error(f"Error creating database pool: {str(e)}")
            raise
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
    
    async def save_conversation(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save conversation data to database"""
        try:
            async with self.pool.acquire() as conn:
                query = """
                INSERT INTO conversations (chatwoot_conversation_id, user_id, status, channel)
                VALUES ($1, $2, $3, $4)
                RETURNING *
                """
                result = await conn.fetchrow(
                    query,
                    conversation_data.get('chatwoot_conversation_id'),
                    conversation_data.get('user_id'),
                    conversation_data.get('status', 'open'),
                    conversation_data.get('channel')
                )
                return dict(result) if result else {}
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
            raise
    
    async def save_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save message data to database"""
        try:
            async with self.pool.acquire() as conn:
                query = """
                INSERT INTO messages (conversation_id, chatwoot_message_id, content, message_type, sender_type)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
                """
                result = await conn.fetchrow(
                    query,
                    message_data.get('conversation_id'),
                    message_data.get('chatwoot_message_id'),
                    message_data.get('content'),
                    message_data.get('message_type'),
                    message_data.get('sender_type')
                )
                return dict(result) if result else {}
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            raise
    
    async def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation message history"""
        try:
            async with self.pool.acquire() as conn:
                query = """
                SELECT * FROM messages 
                WHERE conversation_id = $1 
                ORDER BY created_at ASC 
                LIMIT $2
                """
                results = await conn.fetch(query, conversation_id, limit)
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    async def update_conversation_status(self, conversation_id: str, status: str) -> bool:
        """Update conversation status"""
        try:
            async with self.pool.acquire() as conn:
                query = """
                UPDATE conversations 
                SET status = $1, updated_at = NOW()
                WHERE id = $2
                """
                result = await conn.execute(query, status, conversation_id)
                return result != "UPDATE 0"
        except Exception as e:
            logger.error(f"Error updating conversation status: {str(e)}")
            return False
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile information"""
        try:
            async with self.pool.acquire() as conn:
                query = "SELECT * FROM user_profiles WHERE user_id = $1"
                result = await conn.fetchrow(query, user_id)
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return None

# Global database service instance
db_service = DatabaseService()
