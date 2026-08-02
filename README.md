# rahavard

Re-Usable Python utilities for Django projects — date/time conversion (Gregorian ↔ Jalali),
Persian text & number helpers, pagination, admin shortcuts, and Django custom-command helpers.

## Features

- **Jalali / Persian dates** — convert Unix timestamps and `datetime` objects to Jalali (Persian)
  calendar strings, with optional explicit timezone support.
- **Persian numbers** — convert numbers to Persian digits (`persianize`), format Persian numbers
  with thousand separators (`intcomma_persian`), normalize Arabic letter variants
  (`normalize_persian_text`), and convert Persian/Arabic digits back to English (`to_english_digits`).
- **Human-readable sizes & durations** — `convert_byte` (B → YB, latin or Persian suffixes) and
  `convert_second` / `convert_millisecond` (verbose or compact `HH:MM:SS` style).
- **Django admin helpers** — `make_active` / `make_inactive` bulk actions, `ActiveObjects` manager,
  and reusable `list_display` / `readonly_fields` constants.
- **Django views** — HTMX detection (`comes_from_htmx`), client IP extraction (`get_client_ip`),
  empty 204 responses (`create_empty_response`), live Jalali clock (`get_date_time_live`).
- **Django custom commands** — `colorize` output, `save_log` / `get_command_log_file`,
  `add_yearmonthday_force` CLI args, `keyboard_interrupt_handler`, `abort`.
- **General utilities** — `truncate_text`, `sort_dict` (natural sort, value/key modes with
  key-ascending tie-breaks), `get_list_of_files`, `calculate_offset`, `create_short_uuid`,
  `html_to_plain_text`, `is_int_or_float`, and more.

## Installation

```bash
pip install -e .
# or with dev/test dependencies:
pip install -e ".[dev]"
```

Requires Python 3.9+ and Django.

## Quick usage

```python
from rahavard import (
    convert_to_jalali,
    convert_timestamp_to_jalali,
    get_client_ip,
    normalize_persian_text,
    persianize,
    truncate_text,
)

# Jalali conversion (host-timezone independent with an explicit tz)
convert_timestamp_to_jalali(1682598113)                       # 'پنجشنبه ... ۱۴۰۲/۰۲/۰۷'
convert_to_jalali(datetime(2023, 4, 27, 15, 51, 53))          # 'پنجشنبه ۱۵:۵۱:۵۳ ۱۴۰۲/۰۲/۰۷'

# Persian number helpers
persianize(1234567.89)                                        # '۱۲۳۴۵۶۷.۸۹'
normalize_persian_text('يك كتاب خوب')                         # 'یک کتاب خوب'

# Django views
client_ip = get_client_ip(request)                            # X-Forwarded-For aware

# Text helpers
truncate_text('The quick brown fox', 14)                      # 'The quick...'
```

## Development

Run the test suite (no external services needed):

```bash
pip install -e ".[dev]"
pytest
```

Tests live in `rahavard/test_utils.py` and cover all public utilities, including
edge cases (invalid inputs, huge byte sizes, string-value sorting, missing env vars).

## License

MIT — see [LICENSE](LICENSE).
