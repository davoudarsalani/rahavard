# `django` on `IIS`

> [nitinnain.com](https://nitinnain.com/setting-up-and-running-django-on-windows-iis-server/)

<br>

## Virtual Environment
```
cd C:\
mkdir <PROJECT_SLUG>
cd <PROJECT_SLUG>
python -m venv venv
venv\Scripts\activate.bat

python.exe -m pip install --upgrade pip
pip install -r requirements.txt
pip install wfastcgi
```

<br>

# Configure `fastcgi`

- Open `IIS Manager`
- Click on the name of the server in the list on the left.
- Double-click the `FastCGI Settings` icon
- Under `Actions` on the right-hand side, click `Add application ...`
  - in `Full Path`, enter:<br>
   `C:\<PROJECT_SLUG>\venv\Scripts\python.exe`
- In the `Arguments`, enter:<br>
   `C:\<PROJECT_SLUG>\venv\Lib\site-packages\wfastcgi.py`
- With the `Add FastCGI Application` dialog box still open, under the `General` section,
   click on the `Environment Variables` line, then click the gray `"..."` button
   that appears next to `Collection` on the right-hand side of the line.
   This opens the `EnvironmentVariables Collection Editor` dialog.
- In the `EnvironmentVariables Collection Editor dialog`, click `Add`
- Enter:
  ```
  Name:  DJANGO_SETTINGS_MODULE
  Value: <PROJECT_SETTINGS_DIR>.settings

  Name:  PYTHONPATH
  Value: C:\<PROJECT_SLUG>

  Name:  WSGI_HANDLER
  Value: django.core.wsgi.get_wsgi_application()
  ```
  - Click `OK`

<br>

## Create and Configure a New IIS Web Site
- On the left, under `Connections`, expand the tree under the server name.
- Right-click on the `Sites` folder and click `Add Website ...`
- For `Site name`, enter `<PROJECT_SLUG_UPPERCASE>`
- For `Physical path`, enter `C:\<PROJECT_SLUG>`
- Set port to `81`
- You may leave the `Host name` blank.
- Click `OK`

<br>

## Add a `FastCGI` handler mapping to this site
- In `IIS Manager`, expand the `Sites` folder on the left-hand side and click on the `<PROJECT_SLUG_UPPERCASE>` site
- On the right, double-click Handler Mappings`
- On the right, under `Actions` click `Add Module Mapping`
- In the `Request path` box enter an asterisk: `*`
- Click the arrow on the right-hand side of the `Module` box and select `FastCgi Module` (NOT `CgiModule`)
- In the `Executable` box, enter:<br>
  `C:\<PROJECT_SLUG>\venv\Scripts\python.exe|C:\<PROJECT_SLUG>\venv\Lib\site-packages\wfastcgi.py`
- In the `Name` box, enter anything you want (e.g. `Django Handler`)
- Click the `Request Restrictions` button
  - Uncheck the `Invoke handler only if request is mapped to` checkbox.
- Click `OK`
- Click `OK`
- When prompted `Do you want to create a FastCGI application for this executable?`, Click `No`
