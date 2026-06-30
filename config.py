import os

class Config:
    """Bot configuration settings"""
    
    # Get bot token from environment variable (Railway will set this)
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Optional: Railway provides PORT for web services
    PORT = int(os.getenv('PORT', 8443))
    
    @classmethod
    def validate(cls):
        """Validate that all required configurations are set"""
        if not cls.BOT_TOKEN:
            raise ValueError(
                "BOT_TOKEN is not set. Please add it as an environment variable in Railway."
            )
        return True

# Validate configuration on import
Config.validate()
