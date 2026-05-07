'''
run:
~/main/pypi/rahavard/venv/bin/pytest \
~/main/pypi/rahavard/rahavard/test_utils.py
'''

from django.conf import settings

from datetime import datetime as dt

import pytest

from .utils import (
    calculate_offset,
    contains_ymd,
    convert_byte,
    convert_millisecond,
    convert_second,
    convert_string_True_False_None_0,
    convert_timestamp_to_jalali,
    convert_to_jalali,
    convert_to_second,
    create_id_for_htmx_indicator,
    get_command,
    get_command_log_file,
    get_percent,
    html_to_plain_text,
    intcomma_persian,
    is_int_or_float,
    is_ymd,
    persianize,
    sort_dict,
    starts_with_ymdhms,
)


class TestCalculateOffset:
    @pytest.mark.parametrize('page, limit, expected', [
        (1, 25, 0),
        (2, 25, 25),
        (3, 10, 20),
        (1, 1, 0),
        (5, 20, 80),
    ])
    def test_valid_cases(self, page, limit, expected):
        assert calculate_offset(page, limit) == expected

    @pytest.mark.parametrize('page, limit, expected', [
        (1, 0, 0),
        (2, 0, 0),
        (10, 0, 0),
    ])
    def test_zero_limit(self, page, limit, expected):
        assert calculate_offset(page, limit) == expected

    @pytest.mark.parametrize('page, limit, expected', [
        (1000, 100, 99900),
        (10**6, 10, 9999990),
    ])
    def test_large_values(self, page, limit, expected):
        assert calculate_offset(page, limit) == expected


class TestContainsYMD:
    @pytest.mark.parametrize('value', [
        '2023-10-05',
        "Today's date is 2023-10-05.",
        'prefix 2023-01-01 suffix',
        '2023-12-31 end',
        '2023-10-05T12:00:00',
        '[2023-10-05]',
        'date=2023-10-05;',
    ])
    def test_valid_matches(self, value):
        assert contains_ymd(value) is True

    @pytest.mark.parametrize('value', [
        '',
        'no date here',
        '2023/10/05',  ## wrong separator
        '05-10-2023',  ## wrong order
        '2023-1-05',   ## not zero-padded
        '2023-10-5',   ## not zero-padded
        '20231005',    ## no separators
        '2023-10',     ## partial
        '10-05',       ## partial
        '2023-',       ## partial
        '-10-05',      ## partial
    ])
    def test_invalid_formats(self, value):
        assert contains_ymd(value) is False

    @pytest.mark.parametrize('value', [
        'abcd-ef-gh',
        '----',
        '2023--10-05',
        '2023-10--05',
    ])
    def test_garbage(self, value):
        assert contains_ymd(value) is False


class TestConvertByte:
    @pytest.mark.parametrize('value', [None, 'abc', [], {}, object()])
    def test_invalid_inputs(self, value):
        assert convert_byte(value) == '0B'
        assert convert_byte(value, to_persian=True) == '۰ بایت'

    def test_zero(self):
        assert convert_byte(0) == '0B'
        assert convert_byte(0, to_persian=True) == '۰ بایت'

    @pytest.mark.parametrize('value, expected', [
        (1, '1B'),
        (512, '512B'),
        (1023, '1023B'),
    ])
    def test_bytes(self, value, expected):
        assert convert_byte(value) == expected

    @pytest.mark.parametrize('value, expected', [
        (1024, '1KB'),
        (2048, '2KB'),
        (1536, '1.5KB'),
    ])
    def test_kilobytes(self, value, expected):
        assert convert_byte(value) == expected

    @pytest.mark.parametrize('value, expected', [
        (1048576, '1MB'),
        (2097152, '2MB'),
        (1572864, '1.5MB'),
    ])
    def test_megabytes(self, value, expected):
        assert convert_byte(value) == expected

    @pytest.mark.parametrize('value, expected', [
        (1073741824, '1GB'),
        (2147483648, '2GB'),
    ])
    def test_gigabytes(self, value, expected):
        assert convert_byte(value) == expected

    @pytest.mark.parametrize('value, expected', [
        (1099511627776, '1TB'),
    ])
    def test_terabytes(self, value, expected):
        assert convert_byte(value) == expected

    @pytest.mark.parametrize('value, expected', [
        (1024, '۱ کیلوبایت'),
        (1536, '۱.۵ کیلوبایت'),
        (1048576, '۱ مگابایت'),
    ])
    def test_persian_output(self, value, expected):
        assert convert_byte(value, to_persian=True) == expected

    def test_no_trailing_decimal(self):
        assert convert_byte(1024) == '1KB'
        assert convert_byte(1048576) == '1MB'

    def test_float_input(self):
        assert convert_byte(1024.0) == '1KB'
        assert convert_byte(1536.0) == '1.5KB'

    @pytest.mark.parametrize('value, expected', [
        (1024**5, '1PB'),
        (1024**6, '1EB'),
    ])
    def test_large_values(self, value, expected):
        assert convert_byte(value) == expected


class TestConvertMillisecond:
    @pytest.mark.parametrize('value', [None, 'abc', [], {}, object()])
    def test_invalid_inputs(self, value):
        assert convert_millisecond(value) == '0'
        assert convert_millisecond(value, verbose=False) == '0:00'

    def test_zero(self):
        assert convert_millisecond(0) == '0'
        assert convert_millisecond(0, verbose=False) == '0:00'

    @pytest.mark.parametrize('value', [0.1, 0.5, 0.999])
    def test_less_than_one_millisecond(self, value):
        ## still < 1 second after conversion
        assert convert_millisecond(value) == '~0'
        assert convert_millisecond(value, verbose=False) == '~0:00'

    @pytest.mark.parametrize('ms', [
        1000,
        2000,
        59000,
        60000,
        3600000,
    ])
    def test_matches_convert_second(self, ms):
        assert convert_millisecond(ms) == convert_second(ms / 1000)
        assert convert_millisecond(ms, verbose=False) == convert_second(ms / 1000, verbose=False)

    def test_float_input(self):
        assert convert_millisecond(1000.0) == '1 sec'
        assert convert_millisecond(1500.0, verbose=False) == convert_second(1.5, verbose=False)

    @pytest.mark.parametrize('ms, expected', [
        (1000, '1 sec'),
        (2000, '2 secs'),
        (60000, '1 min'),
    ])
    def test_basic_values(self, ms, expected):
        assert convert_millisecond(ms) == expected

    def test_consistency_with_seconds(self):
        for ms in [1, 999, 1000, 61000, 3661000]:
            assert convert_millisecond(ms) == convert_second(ms / 1000)


class TestConvertSecond:
    @pytest.mark.parametrize('value', [None, 'abc', [], {}, object()])
    def test_invalid_inputs(self, value):
        assert convert_second(value) == '0'
        assert convert_second(value, verbose=False) == '0:00'

    def test_zero(self):
        assert convert_second(0) == '0'
        assert convert_second(0, verbose=False) == '0:00'

    @pytest.mark.parametrize('value', [0.1, 0.56, 0.999])
    def test_less_than_one(self, value):
        assert convert_second(value) == '~0'
        assert convert_second(value, verbose=False) == '~0:00'

    @pytest.mark.parametrize('seconds, verbose, expected', [
        (1, True, '1 sec'),
        (2, True, '2 secs'),
        (59, True, '59 secs'),
        (1, False, '0:01'),
        (59, False, '0:59'),
    ])
    def test_seconds_only(self, seconds, verbose, expected):
        assert convert_second(seconds, verbose) == expected

    @pytest.mark.parametrize('seconds, verbose, expected', [
        (60, True, '1 min'),
        (61, True, '1 min and 1 sec'),
        (120, True, '2 mins'),
        (125, True, '2 mins and 5 secs'),
        (60, False, '1:00'),
        (61, False, '1:01'),
    ])
    def test_minutes(self, seconds, verbose, expected):
        assert convert_second(seconds, verbose) == expected

    @pytest.mark.parametrize('seconds, verbose, expected', [
        (3600, True, '1 hr'),
        (3661, True, '1 hr, 1 min and 1 sec'),
        (7200, True, '2 hrs'),
        (3600, False, '1:00:00'),
        (3661, False, '1:01:01'),
    ])
    def test_hours(self, seconds, verbose, expected):
        assert convert_second(seconds, verbose) == expected

    @pytest.mark.parametrize('seconds, verbose, expected', [
        (86400, True, '1 day'),
        (90000, True, '1 day and 1 hr'),
        (172800, True, '2 days'),
        (86400, False, '1:00:00:00'),
    ])
    def test_days(self, seconds, verbose, expected):
        assert convert_second(seconds, verbose) == expected

    @pytest.mark.parametrize('seconds, verbose, expected', [
        (2592000, True, '1 month'),  ## 30 days
        (2678400, True, '1 month and 1 day'),
        (5184000, True, '2 months'),
        (2592000, False, '1:00:00:00:00'),
    ])
    def test_months(self, seconds, verbose, expected):
        assert convert_second(seconds, verbose) == expected

    @pytest.mark.parametrize('seconds, verbose, expected', [
        (31536000, True, '1 year and 5 days'),
        (63072000, True, '2 years and 10 days'),
        (31536000, False, '1:00:05:00:00:00'),
    ])
    def test_years(self, seconds, verbose, expected):
        assert convert_second(seconds, verbose) == expected

    @pytest.mark.parametrize('seconds, verbose, expected', [
        (40000000, True, '1 year, 3 months and 12 days'),
        (40000000, False, '1:03:12:23:06:40'),
    ])
    def test_large_mixed(self, seconds, verbose, expected):
        assert convert_second(seconds, verbose) == expected

    def test_no_leading_zero_verbose(self):
        assert not convert_second(3600).startswith('0')

    def test_no_leading_zero_compact(self):
        assert convert_second(61, verbose=False) == '1:01'

    def test_pluralization(self):
        assert convert_second(1) == '1 sec'
        assert convert_second(2) == '2 secs'
        assert convert_second(60) == '1 min'
        assert convert_second(120) == '2 mins'

    @pytest.mark.parametrize('seconds, expected', [
        (59, '59 secs'),
        (60, '1 min'),
        (3599, '59 mins and 59 secs'),
        (3600, '1 hr'),
        (86399, '23 hrs, 59 mins and 59 secs'),
        (86400, '1 day'),
    ])
    def test_boundaries(self, seconds, expected):
        assert convert_second(seconds) == expected


class TestConvertStringTrueFalseNone0:
    @pytest.mark.parametrize('value, expected', [
        ('True', True),
        ('False', False),
        ('None', None),
        ('0', 0),
    ])
    def test_valid_conversions(self, value, expected):
        assert convert_string_True_False_None_0(value) == expected

    @pytest.mark.parametrize('value', [
        '',
        'true',   ## case-sensitive
        'false',
        'none',
        '00',
        '1',
        'True ',
        ' False',
        'None\n',
        ' 0 ',
        'yes',
        'no',
        'null',
        'undefined',
        'Hello',
    ])
    def test_non_matching_strings(self, value):
        assert convert_string_True_False_None_0(value) == value

    def test_type_preservation_for_non_matching(self):
        value = 'random_string'
        result = convert_string_True_False_None_0(value)
        assert isinstance(result, str)
        assert result == value

    def test_exact_match_only(self):
        assert convert_string_True_False_None_0('Truex') == 'Truex'
        assert convert_string_True_False_None_0('xTrue') == 'xTrue'
        assert convert_string_True_False_None_0('False!') == 'False!'
        assert convert_string_True_False_None_0('[None]') == '[None]'


class TestConvertTimestampToJalali:
    def test_none(self):
        assert convert_timestamp_to_jalali() == ''

    @pytest.mark.parametrize('value', [0, None, False])
    def test_falsy_inputs(self, value):
        assert convert_timestamp_to_jalali(value) == ''

    def test_valid_timestamp_structure(self):
        result = convert_timestamp_to_jalali(1682598113)

        ## expected structure:
        ## 'weekday hh:mm:ss yyyy/mm/dd' (all persian digits except weekday)
        parts = result.split(' ')
        assert len(parts) == 3

        weekday, time_part, date_part = parts

        assert weekday  ## non-empty

        ## check time format
        t = time_part.split(':')
        assert len(t) == 3
        assert all(len(x) == 2 for x in t)

        ## check date format
        d = date_part.split('/')
        assert len(d) == 3
        assert all(len(x) >= 2 for x in d)

    def test_persian_digits(self):
        result = convert_timestamp_to_jalali(1682598113)

        ## ensure no english digits present
        for ch in '0123456789':
            assert ch not in result

    def test_different_timestamps(self):
        r1 = convert_timestamp_to_jalali(1682598113)
        r2 = convert_timestamp_to_jalali(1682598114)
        assert not r1 == r2

    def test_int_casting(self):
        assert convert_timestamp_to_jalali(1682598113.0) == convert_timestamp_to_jalali(1682598113)

    def test_large_timestamp(self):
        result = convert_timestamp_to_jalali(32503680000)  ## year 3000
        assert isinstance(result, str)
        assert not result == ''

    def test_no_extra_spaces(self):
        result = convert_timestamp_to_jalali(1682598113)
        assert result == result.strip()
        assert '  ' not in result

    def test_literal_jalali(self):
        assert convert_timestamp_to_jalali(1682598113) == 'پنج‌شنبه ۱۵:۵۱:۵۳ ۱۴۰۲/۰۲/۰۷'


class TestConvertToJalali:
    def test_none(self):
        assert convert_to_jalali() == ''

    @pytest.mark.parametrize('value', [None, False])
    def test_falsy_inputs(self, value):
        assert convert_to_jalali(value) == ''

    def test_valid_datetime_structure(self):
        from datetime import datetime

        result = convert_to_jalali(datetime(2023, 4, 27, 15, 51, 53))

        ## expected structure:
        ## 'weekday hh:mm:ss yyyy/mm/dd' (all persian digits except weekday)
        parts = result.split(' ')
        assert len(parts) == 3

        weekday, time_part, date_part = parts

        assert weekday  ## non-empty

        ## check time format
        t = time_part.split(':')
        assert len(t) == 3
        assert all(len(x) == 2 for x in t)

        ## check date format
        d = date_part.split('/')
        assert len(d) == 3
        assert all(len(x) >= 2 for x in d)

    def test_persian_digits(self):
        from datetime import datetime

        result = convert_to_jalali(datetime(2023, 4, 27, 15, 51, 53))

        ## ensure no english digits present
        for ch in '0123456789':
            assert ch not in result

    def test_different_datetimes(self):
        from datetime import datetime

        r1 = convert_to_jalali(datetime(2023, 4, 27, 15, 51, 53))
        r2 = convert_to_jalali(datetime(2023, 4, 27, 15, 51, 54))

        assert not r1 == r2

    def test_no_extra_spaces(self):
        from datetime import datetime

        result = convert_to_jalali(datetime(2023, 4, 27, 15, 51, 53))

        assert result == result.strip()
        assert '  ' not in result

    def test_literal_jalali(self):
        from datetime import datetime

        assert convert_to_jalali(datetime(2023, 4, 27, 15, 51, 53)) == 'پنج‌شنبه ۱۵:۵۱:۵۳ ۱۴۰۲/۰۲/۰۷'

    def test_leap_year(self):
        from datetime import datetime

        result = convert_to_jalali(datetime(2020, 2, 29, 12, 0, 0))

        assert isinstance(result, str)
        assert not result == ''

    def test_microseconds_ignored(self):
        from datetime import datetime

        r1 = convert_to_jalali(datetime(2023, 4, 27, 15, 51, 53, 0))
        r2 = convert_to_jalali(datetime(2023, 4, 27, 15, 51, 53, 999999))

        assert r1 == r2

    def test_old_date(self):
        from datetime import datetime

        result = convert_to_jalali(datetime(1970, 1, 1, 0, 0, 0))

        assert isinstance(result, str)
        assert not result == ''

    def test_future_date(self):
        from datetime import datetime

        result = convert_to_jalali(datetime(3000, 1, 1, 0, 0, 0))

        assert isinstance(result, str)
        assert not result == ''


class TestConvertToSecond:
    @pytest.mark.parametrize('value', [None, 0, '2023-01-01', [], {}, object()])
    def test_invalid_inputs(self, value):
        with pytest.raises(Exception):
            convert_to_second(value)

    def test_epoch_type(self):
        result = convert_to_second(dt(1970, 1, 1, 0, 0, 0))

        assert isinstance(result, int)

    def test_known_values(self):
        d1 = dt(2000, 1, 1, 0, 0, 0)
        d2 = dt(2000, 1, 1, 0, 0, 1)

        assert convert_to_second(d2) - convert_to_second(d1) == 1

    def test_return_type(self):
        result = convert_to_second(dt(2023, 1, 1, 0, 0, 0))
        assert isinstance(result, int)

    def test_microseconds_are_truncated(self):
        d1 = dt(2023, 1, 1, 0, 0, 0, 0)
        d2 = dt(2023, 1, 1, 0, 0, 0, 999999)

        assert convert_to_second(d1) == convert_to_second(d2)

    def test_sequential_seconds(self):
        d1 = dt(2023, 1, 1, 0, 0, 0)
        d2 = dt(2023, 1, 1, 0, 0, 1)

        assert convert_to_second(d2) - convert_to_second(d1) == 1

    def test_large_future_date(self):
        result = convert_to_second(dt(3000, 1, 1, 0, 0, 0))

        assert isinstance(result, int)
        assert result > 0

    def test_consistency(self):
        date_obj = dt(2023, 5, 1, 10, 20, 30)

        r1 = convert_to_second(date_obj)
        r2 = convert_to_second(date_obj)

        assert r1 == r2

    def test_matches_datetime_timestamp(self):
        date_obj = dt(2023, 10, 26, 12, 0, 0)

        assert convert_to_second(date_obj) == int(date_obj.timestamp())


class TestCreateIdForHtmxIndicator:
    @pytest.mark.parametrize('args, expected', [
        (('tops',), 'tops--htmx-indicator'),
        (
            ('by-date', 'source-ip', '2024-06-30'),
            'by-date-source-ip-2024-06-30--htmx-indicator'
        ),
        (
            ('user', 'profile', 'edit'),
            'user-profile-edit--htmx-indicator'
        ),
    ])
    def test_valid_cases(self, args, expected):
        assert create_id_for_htmx_indicator(*args) == expected

    def test_no_args(self):
        assert create_id_for_htmx_indicator() == '--htmx-indicator'

    @pytest.mark.parametrize('args, expected', [
        (
            ('a--b',),
            'a--b--htmx-indicator'
        ),
        (
            ('a---b',),
            'a--b--htmx-indicator'
        ),
        (
            ('a----b',),
            'a--b--htmx-indicator'
        ),
        (
            ('a', '--', 'b'),
            'a--b--htmx-indicator'
        ),
    ])
    def test_hyphen_normalization(self, args, expected):
        assert create_id_for_htmx_indicator(*args) == expected

    @pytest.mark.parametrize('args, expected', [
        (
            ('',),
            '--htmx-indicator'
        ),
        (
            ('', 'tops'),
            '-tops--htmx-indicator'
        ),
        (
            ('tops', ''),
            'tops--htmx-indicator'
        ),
        (
            ('', '', ''),
            '--htmx-indicator'
        ),
    ])
    def test_empty_strings(self, args, expected):
        assert create_id_for_htmx_indicator(*args) == expected

    @pytest.mark.parametrize('args', [
        ('simple',),
        ('a', 'b', 'c'),
        ('with-dash', 'another-value'),
    ])
    def test_suffix_always_present(self, args):
        result = create_id_for_htmx_indicator(*args)
        assert result.endswith('--htmx-indicator')

    def test_return_type(self):
        result = create_id_for_htmx_indicator('test')
        assert isinstance(result, str)

    def test_preserves_double_hyphen(self):
        result = create_id_for_htmx_indicator('a--b')
        assert '---' not in result
        assert result == 'a--b--htmx-indicator'

    def test_large_number_of_args(self):
        args = tuple(f'v{i}' for i in range(100))

        result = create_id_for_htmx_indicator(*args)

        assert result.startswith('v0-v1-v2')
        assert result.endswith('--htmx-indicator')
        assert 'v99' in result


class TestGetCommand:
    @pytest.mark.parametrize('full_path, expected', [
        ('/Foo/BAR/BAZ/commands/parse-dns.py', 'parse-dns'),
        ('/tmp/test/example.txt', 'example'),
        ('relative/path/to/script.sh', 'script'),
        ('command.py', 'command'),
        ('/a/b/c/my-command', 'my-command'),
    ])
    def test_drop_extension_default(self, full_path, expected):
        assert get_command(full_path) == expected

    @pytest.mark.parametrize('full_path, expected', [
        ('/Foo/BAR/BAZ/commands/parse-dns.py', 'parse-dns.py'),
        ('/tmp/test/example.txt', 'example.txt'),
        ('relative/path/to/script.sh', 'script.sh'),
        ('command.py', 'command.py'),
        ('/a/b/c/my-command', 'my-command'),
    ])
    def test_keep_extension(self, full_path, expected):
        assert get_command(full_path, drop_extention=False) == expected

    @pytest.mark.parametrize('full_path, expected', [
        ('archive.tar.gz', 'archive.tar'),
        ('/tmp/archive.tar.gz', 'archive.tar'),
        ('/tmp/.env', '.env'),
        ('/tmp/.env.local', '.env'),
    ])
    def test_multiple_and_hidden_extensions(self, full_path, expected):
        assert get_command(full_path) == expected

    @pytest.mark.parametrize('full_path, expected', [
        ('archive.tar.gz', 'archive.tar.gz'),
        ('/tmp/archive.tar.gz', 'archive.tar.gz'),
        ('/tmp/.env', '.env'),
        ('/tmp/.env.local', '.env.local'),
    ])
    def test_multiple_and_hidden_extensions_keep(self, full_path, expected):
        assert get_command(full_path, drop_extention=False) == expected

    def test_empty_path(self):
        assert get_command('') == ''
        assert get_command('', drop_extention=False) == ''

    def test_directory_path(self):
        assert get_command('/tmp/foo/') == ''
        assert get_command('/tmp/foo/', drop_extention=False) == ''


class TestGetCommandLogFile:
    @pytest.fixture(autouse=True)
    def configure_settings(self):
        if not settings.configured:
            settings.configure(PROJECT_LOGS_DIR='/FOO/BAR/BAZ')

    @pytest.mark.parametrize('command, expected', [
        ('live-parse', '/FOO/BAR/BAZ/live-parse.log'),
        ('sync_data', '/FOO/BAR/BAZ/sync_data.log'),
        ('backup', '/FOO/BAR/BAZ/backup.log'),
    ])
    def test_valid_commands(self, command, expected):
        assert get_command_log_file(command) == expected

    def test_empty_command(self):
        assert get_command_log_file('') == '/FOO/BAR/BAZ/.log'

    def test_command_with_extension(self):
        assert get_command_log_file('parse.py') == '/FOO/BAR/BAZ/parse.py.log'

    def test_command_with_spaces(self):
        assert get_command_log_file('my command') == '/FOO/BAR/BAZ/my command.log'


class TestGetPercent:
    @pytest.mark.parametrize('smaller_number, total_number', [
        (0, 100),
        (100, 0),
        (0, 0),
        (0.0, 100),
        (100, 0.0),
    ])
    def test_zero_inputs(self, smaller_number, total_number):
        assert get_percent(smaller_number, total_number) == '0'
        assert get_percent(
            smaller_number,
            total_number,
            to_persian=True,
        ) == '۰'

    @pytest.mark.parametrize('smaller_number, total_number, expected', [
        (25, 100, '25'),
        (1, 100, '1'),
        (50, 200, '25'),
        (5, 10, '50'),
        (100, 100, '100'),
    ])
    def test_integer_percentages(
        self,
        smaller_number,
        total_number,
        expected,
    ):
        assert get_percent(smaller_number, total_number) == expected

    @pytest.mark.parametrize('smaller_number, total_number, expected', [
        (99.95232355216523, 100, '99.9'),
        (1, 3, '33.3'),
        (2, 3, '66.6'),
        (10, 6, '166.6'),
        (15.5, 20, '77.5'),
    ])
    def test_decimal_percentages(
        self,
        smaller_number,
        total_number,
        expected,
    ):
        assert get_percent(smaller_number, total_number) == expected

    @pytest.mark.parametrize('smaller_number, total_number', [
        (0.1, 100),
        (0.5, 1000),
        (0.99, 1000),
    ])
    def test_less_than_one_percent(self, smaller_number, total_number):
        assert get_percent(smaller_number, total_number) == '~0'
        assert get_percent(
            smaller_number,
            total_number,
            to_persian=True,
        ) == '~۰'

    @pytest.mark.parametrize('smaller_number, total_number, expected', [
        (25, 100, '۲۵'),
        (1, 100, '۱'),
        (99.95232355216523, 100, '۹۹.۹'),
        (15.5, 20, '۷۷.۵'),
    ])
    def test_persian_output(
        self,
        smaller_number,
        total_number,
        expected,
    ):
        assert get_percent(
            smaller_number,
            total_number,
            to_persian=True,
        ) == expected

    def test_no_trailing_decimal_zero(self):
        assert get_percent(97, 100) == '97'
        assert get_percent(50, 100) == '50'

    def test_float_inputs(self):
        assert get_percent(25.0, 100.0) == '25'
        assert get_percent(12.5, 50.0) == '25'

    @pytest.mark.parametrize('smaller_number, total_number, expected', [
        (1, 9999999, '~0'),
        (9999999, 9999999, '100'),
        (999999, 1000000, '99.9'),
    ])
    def test_large_values(
        self,
        smaller_number,
        total_number,
        expected,
    ):
        assert get_percent(
            smaller_number,
            total_number,
        ) == expected

    def test_return_type(self):
        assert isinstance(get_percent(25, 100), str)
        assert isinstance(
            get_percent(25, 100, to_persian=True),
            str,
        )

    def test_no_rounding_to_hundred(self):
        ## ensure truncation instead of rounding
        assert get_percent(99.999, 100) == '99.9'


class TestHtmlToPlainText:
    @pytest.mark.parametrize('value, expected', [
        ('', ''),
        ('Hello World', 'Hello World'),
        ('<p>Hello World</p>', 'Hello World'),
        ('<p>Hello<b>World</b></p>', 'Hello World'),
        ('<div>Hello <span>World</span></div>', 'Hello  World'),
        ('<h1>Title</h1><p>Description</p>', 'Title Description'),
    ])
    def test_basic_cases(self, value, expected):
        assert html_to_plain_text(value) == expected

    @pytest.mark.parametrize('value, expected', [
        ('<p>Hello<br>World</p>', 'Hello World'),
        ('<ul><li>One</li><li>Two</li></ul>', 'One Two'),
        ('<table><tr><td>A</td><td>B</td></tr></table>', 'A B'),
    ])
    def test_nested_and_structured_tags(self, value, expected):
        assert html_to_plain_text(value) == expected

    @pytest.mark.parametrize('value, expected', [
        ('<p>  Hello   World  </p>', 'Hello   World'),
        ('   <b>Hello</b>   ', 'Hello'),
    ])
    def test_whitespace_handling(self, value, expected):
        assert html_to_plain_text(value) == expected

    @pytest.mark.parametrize('value, expected', [
        ('&nbsp;', ''),
        ('&lt;b&gt;Hello&lt;/b&gt;', '<b>Hello</b>'),
        ('Tom &amp; Jerry', 'Tom & Jerry'),
    ])
    def test_html_entities(self, value, expected):
        assert html_to_plain_text(value) == expected

    def test_script_tag(self):
        value = '<script>alert("x")</script><p>Hello</p>'
        assert html_to_plain_text(value) == 'Hello'

    def test_style_tag(self):
        value = '<style>body{color:red}</style><p>Hello</p>'
        assert html_to_plain_text(value) == 'Hello'

    def test_comments(self):
        value = '<!-- comment --><p>Hello</p>'
        assert html_to_plain_text(value) == 'Hello'

    def test_unicode_text(self):
        value = '<p>سلام <b>دنیا</b></p>'
        assert html_to_plain_text(value) == 'سلام  دنیا'

    def test_malformed_html(self):
        value = '<p>Hello<b>World'
        assert html_to_plain_text(value) == 'Hello World'

    def test_only_tags(self):
        assert html_to_plain_text('<div><br></div>') == ''

    def test_no_extra_spaces(self):
        result = html_to_plain_text('<p>Hello <b>World</b></p>')
        assert result == result.strip()
        assert '  ' in result


class TestIntcommaPersian:
    @pytest.mark.parametrize('value, expected', [
        ('۰', '۰'),
        ('۱۲', '۱۲'),
        ('۱۲۳', '۱۲۳'),
        ('۱۲۳۴', '۱،۲۳۴'),
        ('۱۲۳۴۵', '۱۲،۳۴۵'),
        ('۱۲۳۴۵۶', '۱۲۳،۴۵۶'),
        ('۱۲۳۴۵۶۷', '۱،۲۳۴،۵۶۷'),
        ('۱۲۳۴۵۶۷۸۹', '۱۲۳،۴۵۶،۷۸۹'),
    ])
    def test_integer_grouping(self, value, expected):
        assert intcomma_persian(value) == expected

    @pytest.mark.parametrize('value, expected', [
        ('۱۲۳۴۵۶۷۸۹.۱۲۳۴۵۶۷۸۹', '۱۲۳،۴۵۶،۷۸۹.۱۲۳۴۵۶۷۸۹'),
        ('۱.۱۲۳۴۵۶', '۱.۱۲۳۴۵۶'),
        ('۱۲۳۴.۵۶', '۱،۲۳۴.۵۶'),
        ('۱۲۳۴۵۶۷.۸۹', '۱،۲۳۴،۵۶۷.۸۹'),
    ])
    def test_float_dot_format(self, value, expected):
        assert intcomma_persian(value) == expected

    @pytest.mark.parametrize('value, expected', [
        ('۱۲۳۴۵۶۷۸۹/۱۲۳۴۵۶۷۸۹', '۱۲۳،۴۵۶،۷۸۹/۱۲۳۴۵۶۷۸۹'),
        ('۱۲۳۴/۵۶', '۱،۲۳۴/۵۶'),
        ('۱/۲', '۱/۲'),
    ])
    def test_slash_format(self, value, expected):
        assert intcomma_persian(value) == expected

    @pytest.mark.parametrize('value', [
        '',
        'abc',
        '۱۲۳abc۴۵۶',
    ])
    def test_non_numeric_or_mixed_input(self, value):
        ## function does not validate input; it formats raw string grouping on left side
        result = intcomma_persian(value)
        assert isinstance(result, str)
        assert result is not None

    def test_no_trailing_comma(self):
        assert intcomma_persian('۱') == '۱'
        assert intcomma_persian('۱۲۳') == '۱۲۳'

    def test_preserves_input_structure_float_vs_slash(self):
        assert '.' in intcomma_persian('۱۲۳۴۵۶.۷۸۹')
        assert '/' in intcomma_persian('۱۲۳۴۵۶/۷۸۹')


class TestIsIntOrFloat:
    @pytest.mark.parametrize('value', [
        '123',
        '0',
        '456789',
    ])
    def test_valid_int_strings(self, value):
        assert is_int_or_float(value) is True

    @pytest.mark.parametrize('value', [
        '123.456',
        '0.0',
        '10.5',
    ])
    def test_valid_float_strings(self, value):
        assert is_int_or_float(value) is True

    @pytest.mark.parametrize('value, expected', [
        (123, True),
        (123.456, True),
        (0, True),
        (0.0, True),
    ])
    def test_numeric_inputs(self, value, expected):
        assert is_int_or_float(value) == expected

    @pytest.mark.parametrize('value', [
        '',
        'abc',
        '123abc',
        'abc123',
        None,
        True,
        False,
    ])
    def test_invalid_basic_cases(self, value):
        assert is_int_or_float(value) is False

    @pytest.mark.parametrize('value', [
        '-1',
        '+1',
        '-123.45',
        '+123.45',
    ])
    def test_signed_numbers(self, value):
        assert is_int_or_float(value) is False

    @pytest.mark.parametrize('value', [
        ' 123',
        '123 ',
        ' 123.45 ',
    ])
    def test_whitespace_cases(self, value):
        assert is_int_or_float(value) is False

    @pytest.mark.parametrize('value', [
        '1e3',
        '1E3',
        'NaN',
        'inf',
        '-inf',
    ])
    def test_scientific_and_special_notation(self, value):
        assert is_int_or_float(value) is False

    @pytest.mark.parametrize('value', [
        '1.2.3',
        '..123',
        '123..',
    ])
    def test_multiple_dots(self, value):
        assert is_int_or_float(value) is True

    def test_object_input(self):
        assert is_int_or_float(object()) is False


class TestIsYMD:
    @pytest.mark.parametrize('value', [
        '2023-10-05',
        '0000-01-01',
        '9999-12-31',
        '2024-02-29',  ## leap year format (format only, not validation)
    ])
    def test_valid_exact_matches(self, value):
        assert is_ymd(value) is True

    @pytest.mark.parametrize('value', [
        '',
        '2023/10/05',  ## wrong separator
        '05-10-2023',  ## wrong order
        '2023-1-05',   ## not zero-padded
        '2023-10-5',   ## not zero-padded
        '20231005',    ## no separators
        '2023-10',     ## partial
        '10-05',       ## partial
        '2023-',       ## partial
        '-10-05',      ## partial
    ])
    def test_invalid_formats(self, value):
        assert is_ymd(value) is False

    @pytest.mark.parametrize('value', [
        'abcd-ef-gh',
        '----',
        '2023--10-05',
        '2023-10--05',
        '20a3-10-05',
        '2023-1a-05',
        '2023-10-0b',
    ])
    def test_garbage(self, value):
        assert is_ymd(value) is False

    @pytest.mark.parametrize('value', [
        ' 2023-10-05',
        '2023-10-05 ',
        'x2023-10-05',
        '2023-10-05x',
        '[2023-10-05]',
        'date=2023-10-05',
    ])
    def test_not_full_string_match(self, value):
        assert is_ymd(value) is False


class TestPersianize:
    @pytest.mark.parametrize('value, expected', [
        (0, '۰'),
        (1, '۱'),
        (9, '۹'),
        (10, '۱۰'),
        (123, '۱۲۳'),
        (1005, '۱۰۰۵'),
    ])
    def test_integers(self, value, expected):
        assert persianize(value) == expected

    @pytest.mark.parametrize('value, expected', [
        (0.0, '۰'),
        (1.0, '۱'),
        (10.0, '۱۰'),
        (123.0, '۱۲۳'),
        (123.00, '۱۲۳'),
    ])
    def test_float_whole_numbers(self, value, expected):
        assert persianize(value) == expected

    @pytest.mark.parametrize('value, expected', [
        (123.45, '۱۲۳.۴۵'),
        (10.10, '۱۰.۱'),
        (0.12, '۰.۱۲'),
        (99.99, '۹۹.۹۹'),
    ])
    def test_float_two_decimal_digits(self, value, expected):
        assert persianize(value) == expected

    @pytest.mark.parametrize('value, expected', [
        (123.456, '۱۲۳.۴۵'),
        (1.239, '۱.۲۳'),
        (10.9876, '۱۰.۹۸'),
    ])
    def test_float_truncation_not_rounding(self, value, expected):
        assert persianize(value) == expected

    def test_zero_edge_case(self):
        assert persianize(0) == '۰'
        assert persianize(0.0) == '۰'

    def test_large_number(self):
        assert persianize(1000000) == '۱۰۰۰۰۰۰'

    def test_no_trailing_dot_for_integer_float(self):
        assert '.' not in persianize(10.0)
        assert '.' in persianize(10.1)


class TestSortDict:
    def test_sort_by_key_ascending(self):
        data = {'b': 2, 'a': 1, 'c': 3}
        result = sort_dict(data, based_on='key', reverse=False)
        assert list(result.keys()) == ['a', 'b', 'c']

    def test_sort_by_key_descending(self):
        data = {'b': 2, 'a': 1, 'c': 3}
        result = sort_dict(data, based_on='key', reverse=True)
        assert list(result.keys()) == ['c', 'b', 'a']

    def test_sort_by_value_ascending(self):
        data = {'b': 2, 'a': 1, 'c': 3}
        result = sort_dict(data, based_on='value', reverse=False)
        assert list(result.keys()) == ['a', 'b', 'c']

    def test_sort_by_value_descending(self):
        data = {'b': 2, 'a': 1, 'c': 3}
        result = sort_dict(data, based_on='value', reverse=True)
        assert list(result.keys()) == ['c', 'b', 'a']

    def test_value_sort_tie_break_by_key_always_ascending(self):
        data = {'b': 1, 'a': 1, 'c': 1}
        result_asc = sort_dict(data, based_on='value', reverse=False)
        result_desc = sort_dict(data, based_on='value', reverse=True)

        ## tie-break should always enforce key ascending
        assert list(result_asc.keys()) == ['a', 'b', 'c']
        assert list(result_desc.keys()) == ['a', 'b', 'c']

    def test_none_keys_are_normalized_and_sorted(self):
        data = {'b': 2, None: 1, 'a': 3}
        result = sort_dict(data, based_on='key', reverse=False)

        ## None becomes 'None', so lexicographically it comes before 'a' and 'b'
        assert list(result.keys()) == [None, 'a', 'b']

    def test_none_key_reverse_sort(self):
        data = {'b': 2, None: 1, 'a': 3}
        result = sort_dict(data, based_on='key', reverse=True)

        ## reverse lexicographic order: 'b' > 'a' > 'None'
        assert list(result.keys()) == ['b', 'a', None]

    def test_none_values_sorted_by_key_tie_break(self):
        data = {'b': None, 'a': None, 'c': None}
        result = sort_dict(data, based_on='value', reverse=False)

        ## all values equal, so key ascending decides order
        assert list(result.keys()) == ['a', 'b', 'c']

    def test_unknown_based_on_returns_original(self):
        data = {'b': 2, 'a': 1}
        result = sort_dict(data, based_on='unknown', reverse=False)

        assert result == data

    def test_mixed_numeric_values_reverse(self):
        data = {'a': 10, 'b': 2, 'c': 5}
        result = sort_dict(data, based_on='value', reverse=True)

        assert list(result.keys()) == ['a', 'c', 'b']


class TestStartsWithYMDHMS:
    @pytest.mark.parametrize('value', [
        '2023-10-05 12:34:56 Some event',
        '0000-01-01 00:00:00 start',
        '9999-12-31 23:59:59 end',
        '2024-02-29 01:02:03 leap year event',
        '2023-10-05 12:34:56 x',
    ])
    def test_valid_matches(self, value):
        assert starts_with_ymdhms(value) is True

    @pytest.mark.parametrize('value', [
        '',
        '2023-10-05 12:34:56',              ## no trailing space/text
        '2023-10-05 12:34 Some event',      ## missing seconds
        '2023-10-05 Some event',            ## missing time
        '12:34:56 2023-10-05 Some event',   ## wrong order
        'Some event 2023-10-05 12:34:56',   ## not at start
        ' 2023-10-05 12:34:56 Some event',  ## leading space
        '2023-10-05T12:34:56 Some event',   ## wrong separator
        '2023/10/05 12:34:56 Some event',   ## wrong date separator
        '2023-10-05 12-34-56 Some event',   ## wrong time separator
        '2023-1-05 12:34:56 Some event',    ## not zero-padded date
        '2023-10-5 12:34:56 Some event',    ## not zero-padded date
        '2023-10-05 2:34:56 Some event',    ## not zero-padded hour
        '2023-10-05 12:4:56 Some event',    ## not zero-padded minute
        '2023-10-05 12:34:5 Some event',    ## not zero-padded second
    ])
    def test_invalid_formats(self, value):
        assert starts_with_ymdhms(value) is False

    @pytest.mark.parametrize('value', [
        'abcd-ef-gh ij:kl:mn Some event',
        '---- --:--:-- x',
        '2023--10-05 12:34:56 Some event',
        '2023-10--05 12:34:56 Some event',
        '2023-10-05 12:34::56 Some event',
        '2023-10-05 ::12:34:56 Some event',
        '20a3-10-05 12:34:56 Some event',
        '2023-1a-05 12:34:56 Some event',
        '2023-10-0b 12:34:56 Some event',
        '2023-10-05 1a:34:56 Some event',
        '2023-10-05 12:3b:56 Some event',
        '2023-10-05 12:34:5c Some event',
    ])
    def test_garbage(self, value):
        assert starts_with_ymdhms(value) is False

    @pytest.mark.parametrize('value', [
        '2023-10-05 12:34:56Some event',  ## missing space after time
        '[2023-10-05 12:34:56 Some event]',
        'x2023-10-05 12:34:56 Some event',
    ])
    def test_not_strict_start_or_spacing(self, value):
        assert starts_with_ymdhms(value) is False
