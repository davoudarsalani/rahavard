# Useful `django` Commands

<br>

## Import Custom User Model

- In `models.py`:
```
## by-codingentrepreneurs--djangoflix-build-a-netflix-like-service-in-django-and-python/09-1-user-ratings-model.mp4

from django.conf import settings
User = settings.AUTH_USER_MODEL

class Article(models.Model, CommonMethods):
    author = models.ForeignKey(User, ...)
    ...
```

- In `views.py`, `forms.py`, `admins.py`, etc:
```
## by-codingentrepreneurs--djangoflix-build-a-netflix-like-service-in-django-and-python/09-2-test-user-ratings.mp4

from django.contrib.auth import get_user_model

User = get_user_model()
users = User.objects.all()
```

<br>

## A `class` to Be Used Only for Inheritence *(Meaning It Should Be Prevented from Actually Creating a Table in the Database)*

<br>

> [youtube.com](https://www.youtube.com/watch?v=KSPRODsdfo4)

```
class ToBeInherited(models.Model):
    class Meta:
        abstract = True
    name = models.CharField(max_length=50)
    ...
```

<br>

## Reset the Auto-Increment `id` to `1`

<br>

> [dev.to](https://dev.to/chanyayun/django-reset-auto-increment-id-to-1-2j2g)

```
manage.py dbshell
```
```
## get tables
.tables

## reset index
DELETE FROM "<table_name>";
DELETE FROM SQLite_sequence WHERE name="<table_name>";

## method 1.
DELETE FROM "<table_name>"
  WHERE id NOT IN (
    SELECT id FROM "<table_name>"
    WHERE id BETWEEN 1 AND 2  ## 'id BETWEEN 1 AND 2' because two rows were previously added and then deleted
  );

## method 2.
DELETE FROM "<table_name>"
  WHERE id NOT IN (
    SELECT id FROM "<table_name>"
    WHERE id == 1  ## 'id == 1' (because only one row was previously added and then deleted)
  );
```

<br>

## On `cpanel`
```
echo 'from heart.wsgi import application' > passenger_wsgi.py
```

<br>

## User Agent
```
request.META.get('HTTP_USER_AGENT')
```

<br>

## `url`/`uri`

- In `*.html`:

```
{{ request.build_absolute_uri }}  ## https://www.example.com/news/today/?page=2   JUMP_1
{{ request.get_full_path      }}  ##                        /news/today/?page=2
{{ request.path               }}  ##                        /news/today/
{{ request.path_info          }}  ##                        /news/today/
```

- In `*.py`:
```
request.build_absolute_uri()     ## https://www.example.com/news/today/?page=2   JUMP_1
request.build_absolute_uri('?')  ## https://www.example.com/news/today/
request.build_absolute_uri('/')  ## https://www.example.com/

request.build_absolute_uri(reverse('single-url', kwargs={'slug': 'news', 'date': 'today'}))  ## https://www.example.com/news/today/
                           reverse('single-url', kwargs={'slug': 'news', 'date': 'today'})   ##                        /news/today/

absolute_uri = f'{request.scheme}://{request.get_host()}{request.path}'
## OR request.build_absolute_uri()   JUMP_1
```

<br>

## Database Model Queries

<br>

> [youtube.com](https://www.youtube.com/watch?v=PD3YnPSHC-c)

<br>

For `Note` and `Page` models:

- With no `related_name`:

```
notes = page_object.note_set.all()
notes = page_object.note_set.filter(...)
```

- With `related_name` (e.g. `note_page_rel`):
> NOTE<br>
if there is a `related_name`,<br>
we HAVE to use that instead of `note_set`
```
notes = page_object.note_page_rel.all()
notes = page_object.note_page_rel.filter(...)
```

<br>

## Sessions
```
from django.contrib.sessions.models import Session

## the key is manually copied from browser
key = 'dgedhegedjedhedgjhwewed'

s = Session.objects.filter(pk=key)
print(s.get_decoded())
```

<br>

## Send Email

- Method 1:
```
from django.conf import settings
from django.core.mail import send_mail

send_mail(
    subject='test-subj',
    message='test-message',
    from_email='settings.EMAIL_HOST_USER',
    recipient_list=[
        '<email-address>',
        ...
    ],
)
```

- Method 2:
```
from django.conf import settings
from django.core.mail import EmailMessage

email = EmailMessage(
    subject='test-subj',
    body='test-body',
    from_email=settings.EMAIL_HOST_USER,
    to=[
        '<email-address>',
        ...
    ],
)
email.fail_silently = False
email.send()
```
