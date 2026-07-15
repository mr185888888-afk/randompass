import os

class Config:
    """Bot configuration settings"""
    
    # Get bot token from environment variable
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Image URL for logo
    IMAGE_URL = os.getenv('IMAGE_URL', '')
    
    # Railway settings
    PORT = int(os.getenv('PORT', 8443))
    
    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError(
                "BOT_TOKEN is not set. Please add it as an environment variable in Railway."
            )
        return True

Config.validate()
