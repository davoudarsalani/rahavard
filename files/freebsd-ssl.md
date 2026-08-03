# `FreeBSD` SSL Configuration

> [digitalocean.com](https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-freebsd-12-0)

<br>

## Install `certbot`

```
sudo pkg install -y security/py-certbot
sudo pkg install -y security/py-certbot-apache
```

<br>

## Comment out Config File for http

```
sudo vim /usr/local/etc/apache24/Includes/<PROJECT_SLUG>.conf
```

&uarr; Comment out all the lines in it.

<br>

## Configure SSL

```
sudo vim /usr/local/etc/apache24/httpd.conf
```
Uncomment:
```
#LoadModule ssl_module libexec/apache24/mod_ssl.so
#Include etc/apache24/extra/httpd-vhosts.conf
#LoadModule rewrite_module libexec/apache24/mod_rewrite.so
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

    ## NOTE you may need to uncomment the following lines
    ##      in case of permission denied errors
    # <Directory "/FOO/BAR/BAZ/<PROJECT_SLUG>/heart">
    #     Require all granted
    # </Directory>
    # Alias /.well-known/acme-challenge/ /FOO/BAR/BAZ/<PROJECT_SLUG>/heart/.well-known/acme-challenge/
    # <Directory "/FOO/BAR/BAZ/<PROJECT_SLUG>/heart/.well-known/acme-challenge/">
    #     Require all granted
    # </Directory>

</VirtualHost>
```

<br>

> To be skipped
```
sudo mkdir /usr/local/www/apache24/data/EXAMPLE_IR
sudo chown -R www:www /usr/local/www/apache24/data/EXAMPLE_IR
```

<br>

## Generate Certificate

```
sudo certbot --apache -d XXXX.EXAMPLE_IR
(-d EXAMPLE_IR if no sub-domains)
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
SSLCertificateFile /usr/local/etc/letsencrypt/live/XXXX.EXAMPLE_IR/fullchain.pem
SSLCertificateKeyFile /usr/local/etc/letsencrypt/live/XXXX.EXAMPLE_IR/privkey.pem
</VirtualHost>
</IfModule>
```

&uarr; Comment out all the lines in it.

<br><br>

```
sudo vim /usr/local/etc/apache24/Includes/<PROJECT_SLUG>-ssl.conf
```

Paste:
```
LoadModule wsgi_module /usr/local/libexec/apache24/mod_wsgi.so

ServerName XXXX.EXAMPLE_IR

## __FOR_FTP_ONLY__
# Timeout 3600

ServerSignature Off
ServerTokens Prod

<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerName XXXX.EXAMPLE_IR

    ## to tell Apache to pass the Authorization header through
    ## (e.g. from mobile apps) to your Django application
    WSGIPassAuthorization On

    ## __FOR_FTP_ONLY__
    # LimitRequestBody 0
    # RequestReadTimeout body=0
    # WSGIApplicationGroup %{GLOBAL}

    SSLProtocol -all +TLSv1.2 +TLSv1.3
    Protocols h2 http/1.1

    ErrorLog  /FOO/BAR/BAZ/<PROJECT_SLUG>/logs/httpd-error.log
    CustomLog /FOO/BAR/BAZ/<PROJECT_SLUG>/logs/httpd-access.log common

    ## https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/modwsgi/#serving-files
    Alias /public-attachments/    /FOO/BAR/BAZ/<PROJECT_SLUG>/static/public-attachments/
    # Alias /robots.txt  /path/to/mysite.com/static/robots.txt
    # Alias /favicon.ico /FOO/BAR/BAZ/<PROJECT_SLUG>/static/files/misc/fav.ico
    # Alias /static/     /FOO/BAR/BAZ/<PROJECT_SLUG>/static/
    <Directory /FOO/BAR/BAZ/<PROJECT_SLUG>/static>
        Require all granted
    </Directory>

    ## user=<REMOTE_USERNAME> group=<REMOTE_USERNAME> processes=2 threads=25 from https://stackoverflow.com/questions/53857711/apache-django-mod-wsgi-errno-13-permission-denied
    WSGIDaemonProcess <PROJECT_SLUG> python-home=/FOO/BAR/BAZ/<PROJECT_SLUG>/venv python-path=/FOO/BAR/BAZ/<PROJECT_SLUG> user=<REMOTE_USERNAME> group=<REMOTE_USERNAME> processes=2 threads=25
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

Reload and Restart `apache24`:
```
sudo service apache24 reload && \
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
Options Indexes FollowSymLinks
```
with
```
Options -Indexes +FollowSymLinks
```

2. Replace
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
        Require all denied
    </LimitExcept>
    Require all granted
</Directory>
```

3. Add to the end of file:
```
TraceEnable off
```

4. Add to the end of file:
```
<IfModule mod_headers.c>
  # Add security and privacy related headers

  ## by me: keep commented to prevent strange behavior on admin page
  # Header set Content-Security-Policy "default-src 'self'; upgrade-insecure-requests;"

  Header always set Strict-Transport-Security "max-age=31536000"
  SetEnv modHeadersAvailable true
  Header always set X-Content-Type-Options "nosniff"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>
```

5. Add to the end of file ([wp-bridge.com](https://www.wp-bridge.com/the-14-step-apache-security-best-practices-checklist/)):
```
FileETag None
```
> The ETag (Entity Tag) header in Apache comes with a number of sensitive details about your server. Therefore, you should hide this sort of information for full protection of your website. Especially, if you’re running an ecommerce website, you’ll have to hide this information to become PCI compliant.

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
