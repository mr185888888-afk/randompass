import os

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    IMAGE_URL = os.getenv('IMAGE_URL', '')
    PORT = int(os.getenv('PORT', 8443))
    
    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required!")
        return True

Config.validate()
