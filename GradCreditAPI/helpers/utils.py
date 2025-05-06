import csv
import logging

from lcg_common import now_utc
from lcg_common.webservice import current_user_name


def welcome_message():
    msg = f"<namehere> API -- {now_utc().isoformat()}"
    try:
        if current_user_name():
            msg = f"Welcome {current_user_name()}! <namehere> API -- {now_utc().isoformat()}"
    except Exception as e:
        logging.error(e)
    return msg