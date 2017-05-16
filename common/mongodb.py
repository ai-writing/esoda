from django.conf import settings
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)

MONGODB = MongoClient(settings.MONGODB_HOST)

try:
    MONGODB.database_names()
except:
    MONGODB.admin.authenticate(settings.MONGODB_USER, settings.MONGODB_PASSWORD)
logger.info('Connected to MongoDB: %s', MONGODB)  # Logging won't work in settings.py
