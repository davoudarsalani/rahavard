from django.conf import settings
from django.contrib import admin, messages
from django.core.management.base import CommandError
from django.db.models import QuerySet
from django.http import HttpResponse, HttpRequest

from datetime import datetime
from math import floor, log as math_log, pow as math_pow
from os import path, listdir, getenv
from re import match, sub, compile
from types import FrameType
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from convert_numbers import english_to_persian
from jdatetime import datetime as jdt
from natsort import natsorted

import jdatetime


ADMIN_PY__LIST_DISPLAY_LINKS   = ['id', 'short_uuid']
#
ADMIN_PY__READONLY_FIELDS      = ['id', 'short_uuid', 'created', 'updated']
ADMIN_PY__LIST_FILTER          = ['active', 'short_uuid']
#
ADMIN_PY__USER_READONLY_FIELDS = ['id', 'short_uuid', 'date_joined', 'last_login']
ADMIN_PY__USER_LIST_FILTER     = ['is_superuser', 'is_staff', 'is_active', 'is_limited_admin', 'short_uuid']

JALALI_FORMAT = '%A %H %M %S %d %m %Y'

YMD_REGEX = r'[0-9]{4}-[0-9]{2}-[0-9]{2}'
HMS_REGEX = r'[0-9]{2}:[0-9]{2}:[0-9]{2}'

_SIZE_SIFFIXES = {
    'persian': [
        'بایت',
        'کیلوبایت',
        'مگابایت',
        'گیگابایت',
        'ترابایت',
        'پتابایت',
        'اگزابایت',
        'زتابایت',
        'یوتابایت',
    ],
    'latin': [
        'B',
        'KB',
        'MB',
        'GB',
        'TB',
        'PB',
        'EB',
        'ZB',
        'YB',
    ],
}


def contains_ymd(string: str) -> bool:
    '''
    Check if a string contains a date in the format YYYY-MM-DD.

    This function uses a regular expression to determine if the input string contains a date in the format YYYY-MM-DD.

    Args:
        string (str): The input string to be checked.

    Returns:
        bool: True if the string contains a date in the format YYYY-MM-DD, False otherwise.

    Examples:
        >>> contains_ymd("Today's date is 2023-10-05.")
        True
        >>> contains_ymd('No date here!')
        False
        >>> contains_ymd('The event is on 2023-12-25.')
        True
        >>> contains_ymd('Date: 2023/10/05')
        False
    '''

    return match(f'^.*{YMD_REGEX}.*$', string) is not None

def is_ymd(string: str) -> bool:
    '''
    Check if a given string matches the Year-Month-Day (YMD) format.

    Args:
        string (str): The string to be checked.

    Returns:
        bool: True if the string matches the YMD format, False otherwise.

    Examples:
        >>> is_ymd('2023-10-05')
        True
        >>> is_ymd('05-10-2023')
        False
        >>> is_ymd('2023/10/05')
        False
        >>> is_ymd('20231005')
        False
    '''

    return match(f'^{YMD_REGEX}$', string) is not None

def starts_with_ymdhms(string: str) -> bool:
    '''
    Check if a string starts with a date and time in the format 'YYYY-MM-DD HH:MM:SS'.

    Args:
        string (str): The string to be checked.

    Returns:
        bool: True if the string starts with a date and time in the specified format, False otherwise.

    Examples:
        >>> starts_with_ymdhms('2023-10-05 12:34:56 Some event')
        True
        >>> starts_with_ymdhms('Some event 2023-10-05 12:34:56')
        False
        >>> starts_with_ymdhms('2023-10-05 12:34:56')
        False
        >>> starts_with_ymdhms('2023-10-05 12:34 Some event')
        False
    '''

    return match(f'^{YMD_REGEX} {HMS_REGEX} ', string) is not None

## ---------------------------------

def calculate_offset(page_number: int, limit_to_show: int) -> int:
    '''
    Calculate the offset for a given page number and limit to show in a MySQL query.

    Args:
        page_number (int): The current page number (1-based index).
        limit_to_show (int): The number of items to show per page (MySQL LIMIT).

    Returns:
        int: The offset to be used in a MySQL query.

    Examples:
        >>> calculate_offset(1, 25)
        0

        >>> calculate_offset(2, 25)
        25

        >>> calculate_offset(3, 10)
        20
    '''

    return (page_number - 1) * limit_to_show

def clear_messages(request: HttpRequest) -> None:
    '''
    Clears all messages from the given Django HTTP request.

    Args:
        request (HttpRequest): The Django HTTP request object containing messages to be cleared.

    Returns:
        None
    '''

    storage = messages.get_messages(request)
    storage.used = True

def comes_from_htmx(request: HttpRequest) -> bool:
    '''
    Check if the request comes from HTMX.

    This function inspects the headers of a Django request to determine if it
    originated from an HTMX request by checking for the presence of the 'HX-Request' header.

    Args:
        request (HttpRequest): The Django HttpRequest object.

    Returns:
        bool: True if the request contains the 'HX-Request' header, False otherwise.

    Examples:
        >>> from django.http import HttpRequest
        >>> request = HttpRequest()
        >>> request.headers['HX-Request'] = 'true'
        >>> comes_from_htmx(request)
        True

        >>> request = HttpRequest()
        >>> comes_from_htmx(request)
        False
    '''

    return 'HX-Request' in request.headers

def convert_byte(size_in_bytes: Union[int, float], to_persian: bool = False) -> str:
    '''
    Convert a size in bytes to a human-readable string format.

    Parameters:
        size_in_bytes (Union[int, float]): The size in bytes to be converted.
        to_persian (bool): If True, the output will be in Persian. Default is False.

    Returns:
        str: The human-readable string representation of the size.

    Examples:
        >>> convert_byte(1024)
        '1.0KB'
        >>> convert_byte(1048576)
        '1.0MB'
        >>> convert_byte(0)
        '0B'
        >>> convert_byte(1024, to_persian=True)
        '۱.۰ کیلوبایت'
        >>> convert_byte(1048576, to_persian=True)
        '۱.۰ مگابایت'

    Note:
        - https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
    '''
    ## __HAS_RUST_VERSION__

    if not is_int_or_float(size_in_bytes) or \
       int(size_in_bytes) == 0:
        if to_persian:
            return '۰ بایت'
        return '0B'

    i = int(floor(math_log(size_in_bytes, 1024)))
    p = math_pow(1024, i)
    conv = f'{float(size_in_bytes / p):.1f}'

    ## remove trailing .0 or .00
    if match(r'^[0-9]+\.0+$', conv):
        conv = sub(r'\.0+$', '', conv)

    if to_persian:
        suffixes = _SIZE_SIFFIXES.get('persian')
    else:
        suffixes = _SIZE_SIFFIXES.get('latin')

    if to_persian:
        return f'{persianize(conv)} {suffixes[i]}'

    return f'{conv}{suffixes[i]}'

def convert_millisecond(ms: Union[int, float], verbose: bool = True) -> Union[str, float]:
    '''
    Convert milliseconds to seconds and return the result.

    Parameters:
        ms (Union[int, float]): The time in milliseconds to be converted. If the input is not an integer or float, it defaults to 0.
        verbose (bool): If True, returns a verbose string representation of the time. If False, returns the time as a float. Default is True.

    Returns:
        str or float: The converted time in seconds, either as a verbose string or a float, depending on the value of `verbose`.

    Examples:
        >>> convert_millisecond(1500)
        '1.5 seconds'
        >>> convert_millisecond(1500, verbose=False)
        1.5
        >>> convert_millisecond('invalid', verbose=False)
        0.0
        >>> convert_millisecond(0)
        '0.0 seconds'
    '''

    if not is_int_or_float(ms):
        ms = 0

    return convert_second(
        ## milliseconds -> seconds
        float(ms) / 1000,

        verbose=verbose,
    )

def convert_second(seconds: Union[int, float], verbose: bool = True) -> str:
    '''
    Convert a given number of seconds into a human-readable string format.

    Parameters:
        seconds (Union[int, float]): The number of seconds to convert.
        verbose (bool): If True, returns a verbose string format. If False, returns a compact string format. Default is True.

    Returns:
        str: The converted time in a human-readable string format.

    Examples:
        >>> convert_second(0)
        '0'
        >>> convert_second(0, verbose=False)
        '0:00'
        >>> convert_second(0.56)
        '~0'
        >>> convert_second(0.56, verbose=False)
        '~0:00'
        >>> convert_second(3661)
        '1 hr, 1 min and 1 sec'
        >>> convert_second(3661, verbose=False)
        '1:01:01'
        >>> convert_second(86400)
        '1 day'
        >>> convert_second(86400, verbose=False)
        '1:00:00:00'
        >>> convert_second(31536000)
        '1 year and 5 days'
        >>> convert_second(31536000, verbose=False)
        '1:00:05:00:00:00'
    '''
    ## __HAS_RUST_VERSION__

    if not is_int_or_float(seconds):
        ## JUMP_3
        if verbose:
            return '0'
        return '0:00'

    ## using float instead of int
    ## to prevent turning 0.56 into 0
    seconds = float(seconds)

    if seconds == 0:
        ## JUMP_3
        if verbose:
            return '0'
        return '0:00'

    if seconds < 1:
        if verbose:
            return '~0'
        return '~0:00'

    ss = f'{int(seconds % 60):02}'
    mi = f'{int(seconds / 60 % 60):02}'
    hh = f'{int(seconds / 3600 % 24):02}'
    dd = f'{int(seconds / 3600 / 24 % 30):02}'
    mo = f'{int(seconds / 3600 / 24 / 30 % 12):02}'
    yy = f'{int(seconds / 3600 / 24 / 30 / 12):02}'

    if yy == '00' and mo == '00' and dd == '00':
        if verbose: result = f'{hh} hrs, {mi} mins and {ss} secs'
        else:       result = f'{hh}:{mi}:{ss}'
    elif yy == '00' and mo == '00':
        if verbose: result = f'{dd} days, {hh} hrs and {mi} mins'
        else:       result = f'{dd}:{hh}:{mi}:{ss}'
    elif yy == '00':
        if verbose: result = f'{mo} months, {dd} days and {hh} hrs'
        else:       result = f'{mo}:{dd}:{hh}:{mi}:{ss}'
    else:
        if verbose: result = f'{yy} years, {mo} months and {dd} days'
        else:       result = f'{yy}:{mo}:{dd}:{hh}:{mi}:{ss}'

    if verbose:
        ## remove items whose values are 00, and adjust comma and 'and'
        result = sub(r'00 [a-z]+s, ',                 '',          result)
        result = sub(r'00 [a-z]+s and ',              '',          result)
        result = sub(r'00 [a-z]+s$',                  '',          result)
        result = sub(r', ([0-9][0-9] [a-z]+s )',      r' and \1',  result)
        result = sub(r'and 00 [a-z]+s ',              '',          result)
        result = sub(r' and $',                       '',          result)
        result = sub(r', ([0-9][0-9] [a-z]+)$',       r' and \1',  result)
        result = sub(r' and ([0-9][0-9] [a-z]+) and', r', \1 and', result)
        result = sub(r', +$',                         '',          result)
        result = sub(r', ([0-9][0-9] [a-z]+s)$',      r' and \1',  result)

        ## remove plural s when value is 01
        result = sub(r'(01 [a-z]+)s ',  r'\1 ',  result)
        result = sub(r'(01 [a-z]+)s, ', r'\1, ', result)
        result = sub(r'(01 [a-z]+)s$',  r'\1',   result)

        ## ..., 01 hr, ...  -> ..., 1 hr, ...
        result = sub(r', 0([0-9])',   r', \1',   result)

        ## ... and 05 hrs ... -> ... and 5 hrs ...
        ## (this seems to be a bug in the original function)
        result = sub(r'and 0([0-9])', r'and \1', result)
    else:
        ## 0:00:12 -> 0:12
        ## 0:08:12 -> 8:12
        result = sub(r'^0+:0([0-9]):', r'\1:', result)

        ## 0:10:12 -> 10:12
        result = sub(r'^0+:([1-9])([0-9]):', r'\1\2:', result)

    ## 02 days, ... -> 2 days, ...
    ## 01:23        -> 1:23
    result = sub(r'^0([0-9])', r'\1', result)

    return result

def convert_string_True_False_None_0(item: str) -> Union[bool, None, int, str]:
    '''
    Convert specific string representations to their corresponding Python objects.

    This function converts the strings 'True', 'False', 'None', and '0' to their
    respective Python objects: True, False, None, and 0. If the input string does
    not match any of these, it returns the input string unchanged.

    Parameters:
        item (str): The input string to be converted.

    Returns:
        bool, None, int, or str: The converted Python object or the original string
        if no conversion is applicable.

    Examples:
        >>> convert_string_True_False_None_0('True')
        True
        >>> convert_string_True_False_None_0('False')
        False
        >>> convert_string_True_False_None_0('None')
        None
        >>> convert_string_True_False_None_0('0')
        0
        >>> convert_string_True_False_None_0('Hello')
        'Hello'
    '''

    if item in ['True', 'False', 'None', '0']:
        return {
            'True': True,
            'False': False,
            'None': None,
            '0': 0,
        }.get(item)

    return item

def convert_timestamp_to_jalali(tmstmp: Optional[int] = None) -> str:
    '''
    Convert a Unix timestamp to a Jalali date string.

    This function converts a given Unix timestamp to a Jalali date string in the format:
    'weekday hour:minute:second year/month/day'. If no timestamp is provided, it returns an empty string.

    Parameters:
        tmstmp (Optional[int]): Unix timestamp to be converted. Defaults to None.

    Returns:
        str: The converted Jalali date string or an empty string if no timestamp is provided.

    Examples:
        >>> convert_timestamp_to_jalali(1682598113)
        'چهارشنبه ۰۷:۰۶:۳۳ ۳۰-/۰۱/۱۴۰۲'

        >>> convert_timestamp_to_jalali()
        ''
    '''

    if not tmstmp:
        return ''

    jdatetime.set_locale('fa_IR')

    jalali_object = jdt.fromtimestamp(int(tmstmp))
    w, h, mi, s, d, mo, y = jalali_object.strftime(JALALI_FORMAT).split()

    return f'{w} {english_to_persian(h)}:{english_to_persian(mi)}:{english_to_persian(s)} {english_to_persian(y)}/{english_to_persian(mo)}/{english_to_persian(d)}'

def convert_to_jalali(gregorian_object: Optional[datetime] = None) -> str:
    '''
    Convert a Gregorian datetime object to a Jalali datetime string.

    This function takes a Gregorian datetime object and converts it to a Jalali (Persian) datetime string formatted in Persian locale.

    Args:
        gregorian_object (Optional[datetime]): The Gregorian datetime object to convert. Defaults to None.

    Returns:
        str: The Jalali datetime string in the format 'Weekday Hour:Minute:Second Year/Month/Day'. Returns an empty string if no datetime object is provided.

    Examples:
        >>> from datetime import datetime
        >>> gregorian_date = datetime(2023, 10, 5, 15, 30, 45)
        >>> convert_to_jalali(gregorian_date)
        'پنج‌شنبه ۱۵:۳۰:۴۵ ۱۴۰۲/۰۷/۱۳'

        >>> convert_to_jalali()
        ''
    '''

    if not gregorian_object:
        return ''

    jdatetime.set_locale('fa_IR')

    timestamp = convert_to_second(gregorian_object)

    jalali_object = jdt.fromtimestamp(timestamp)
    w, h, mi, s, d, mo, y = jalali_object.strftime(JALALI_FORMAT).split()

    return f'{w} {english_to_persian(h)}:{english_to_persian(mi)}:{english_to_persian(s)} {english_to_persian(y)}/{english_to_persian(mo)}/{english_to_persian(d)}'

def convert_to_second(date_obj: datetime) -> int:
    '''
    Convert a datetime object to seconds since the epoch.

    Args:
        date_obj (datetime): A datetime object to be converted.

    Returns:
        int: The number of seconds since the epoch.

    Examples:
        >>> from datetime import datetime
        >>> date_obj = datetime(2023, 10, 26, 12, 0, 0)
        >>> convert_to_second(date_obj)
        1698381096

        >>> date_obj = datetime(1970, 1, 1, 0, 0, 0)
        >>> convert_to_second(date_obj)
        0

        >>> date_obj = datetime(2000, 1, 1, 0, 0, 0)
        >>> convert_to_second(date_obj)
        946684800
    '''

    return int(date_obj.timestamp())

def create_id_for_htmx_indicator(*args: str) -> str:
    '''
    Generate a unique ID for an HTMX indicator by joining the provided arguments with hyphens.

    Args:
        *args: Variable length argument list of strings to be joined.

    Returns:
        str: A string representing the unique ID for the HTMX indicator.

    Examples:
        >>> create_id_for_htmx_indicator('by-date', 'source-ip', '2024-06-30')
        'by-date-source-ip-2024-06-30--htmx-indicator'

        >>> create_id_for_htmx_indicator('tops')
        'tops--htmx-indicator'
    '''

    return sub(
        '-{3,}',
        '--',
        f'{"-".join(args)}--htmx-indicator'
    )

def create_short_uuid() -> str:
    '''
    Generate a short UUID string.

    This function creates a UUID (Universally Unique Identifier) and returns a shortened version of it by converting the time_low part of the UUID to a hexadecimal string.

    Returns:
        str: A shortened UUID string.

    Examples:
        >>> create_short_uuid()
        '1a2b3c4d'

        >>> create_short_uuid()
        '5e6f7a8b'
    '''

    _sample = uuid4()
    return hex(int(_sample.time_low))[2:]

def get_date_time_live() -> HttpResponse:
    '''
    Get the current date and time in Persian format.

    This function sets the locale to Persian (fa_IR), retrieves the current Jalali date and time,
    converts the year, month, day, hour, and minute to Persian numerals, and returns the formatted
    date and time as an HTTP response.

    Returns:
        HttpResponse: The current date and time in the format 'YYYY/MM/DD HH:MM' with Persian numerals.

    Examples:
        >>> get_date_time_live()
        HttpResponse('۱۴۰۱/۰۱/۱۷ ۱۴:۳۰')

        >>> get_date_time_live()
        HttpResponse('۱۴۰۱/۰۲/۰۵ ۰۹:۱۵')
    '''

    jdatetime.set_locale('fa_IR')

    jdt_now = jdt.now()

    _year  = english_to_persian(jdt_now.strftime('%Y'))  ## ۱۴۰۱
    _day   = english_to_persian(jdt_now.strftime('%d'))  ## ۱۷
    _month = english_to_persian(jdt_now.strftime('%m'))  ## ۰۱

    _hour = english_to_persian(jdt_now.strftime('%H'))
    _min  = english_to_persian(jdt_now.strftime('%M'))
    # _sec  = english_to_persian(jdt_now.strftime('%S'))

    # _weekday = jdt_now.strftime('%A')  ## چهارشنبه

    return HttpResponse(f'{_year}/{_month}/{_day} {_hour}:{_min}')

def get_list_of_files(directory: str, extension: str) -> List[str]:
    '''
    Get a list of files in a directory with a specific extension, sorted naturally.

    Args:
        directory (str): The directory to search for files.
        extension (str): The file extension to filter by.

    Returns:
        list: A list of absolute file paths with the specified extension, sorted naturally.

    Examples:
        >>> get_list_of_files('/FOO/BAR/BAZ', 'txt')
        ['/FOO/BAR/BAZ/file1.txt', '/FOO/BAR/BAZ/file2.txt']

        >>> get_list_of_files('/FOO/BAR/BAZ', 'py')
        ['/FOO/BAR/BAZ/script1.py', '/FOO/BAR/BAZ/script2.py']

        >>> get_list_of_files('/non/existent/dir', 'txt')
        []

        >>> get_list_of_files('/FOO/BAR/BAZ', 'jpg')
        ['/FOO/BAR/BAZ/image1.jpg', '/FOO/BAR/BAZ/image2.jpg']
    '''

    if not path.exists(directory):
        return []

    return natsorted([
        path.abspath(path.join(directory, _))
        for _ in listdir(directory)

        if all([
            ## NOTE do NOT .{extension} -> {extension}
            _.endswith((f'.{extension}')),

            path.isfile(f'{directory}/{_}'),
        ])
    ])

def get_percent(
    smaller_number: Union[int, float],
    total_number: Union[int, float],
    to_persian: bool = False,
) -> str:
    '''
    Calculate the percentage of a smaller number relative to a total number.

    Parameters:
        smaller_number (Union[int, float]): The part of the total number.
        total_number (Union[int, float]): The total number.
        to_persian (bool): If True, returns the percentage in Persian numerals.

    Returns:
        str: The percentage as a string, optionally in Persian numerals.

    Examples:
        >>> get_percent(25, 100)
        '25'
        >>> get_percent(0, 100)
        '0'
        >>> get_percent(25, 0)
        '0'
        >>> get_percent(1, 100)
        '1'
        >>> get_percent(99.95232355216523, 100)
        '99.9'
        >>> get_percent(25, 100, to_persian=True)
        '۲۵'
        >>> get_percent(0, 100, to_persian=True)
        '۰'
        >>> get_percent(1, 100, to_persian=True)
        '۱'
    '''

    if smaller_number == 0 or total_number == 0:
        if to_persian:
            return '۰'
        return '0'

    _perc = (smaller_number * 100) / total_number

    if int(_perc) == 0:
        if to_persian:
            return '~۰'
        return '~0'

    _perc = int(_perc * 10) / 10  ## 99.95232355216523 -> 99.9
    ## NOTE we didn't use f'{_perc:.1f}'
    ##      because it turns 99.95232355216523 to 100.0

    _perc = sub(r'\.0+$', '', str(_perc))  ## 97.0 -> 97

    if to_persian:
        return persianize(_perc)

    return _perc

def intcomma_persian(num: str) -> str:
    '''
    Formats a Persian number string by adding commas as thousand separators.

    This function supports both integer and floating-point Persian numbers. 
    For floating-point numbers, it correctly handles the decimal separator.

    Args:
        num (str): The Persian number string to be formatted.

    Returns:
        str: The formatted Persian number string with commas as thousand separators.

    Examples:
        >>> intcomma_persian('۱۲۳۴۵۶۷۸۹۰')
        '۱،۲۳۴،۵۶۷،۸۹۰'

        >>> intcomma_persian('۱۲۳۴۵۶۷۸۹۰.۱۲۳۴۵۶۷۸۹۰')
        '۱،۲۳۴،۵۶۷،۸۹۰.۱۲۳۴۵۶۷۸۹۰'

        >>> intcomma_persian('۱۲۳۴۵۶۷۸۹۰/۱۲۳۴۵۶۷۸۹۰')
        '۱،۲۳۴،۵۶۷،۸۹۰/۱۲۳۴۵۶۷۸۹۰'

    Note:
        - https://stackoverflow.com/questions/50319819/separate-thousands-while-typing-in-farsipersian
    '''

    commad = ''
    left = ''
    right = ''
    is_float = False

    ## JUMP_1 is float
    if match(r'^[۱۲۳۴۵۶۷۸۹۰]+\.[۱۲۳۴۵۶۷۸۹۰]+$', num):
        left, right = num.split('.')
        separator = '.'
        is_float = True

    ## JUMP_1 is float
    elif match(r'^[۱۲۳۴۵۶۷۸۹۰]+\/[۱۲۳۴۵۶۷۸۹۰]+$', num):
        left, right = num.split('/')
        separator = '/'
        is_float = True

    else:
        left = num


    for idx, char in enumerate(reversed(left), start=0):
        if idx % 3 == 0 and idx > 0:
            commad = char + '،' + commad
        else:
            commad = char + commad

    if is_float:
        commad = f'{commad}{separator}{right}'

    return commad


_INT_OR_FLOAT_PATTERN = compile(r'^[0-9\.]+$')
def is_int_or_float(string: str) -> bool:
    '''
    Check if the given string represents an integer or a float.

    Args:
        string (str): The string to be checked.

    Returns:
        bool: True if the string represents an integer or a float, False otherwise.

    Examples:
        >>> is_int_or_float('123')
        True
        >>> is_int_or_float('123.456')
        True
        >>> is_int_or_float(123)
        True
        >>> is_int_or_float(123.456)
        True
        >>> is_int_or_float(')
        False
        >>> is_int_or_float('abc')
        False
        >>> is_int_or_float('123abc')
        False
        >>> is_int_or_float(None)
        False
        >>> is_int_or_float(True)
        False
        >>> is_int_or_float(False)
        False
    '''
    ## __HAS_RUST_VERSION__

    return match(_INT_OR_FLOAT_PATTERN, str(string)) is not None

def persianize(number: Union[int, float]) -> str:
    '''
    Convert an English number to its Persian equivalent.

    This function takes a number (integer or float) and converts it to a Persian string representation.
    If the number is a float, it handles the decimal part appropriately.

    Args:
        number (Union[int, float]): The number to be converted.

    Returns:
        str: The Persian string representation of the number.

    Examples:
        >>> persianize(123)
        '۱۲۳'
        >>> persianize(123.45)
        '۱۲۳.۴۵'
        >>> persianize(123.00)
        '۱۲۳'
    '''

    number = str(number)

    ## JUMP_1 is float
    if match(r'^[0-9]+\.[0-9]+$', number):
        _left, _right = number.split('.')
        if match('^0+$', _right):
            return english_to_persian(_left)
        return f'{english_to_persian(_left)}.{english_to_persian(_right[:2])}'

    return english_to_persian(int(number))

def sort_dict(dictionary: Dict[Any, Any], based_on: str, reverse: bool) -> Dict[Any, Any]:
    '''
    Sort a dictionary based on its keys or values, with tie-breaking by key if sorting by value.

    Parameters:
        dictionary (Dict[Any, Any]): The dictionary to be sorted.
        based_on (str): The criteria to sort by, either 'key' or 'value'.
        reverse (bool): If True, sort in descending order, otherwise ascending.

    Returns:
        dict: A new dictionary sorted based on the specified criteria.

    Examples:
        >>> sort_dict({'b': 2, 'a': 1, 'c': 3}, based_on='key', reverse=False)
        {'a': 1, 'b': 2, 'c': 3}

        >>> sort_dict({'b': 2, 'a': 1, 'c': 3}, based_on='key', reverse=True)
        {'c': 3, 'b': 2, 'a': 1}

        >>> sort_dict({'b': 2, 'a': 1, 'c': 3}, based_on='value', reverse=False)
        {'a': 1, 'b': 2, 'c': 3}

        >>> sort_dict({'b': 2, 'a': 1, 'c': 3}, based_on='value', reverse=True)
        {'c': 3, 'b': 2, 'a': 1}
    '''
    ## __HAS_RUST_VERSION__

    def _normalize(val: Any) -> Any:
        '''None -> 'None' to avoid errors'''
        if val is None:
            return 'None'
        return val

    if based_on == 'key':
        return dict(
            natsorted(
                dictionary.items(),
                key=lambda item: _normalize(item[0]),
                reverse=reverse,
            )
        )

    if based_on == 'value':
        ## sort by value first (ascending or descending depending on reverse),
        ## then by key ascending to break ties -
        ## i.e. the pairs whose values are the same,
        ## will be sorted by key ascending no matter what reverse is

        def _sort_key(item):
            val = _normalize(item[1])
            key = _normalize(item[0])
            # For reverse, numeric values get negated; strings stay as-is, and reverse handled manually
            if isinstance(val, (int, float)):
                val_sort = -val if reverse else val
            else:
                val_sort = val  # strings can't be negated
            return (val_sort, key)  # tie-break always by key ascending

        return dict(natsorted(dictionary.items(), key=_sort_key))

    return dictionary

def to_tilda(text: str) -> str:
    '''
    Replaces the home directory path in the given text with a tilde (~).

    Args:
        text (str): The text in which to replace the home directory path.

    Returns:
        str: The text with the home directory path replaced by a tilde.

    Examples:
        >>> to_tilda('/home/my_username/documents/file.txt')
        '~/documents/file.txt'
        >>> to_tilda('/home/my_username/')
        '~/'
        >>> to_tilda('/home/other_username/file.txt')
        '/home/other_username/file.txt'
    '''
    ## __HAS_RUST_VERSION__

    return sub(getenv('HOME'), '~', text)


# -----------------
## functions used in django admin.py


@admin.action(description='Make Active')
def make_active(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet,
) -> None:
    '''
    Activates the selected queryset objects based on their model type.

    This function updates the `is_active` field to `True` for 'User' model instances
    and the `active` field to `True` for other model instances in the provided queryset.
    It also sends a message to the model admin indicating the number of objects that were activated.

    Parameters:
        modeladmin (admin.ModelAdmin): The admin.ModelAdmin instance that called this action.
        request (HttpRequest): The current request object.
        queryset (QuerySet): The queryset of objects selected by the user.

    Note:
        - https://stackoverflow.com/questions/67979442/how-do-i-find-the-class-that-relatedmanager-is-managing-when-the-queryset-is-emp
    '''

    _caller = modeladmin.model.__name__  ## 'User'/'Router'/...  (-> is str)
    if _caller == 'User':
        inactive_objects = queryset.filter(is_active=False)
    else:
        inactive_objects = queryset.filter(active=False)

    count = inactive_objects.count()

    if count:
        if _caller == 'User':
            inactive_objects.update(is_active=True)
        else:
            inactive_objects.update(active=True)

        modeladmin.message_user(
            request,
            f'{count} made active'
        )

@admin.action(description='Make Inactive')
def make_inactive(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet,
) -> None:
    '''
    Inactivates the selected queryset objects based on their model type.

    This function updates the `is_active` field to `False` for 'User' model instances
    and the `active` field to `False` for other model instances in the provided queryset.
    It also sends a message to the model admin indicating the number of objects that were activated.

    Parameters:
        modeladmin (admin.ModelAdmin): The admin.ModelAdmin instance that called this action.
        request (HttpRequest): The current request object.
        queryset (QuerySet): The queryset of objects selected by the user.

    Note:
        - https://stackoverflow.com/questions/67979442/how-do-i-find-the-class-that-relatedmanager-is-managing-when-the-queryset-is-emp
    '''

    _caller = modeladmin.model.__name__  ## 'User'/'Router'/...  (-> is str)
    if _caller == 'User':
        active_objects = queryset.filter(is_active=True)
    else:
        active_objects = queryset.filter(active=True)

    count = active_objects.count()

    if count:
        if _caller == 'User':
            active_objects.update(is_active=False)
        else:
            active_objects.update(active=False)

        modeladmin.message_user(
            request,
            f'{count} made inactive'
        )


# -----------------
## functions used in django custom commands


def abort(self, text: Optional[str] = None) -> None:
    print()
    if text:
        print(colorize(self, 'error', text))
    print(colorize(self, 'error', 'aborting...'))
    print()

def add_yearmonthday_force(parser, for_mysql: bool = False) -> None:
    ## __DATABASE_YMD_PATTERN__

    if for_mysql:
        help_msg = 'year-month(s) in YYYY_MM format, e.g. 2024_12 or 2024_05 2024_07 2024_11'
    else:
        help_msg = 'year-month(s) in YYYY-MM format, e.g. 2024-12 or 2024-05 2024-07 2024-11'
    parser.add_argument(
        # '-x',  ## JUMP_2 commented due to lack of a proper name for it
        '--year-months',
        default=[],
        nargs='+',  ## one or more
        type=str,
        help=help_msg,
    )
    if for_mysql:
        help_msg = 'year-month-day(s) in YYYY_MM_DD format, e.g. 2024_12_03 or 2024_05_09 2024_07_29 2024_11_02'
    else:
        help_msg = 'year-month-day(s) in YYYY-MM-DD format, e.g. 2024-12-03 or 2024-05-09 2024-07-29 2024-11-02'
    parser.add_argument(
        # '-x',  ## JUMP_2
        '--year-month-days',
        default=[],
        nargs='+',  ## one or more
        type=str,
        help=help_msg,
    )

    if for_mysql:
        help_msg = 'start year-month in YYYY_MM format, e.g. 2024_10'
    else:
        help_msg = 'start year-month in YYYY-MM format, e.g. 2024-10'
    parser.add_argument(
        # '-x',  ## JUMP_2
        '--start-year-month',
        default=None,
        type=str,
        help=help_msg,
    )
    if for_mysql:
        help_msg = 'start year-month-day in YYYY_MM_DD format, e.g. 2024_10_30'
    else:
        help_msg = 'start year-month-day in YYYY-MM-DD format, e.g. 2024-10-30'
    parser.add_argument(
        # '-x',  ## JUMP_2
        '--start-year-month-day',
        default=None,
        type=str,
        help=help_msg,
    )

    if for_mysql:
        help_msg = 'end year-month in YYYY_MM format, e.g. 2024_12'
    else:
        help_msg = 'end year-month in YYYY-MM format, e.g. 2024-12'
    parser.add_argument(
        # '-x',  ## JUMP_2
        '--end-year-month',
        default=None,
        type=str,
        help=help_msg,
    )
    if for_mysql:
        help_msg = 'end year-month-day in YYYY_MM_DD format, e.g. 2024_12_15'
    else:
        help_msg = 'end year-month-day in YYYY-MM-DD format, e.g. 2024-12-15'
    parser.add_argument(
        # '-x',  ## JUMP_2
        '--end-year-month-day',
        default=None,
        type=str,
        help=help_msg,
    )

    if for_mysql:
        help_msg = 'force even if compressed'
    else:
        help_msg = 'force even if accomplished'
    parser.add_argument(
        '-f',
        '--force',
        default=False,
        action='store_true',
        help=help_msg,
    )

def colorize(self, mode: str, text: str) -> str:
    if mode == 'already_parsed':  return self.style.SQL_COLTYPE(text)        ## green
    if mode == 'command':         return self.style.HTTP_SERVER_ERROR(text)  ## bold magenta
    if mode == 'country_error':   return self.style.NOTICE(text)             ## red
    if mode == 'country_success': return self.style.SQL_COLTYPE(text)        ## green
    if mode == 'country_warning': return self.style.SQL_KEYWORD(text)        ## yellow
    if mode == 'error':           return self.style.ERROR(text)              ## bold red
    if mode == 'host_name':       return self.style.HTTP_SUCCESS(text)       ## white
    if mode == 'invalid':         return self.style.NOTICE(text)             ## red
    if mode == 'warning':         return self.style.SQL_KEYWORD(text)        ## yellow
    if mode == 'ymdhms':          return self.style.HTTP_NOT_MODIFIED(text)  ## cyan

    if mode in [
        'dropping',
        'removing',
    ]:
        return self.style.SQL_KEYWORD(text)  ## yellow

    if mode in [
        'copying',
        'creating',
    ]:
        return self.style.HTTP_INFO(text)  ## bold white

    if mode in [
        'accomplished_in',
        'compressed_in',
        'done',
        'dropped',
        'fetched_in',
        'parsed_in',
        'removed',
        'success',
        'updated_in',
        'wrote_in',
    ]:
        return self.style.SUCCESS(text)  ## bold green

    return self.style.HTTP_SUCCESS(text)  ## white

def get_command(full_path: str, drop_extention: bool = True) -> str:
    '''
    Extracts the command name from a given full path of a Django custom command.

    Args:
        full_path (str): The full path of the Django custom command file.
        drop_extention (bool, optional): If True, drops the file extension from the command name. Defaults to True.

    Returns:
        str: The command name extracted from the full path.

    Examples:
        >>> get_command('/Foo/BAR/BAZ/commands/parse-dns.py')
        'parse-dns'

        >>> get_command('/Foo/BAR/BAZ/commands/parse-dns.py', drop_extention=False)
        'parse-dns.py'
    '''

    base = path.basename(full_path)  ## parse-dns.py

    if drop_extention:
        root_base, _ = path.splitext(base)  ## parse-dns
        return root_base

    return base

def get_command_log_file(command: str) -> str:
    '''
    Examples:
        >>> get_command_log_file('live-parse')
        '/FOO/BAR/BAZ/live-parse.log'
    '''

    return f'{settings.PROJECT_LOGS_DIR}/{command}.log'

def is_allowed(cmd: str, only: List[str], exclude: List[str]) -> bool:
    '''
    Check if a command is allowed based on inclusion and exclusion lists.

    Args:
        cmd (str): The command to check.
        only (list): List of commands that are explicitly allowed. If this list is not empty, only commands in this list are allowed.
        exclude (List[str]): List of commands that are explicitly disallowed. Commands in this list are not allowed.

    Returns:
        bool: True if the command is allowed, False otherwise.
    '''

    _allowed = True

    ## NOTE do NOT if -> elif
    if only: _allowed = False
    if only    and cmd in only:    _allowed = True
    if exclude and cmd in exclude: _allowed = False

    return _allowed

def keyboard_interrupt_handler(sig_num: int, frame: FrameType) -> None:
    '''
    Handle keyboard interrupt signal (SIGINT).

    This function is intended to be used as a signal handler for the SIGINT signal,
    which is typically triggered by pressing Ctrl+C. When the signal is received,
    it prints a newline character and raises a CommandError to indicate that the
    command was interrupted by the user.

    Args:
        sig_num (int): The signal number.
        frame (FrameType): The current stack frame.

    Raises:
        CommandError: Indicates that the command was interrupted by the user.

    Examples:
        To use this handler, you need to register it with the signal module:

        signal.signal(signal.SIGINT, keyboard_interrupt_handler)

        # Now, pressing Ctrl+C will trigger the handler:
        while True:
            try:
                # Simulate long-running process
                time.sleep(1)
            except CommandError as e:
                print(e)
                break
    '''

    raise CommandError(
        f'\ncommand interrupted by user (signal: {sig_num})',
        returncode=0,
    )

def save_log(self, command: str, host_name: str, dest_file: str, msg: str, echo: bool = True) -> None:
    '''
    Logs a message to a specified file and optionally prints it with colorized output.

    Args:
        command (str): The command that was executed.
        host_name (str): The name of the host where the command was executed.
        dest_file (str): The file path where the log should be saved.
        msg (str): The message to log.
        echo (bool, optional): If True, prints the message to the console with colorized output. Defaults to True.

    Examples:
        save_log(self, 'live-parse', 'abc-def.local', '/FOO/BAR/BAZ/live-parse.log', 'parse accomplished in 5 minutes')
    '''
    ## __HAS_RUST_VERSION__

    ymdhms = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    msg = to_tilda(msg)

    if echo:

        if 'accomplished in' in msg:
            msg_ = colorize(self, 'accomplished_in', msg)

        elif 'wrote in' in msg:
            msg_ = colorize(self, 'wrote_in', msg)

        elif 'parsed in' in msg:
            msg_ = colorize(self, 'parsed_in', msg)

        ## in compressed_parsed.py
        elif 'compressed in' in msg:
            msg_ = colorize(self, 'compressed_in', msg)

        ## in update_snort.py
        elif msg == 'done':
            msg_ = colorize(self, 'done', msg)

        ## in fetch_malicious.py
        elif 'fetched in' in msg:
            msg_ = colorize(self, 'fetched_in', msg)

        ## in update_dns.py
        elif 'updated in' in msg:
            msg_ = colorize(self, 'updated_in', msg)

        ## in rotate.py
        elif 'ERROR' in msg:
            msg_ = colorize(self, 'error', msg)

        ## in rotate.py
        elif 'WARNING' in msg:
            msg_ = colorize(self, 'warning', msg)

        ## in rotate.py
        elif 'removing' in msg:
            msg_ = colorize(self, 'removing', msg)

        ## in rotate.py
        elif 'creating' in msg:
            msg_ = colorize(self, 'creating', msg)

        elif 'dropping' in msg:
            msg_ = colorize(self, 'dropping', msg)

        elif 'copying' in msg:
            msg_ = colorize(self, 'copying', msg)

        else:
            msg_ = msg

        print(f"{colorize(self, 'host_name', host_name)} {colorize(self, 'command', command)} {colorize(self, 'ymdhms', ymdhms)} {msg_}")

    with open(dest_file, 'a') as opened:
        opened.write(f'{ymdhms} {msg}\n')
