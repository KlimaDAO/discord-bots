import calendar
from datetime import datetime


def get_current_date_timestamp():
    date_string = datetime.utcnow().strftime("%d/%m/%Y")
    date = datetime.strptime(date_string, "%d/%m/%Y")
    current_date_timestamp = round(calendar.timegm(date.timetuple()))

    return current_date_timestamp


def get_days_ago_timestamp(days):
    '''
    Get timestamp for a day that was `days`(param) ago
    '''
    days_in_seconds = days * 24 * 60 * 60
    return get_current_date_timestamp() - days_in_seconds
