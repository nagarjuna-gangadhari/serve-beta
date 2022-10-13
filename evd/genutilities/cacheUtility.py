import logUtility as logService
from django.conf import settings
import redis

kcacheHost =  settings.REDIS_HOST
kcachePort =  settings.REDIS_PORT
kcachePwd = settings.REDIS_PWD

cacheObj = redis.Redis(
    host=kcacheHost,
    port=kcachePort,
    password=kcachePwd)

def getValueStringForKey(key):
    try:
        return cacheObj.get(key)
    except Exception as e:
        logService.logException("Cache getValueStringForKey", e.message)
        return None

def setValueStringForKey(key,value):
    try:
        val = cacheObj.set(key, value)
    except Exception as e:
        logService.logException("Cache setValueStringForKey", e.message)

