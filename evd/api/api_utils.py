import datetime

import pytz
from pytz import timezone as pytztimezone

def get_timezone_now(timezone_str, remove_tzinfo=True):
    #Getting Current time in Indian Timezone 'Asia/Kolkata'
    utc_today = datetime.datetime.now(tz=pytz.UTC)
    ist_timezone = pytztimezone('Asia/Kolkata')
    today = utc_today.astimezone(ist_timezone)
    if remove_tzinfo:
        #Replacing timezone as MySQL backend does not support timezone-aware datetimes when USE_TZ is False.
        today = today.replace(tzinfo=None)

    return today
