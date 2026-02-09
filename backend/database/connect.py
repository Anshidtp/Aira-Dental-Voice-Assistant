from pymongo import AsyncMongoClient
from beanie import init_beanie
from loguru import logger
from typing import Optional

from ..config.settings import settings
from ..models.database import DOCUMENT_MODELS


class Database:
    """MongoDB database manager"""
    
    client: Optional[AsyncMongoClient] = None
    
    @classmethod
    async def connect_db(cls):
        """
        Connect to MongoDB Atlas and initialize Beanie ODM
        """
        try:
            # Create Motor client with MongoDB Atlas connection string
            cls.client = AsyncMongoClient(
                settings.MONGODB_URI,  # Updated to use Atlas URI
                tls=True,  # Ensure TLS/SSL is enabled for Atlas
                tlsAllowInvalidCertificates=False  # Validate certificates
            )
            
            # Test connection
            await cls.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB Atlas at {settings.MONGODB_URI}")
            
            # Initialize Beanie with document models
            await init_beanie(
                database=cls.client[settings.MONGODB_DB_NAME],
                document_models=DOCUMENT_MODELS
            )
            
            logger.info(f"Beanie ODM initialized with {len(DOCUMENT_MODELS)} document models")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB Atlas: {e}")
            raise
    
    @classmethod
    async def close_db(cls):
        """
        Close MongoDB connection
        """
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")
    
    @classmethod
    def get_db(cls):
        """
        Get database instance
        
        Returns:
            Database instance
        """
        if not cls.client:
            raise RuntimeError("Database not initialized. Call connect_db() first.")
        
        return cls.client[settings.MONGODB_DB_NAME]


# Global database instance
db = Database()