from datetime import datetime


def get_date(date_string):
    try:
        return datetime.strptime(date_string, "%d.%m.%Y")
    except ValueError:
        return False
