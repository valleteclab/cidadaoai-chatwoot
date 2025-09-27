# Supabase database client and operations
from supabase import create_client, Client
import os
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials not found in environment variables")
        
        self.client: Client = create_client(supabase_url, supabase_key)
    
    async def save_conversation(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save conversation data to database
        
        Args:
            conversation_data: Dictionary containing conversation information
            
        Returns:
            Saved conversation record
        """
        try:
            result = self.client.table("conversations").insert(conversation_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
            raise
    
    async def save_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save message data to database
        
        Args:
            message_data: Dictionary containing message information
            
        Returns:
            Saved message record
        """
        try:
            result = self.client.table("messages").insert(message_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            raise
    
    async def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get conversation message history
        
        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of message records
        """
        try:
            result = self.client.table("messages")\
                .select("*")\
                .eq("conversation_id", conversation_id)\
                .order("created_at", desc=False)\
                .limit(limit)\
                .execute()
            
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    async def update_conversation_status(self, conversation_id: str, status: str) -> bool:
        """
        Update conversation status
        
        Args:
            conversation_id: ID of the conversation
            status: New status
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.client.table("conversations")\
                .update({"status": status})\
                .eq("id", conversation_id)\
                .execute()
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error updating conversation status: {str(e)}")
            return False
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile information
        
        Args:
            user_id: ID of the user
            
        Returns:
            User profile data or None if not found
        """
        try:
            result = self.client.table("user_profiles")\
                .select("*")\
                .eq("user_id", user_id)\
                .execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return None

# Global database service instance
db_service = DatabaseService()
