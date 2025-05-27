# `FreeBSD` SSL Configuration

> [digitalocean.com](https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-freebsd-12-0)

<br>

## Install `certbot`

```
sudo pkg install -y security/py-certbot
sudo pkg install -y security/py-certbot-apache
```

## Configure SSL

```
sudo vim /usr/local/etc/apache24/httpd.conf
```
Uncomment:
```
#LoadModule ssl_module libexec/apache24/mod_ssl.so
#Include etc/apache24/extra/httpd-vhosts.conf
```

<br><br>

```
sudo vim /usr/local/etc/apache24/extra/httpd-vhosts.conf
```

Paste:
```
<VirtualHost *:80>

    ServerAdmin support@EXAMPLE_IR
    ServerName  EXAMPLE_IR
    ServerAlias XXXX.EXAMPLE_IR

    # Redirect permanent / https://XXXX.EXAMPLE_IR

    DocumentRoot "/FOO/BAR/BAZ/<PROJECT_SLUG>/heart"
    ErrorLog     "/FOO/BAR/BAZ/<PROJECT_SLUG>/logs/httpd-error.log"
    CustomLog    "/FOO/BAR/BAZ/<PROJECT_SLUG>/logs/httpd-access.log" common

</VirtualHost>
```

<br>

> To be skipped
```
sudo mkdir /usr/local/www/apache24/data/EXAMPLE_IR
sudo chown -R www:www /usr/local/www/apache24/data/EXAMPLE_IR
```

<br><br>

```
sudo vim /usr/local/etc/apache24/httpd.conf
```

Uncomment:
```
#LoadModule rewrite_module libexec/apache24/mod_rewrite.so
```

<br>

> NOTE:<br>
> To prevent potential errors and/or conflicts,<br>
> first get rid of any `/usr/local/etc/apache24/Includes/httpd.conf`<br>
> already created by you.

<br>

## Generate Certificate

```
sudo certbot --apache -d EXAMPLE_IR -d XXXX.EXAMPLE_IR
```

The above command will append these lines<br>
to `/usr/local/etc/apache24/extra/httpd-vhosts.conf`:
```
RewriteEngine on
RewriteCond %{SERVER_NAME} =XXXX.EXAMPLE_IR [OR]
RewriteCond %{SERVER_NAME} =EXAMPLE_IR
RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
```

<br>

Also, the file `/usr/local/etc/apache24/extra/httpd-vhosts-le-ssl.conf`<br>
will be created with the following content:
```
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerAdmin support@EXAMPLE_IR
    DocumentRoot "/FOO/BAR/BAZ/<PROJECT_SLUG>/heart"
    ServerName EXAMPLE_IR
    ServerAlias XXXX.EXAMPLE_IR
    ErrorLog "/FOO/BAR/BAZ/<PROJECT_SLUG>/logs/httpd-error.log"
    CustomLog "/FOO/BAR/BAZ/<PROJECT_SLUG>/logs/httpd-access.log" common

Include /usr/local/etc/letsencrypt/options-ssl-apache.conf
SSLCertificateFile /usr/local/etc/letsencrypt/live/EXAMPLE_IR/fullchain.pem
SSLCertificateKeyFile /usr/local/etc/letsencrypt/live/EXAMPLE_IR/privkey.pem
</VirtualHost>
</IfModule>
```


Change the above content to:
> replace `python3.11` with appropriate python version)
```
LoadModule wsgi_module /usr/local/libexec/apache24/mod_wsgi.so

ServerName XXXX.EXAMPLE_IR
## >>> EXAMPLE_IR when no sub-domains

<IfModule mod_ssl.c>
<VirtualHost *:443>
    ## to tell Apache to pass the Authorization header through
    ## (e.g. from mobile apps) to your Django application
    WSGIPassAuthorization On

    ErrorLog  /FOO/BAR/BAZ/<PROJECT_SLUG>/logs/httpd-error.log
    CustomLog /FOO/BAR/BAZ/<PROJECT_SLUG>/logs/httpd-access.log common

    ## https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/modwsgi/#serving-files
    Alias /uploads/    /FOO/BAR/BAZ/<PROJECT_SLUG>/static/uploads/
    # Alias /robots.txt  /path/to/mysite.com/static/robots.txt
    # Alias /favicon.ico /FOO/BAR/BAZ/<PROJECT_SLUG>/static/files/misc/fav.ico
    # Alias /static/     /FOO/BAR/BAZ/<PROJECT_SLUG>/static/
    <Directory /FOO/BAR/BAZ/<PROJECT_SLUG>/static>
        Require all granted
    </Directory>

    ## user=<REMOTE_USERNAME> group=<REMOTE_USERNAME> processes=2 threads=25 from https://stackoverflow.com/questions/53857711/apache-django-mod-wsgi-errno-13-permission-denied
    WSGIDaemonProcess <PROJECT_SLUG> python-path=/FOO/BAR/BAZ/<PROJECT_SLUG>:/FOO/BAR/BAZ/<PROJECT_SLUG>/venv/lib/python3.11/site-packages/ user=<REMOTE_USERNAME> group=<REMOTE_USERNAME> processes=2 threads=25
    WSGIProcessGroup  <PROJECT_SLUG>
    WSGIScriptAlias   / /FOO/BAR/BAZ/<PROJECT_SLUG>/heart/wsgi.py

    <Directory /FOO/BAR/BAZ/<PROJECT_SLUG>/heart>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    SSLCertificateFile    /usr/local/etc/letsencrypt/live/XXXX.EXAMPLE_IR/fullchain.pem
    SSLCertificateKeyFile /usr/local/etc/letsencrypt/live/XXXX.EXAMPLE_IR/privkey.pem
    Include               /usr/local/etc/letsencrypt/options-ssl-apache.conf

</VirtualHost>
</IfModule>
```

<br>

To prevent `apache24` warning when restarting:
```
sudo mkdir -p /usr/local/docs/EXAMPLE_IR
```

<br>

Restart `apache24`:
```
sudo service apache24 restart
```

<br>

To display a list of all virtual hosts:
```
sudo apachectl -t -D DUMP_VHOSTS
```
- `-t` tells apachectl to run a configuration file syntax test.<br>It checks the configuration files for any syntax errors without starting the server.
- `-D DUMP_VHOSTS` defines a macro named DUMP_VHOSTS.<br>When Apache is run with this macro, it will print out the list of all configured virtual hosts.

<br>

<br><br><br><br><br>


## Hardening `apache24`

> [digitalocean.com](https://www.digitalocean.com/community/tutorials/recommended-steps-to-harden-apache-http-on-freebsd-12-0*)

<br>

```
sudo vim /usr/local/etc/apache24/httpd.conf
```

1. Replace
```
#ServerName www.example.com:80
```
with
```
#ServerName www.example.com:80
ServerTokens Prod
```

2. Replace
```
Options Indexes FollowSymLinks
```
with
```
Options -Indexes +FollowSymLinks
```
3. Replace
```
DocumentRoot "/usr/local/www/apache24/data"
<Directory "/usr/local/www/apache24/data">
    ...
    Require all granted
</Directory>
```
with
```
DocumentRoot "/usr/local/www/apache24/data"
<Directory "/usr/local/www/apache24/data">
    ...
    <LimitExcept GET POST HEAD>
       deny from all
    </LimitExcept>
    Require all granted
</Directory>
```
4. Add to the end of file:
```
TraceEnable off
```
5. Add to the end of file:
```
<IfModule mod_headers.c>
  # Add security and privacy related headers

  ## by me: keep commented to prevent strange behavior on admin page
  # Header set Content-Security-Policy "default-src 'self'; upgrade-insecure-requests;"

  Header set Strict-Transport-Security "max-age=31536000; includeSubDomains"
  Header always edit Set-Cookie (.*) "$1; HttpOnly; Secure"
  Header set X-Content-Type-Options "nosniff"
  Header set X-XSS-Protection "1; mode=block"
  Header set Referrer-Policy "strict-origin"
  Header set X-Frame-Options: "deny"
  SetEnv modHeadersAvailable true
</IfModule>
```
6. Add to the end of file ([wp-bridge.com](https://www.wp-bridge.com/the-14-step-apache-security-best-practices-checklist/)):
```
FileETag None
```
> The ETag (Entity Tag) header in Apache comes with a number of sensitive details about your server. Therefore, you should hide this sort of information for full protection of your website. Especially, if you’re running an ecommerce website, you’ll have to hide this information to become PCI compliant.

<br><br>

Change `Timeout`:
```
sudo vim /usr/local/etc/apache24/extra/httpd-default.conf
```
Replace
```
Timeout 60
```
with
```
Timeout 30
```

<br><br>

Restart `apache24`:
```
sudo service apache24 restart
```

<br><br>

To test changes:<br>
*Method 1 ([stackoverflow.com](https://stackoverflow.com/a/24161120/))*
```
curl -v -X TRACE --connect-timeout 20 --max-time 60 http://XXXX.EXAMPLE_IR 2>&1
```
*Method 2*
```
nmap -sV -p 80 <YOUR_IP>
```
