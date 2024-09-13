# `FreeBSD` Post-Install Configuration

<br>

## Set DNS IP Addresses

```
su
vi /etc/resolv.conf
```

Paste:
```
## shecan
# nameserver 178.22.122.100
# nameserver 185.51.200.2
```

<br>

## To Prevent `/etc/resolv.conf` from Automatically Resetting

```
echo 'resolvconf=NO' >> /etc/resolvconf.conf
```

<br>

## Install `pkg` and Update OS

```
pkg
pkg update && pkg upgrade -y
```

<br>

## `sudo` Permission

Install:
```
pkg install -y sudo
```

<br>

Add user to `sudoers`:
```
visudo
```

Replace
```
# %wheel ALL=(ALL:ALL) ALL
```

with
```
%wheel ALL=(ALL:ALL) ALL
%wheel ALL=(ALL) NOPASSWD: /usr/sbin/service apache24 restart, /usr/local/bin/certbot renew
```

<br>

## Install Packages

```
## exit from root
exit

sudo pkg install -y vim bash python git apache24 xfce wget curl gpart jq rsync
sudo pkg install -y syslog-ng p5-Net-Nslookup bind-tools
sudo pkg install -y e2fsprogs   ## this will install chattr and lsattr
sudo pkg install -y xorg xorg-server xorg-apps xorg-drivers
sudo pkg install -y open-vm-tools-nox11   ## for VMs only

## install from ports
sudo pkg install -y sysutils/htop
sudo pkg install -y databases/py-sqlite3
sudo pkg install -y www/mod_wsgi4  ## installs ap24-py39-mod_wsgi
```

<br>

## Make `bash` Default Shell

```
sudo chsh -s /usr/local/bin/bash "$USER"
sudo reboot
```

<br>

## Set Proper Timezone

```
sudo pkg install -y misc/zoneinfo
sudo cp /etc/localtime{,--backup}
sudo cp /usr/share/zoneinfo/Asia/Tehran /etc/localtime  ## NOTE do this last
```

<br>

## Enable `apache24`

```
sudo vim /etc/rc.conf
```

Paste:
```
apache24_enable="YES"
```

<br>

To see loaded `apache24` modules:
```
apachectl -M
```

<br>

## Configure `bash`

`bashrc`:
```
vim ~/.bashrc
```

Paste:
```
PS1='$(xt_stts="$?";[ "$xt_stts" -gt 0 ] && EXIT=" $xt_stts"
echo "-=[ \u@\h \w${EXIT} \$ ]=- ")'
export HISTCONTROL=erasedups:ignoredups:ignorespace
export HISTTIMEFORMAT='%Y%m%d%H%M%S '
export LS_FLAGS='-A --color=always'

alias ls="\ls $LS_FLAGS"
alias sshalive='ssh -o TCPKeepAlive=yes -o ServerAliveCountMax=20 -o ServerAliveInterval=15'

function lsl {
    shopt -s expand_aliases
    local ls_command ls_output

    alias ls_command='\ls $LS_FLAGS -lbh'
    if [ ! "$1" ] || [ -d "$1" ]; then
        ls_output="$(ls_command "${@}" | sed 1d)"
    else
        ls_output="$(ls_command "${@}")"
    fi

    printf '%s\n' "$ls_output" | column -t
    unalias ls_command
}

## to suppress the message:
## "You have new mail in /var/mail/$USER"
unset MAILCHECK
```

Source `bashrc`:
```
source ~/.bashrc
```

<br>

`bash_profile`:
```
echo 'source ~/.bashrc' >> ~/.bash_profile
sudo reboot
```

<br>

## Virtual Environment

```
cd
mkdir -p /FOO/BAR/BAZ/<PROJECT_SLUG>
chown -R "$USER" /FOO/BAR/BAZ/<PROJECT_SLUG>

git clone <REPOSITORY_URL> /FOO/BAR/BAZ/<PROJECT_SLUG>
cd /FOO/BAR/BAZ/<PROJECT_SLUG>
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

<br>

## Suppress MOTD (Message of the Day)

```
touch ~/.hushlogin
```

<br>

## lf

Download/Install:
```
cd /tmp
wget https://github.com/gokcehan/lf/releases/download/r29/lf-freebsd-amd64.tar.gz -O lf.tar.gz
tar -xvf lf.tar.gz
sudo mv lf /usr/bin/
rm lf.tar.gz
```

`lfrc`:
```
mkdir -p ~/.config/lf
vim ~/.config/lf/lfrc
```

Paste:
```
set ifs "\n"  ## NOTE do NOT replace " with '
set shell bash
set info size
set number true
set relativenumber true
set incsearch true
set timefmt "2006-01-02 15:04:05 -0700 Mon"  ## ORIG: "Mon Jan _2 15:04:05 2006"
set errorfmt "\033[0;49;31m%s\033[0m"    ## NOTE JUMP_2 do NOT replace \033 and " with \e and ' respectively
set wrapscroll true
set scrolloff 5
set dircounts true
set period 1
set shellopts "-e"
set ratios 1:2
map q % {{
    lf -remote "send $id clear"
    lf -remote "send $id unselect"
    lf -remote "send $id reload"
    lf -remote "send $id quit"
}}
map <tab>   :clear ; unselect ; reload
map <enter> :open  ; unselect
map <right> :open  ; unselect
map <left>  :updir ; unselect
map .       :set hidden!
map '`'     mark-load
map ';'     read
```

<br>

## `xfce` and `xorg`

```
sudo pw groupmod video -m "$USER" || sudo pw groupmod wheel -m "$USER"
```

<br>
<br>

```
sudo vim /boot/loader.conf
```

Paste:
```
kern.vty=vt
```

<br>
<br>

```
sudo pkg install -y drm-kmod
sudo vim /etc/rc.conf
```

Paste:
```
kld_list="i915kms"
```

<br>

Add to `xinitrc`:
```
echo 'exec /usr/local/bin/startxfce4 --with-ck-launch' >> ~/.xinitrc
startx
```

<br>

## `syslog-ng`

> [blog.matrixpost.net](https://blog.matrixpost.net/set-up-a-central-monitoring-server-with-syslog-ng-on-freebsd/)

> [syslog-ng.com](https://www.syslog-ng.com/technical-documents/doc/syslog-ng-open-source-edition/3.16/administration-guide/58)

<br>

Shut down default `syslogd` daemon:
```
sudo service syslogd stop
```

<br>

Enable `syslog_ng`:
```
sudo vim /etc/rc.conf
```

Paste:
```
syslogd_enable="NO"
syslog_ng_enable="YES"
```

<br>

To check syntax:
```
syslog-ng -s
```

<br>

To Restart:
```
sudo service syslog-ng restart
```

<br><br>

Configuration:<br>
*Step 1*
```
sudo vim /usr/local/etc/syslog-ng.conf
```

Paste:
```
@include "/usr/local/etc/syslog-ng/conf.d/"

## NOTE: If the folders above do not exist, create them:
sudo mkdir -p /usr/local/etc/syslog-ng/conf.d/
```

<br>

*Step 2*
```
sudo vim /usr/local/etc/syslog-ng/conf.d/loghost.conf
```

Paste:
```
source s_loghost {
  syslog(
    ip(<YOUR_IP>)
    transport("udp")
  );
};

destination d_host_daily {
  file(
    "/FOO/BAR/BAZ/logs/$YEAR-$MONTH-$DAY--$WEEKDAY.log"
    template("$YEAR-$MONTH-$DAY $HOUR:$MIN:$SEC $HOST ($FACILITY/$LEVEL) [$PROGRAM] $MSGONLY\n")
    owner(<REMOTE_USER>)
    group(<REMOTE_USER>)
    perm(0600)
    dir_perm(0750)
    create_dirs(yes)
    template_escape(no)
    # overwrite_if_older(514800)  ## overwrite if older than 6 days minus 1 hour
  );
};

## forward logs to live-parse
## (needed for live_parse service)
destination d_live_parse {
  syslog(
    "<YOUR_IP>"
    transport("udp")
    port(<YOUR_PORT>)
    template("$YEAR-$MONTH-$DAY $HOUR:$MIN:$SEC $HOST ($FACILITY/$LEVEL) [$PROGRAM] $MSGONLY\n")
    template_escape(no)
  );
};

log {
  source(s_loghost);
  destination(d_host_daily);
  destination(d_live_parse);
};

```

<br>

## `crontab`

List cronjobs for user:
```
sudo crontab -l -u "$USER"
```

<br>


Add cronjobs for user:
```
sudo crontab -e -u "$USER"
```

Paste:
```
## at minute 0 [every hour]
0 * * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py actions --action=dumpdata

## at 00:01
1 0 * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py actions --action=check-deploy

## at 00:02
2 0 * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py actions --action=check-trace

## at every 30th minute
*/30 * * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py actions --action=collectstatic

## at minute 1 past hour 0 and 12
1 0,12 * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py actions --action=renew

## --------------------
## only on log analyzer

## at every 30th minute
# */30 * * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py actions --action=backup

## at minute 1 [every hour]
1 * * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py actions --action=storage

## at 00:03
3 0 * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py actions --action=parse --batch=one    (--demo)

## at 00:30
30 0 * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py actions --action=parse --batch=two    (--demo)

## at every 30th minute
*/30 * * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py actions --action=hourly-parse
```

<br>

## Configure `ntp` *(for Non-Virtual Servers Only)*

Enable `ntp`:
```
sudo vim /etc/rc.conf
```

Paste:
```
## NTP
ntpdate_enable="YES"
ntp_sync_on_start="YES"
ntpd_enable="YES"
```

<br>

Configure `ntp`:
```
sudo vim /etc/ntp.conf
```
1. Comment:
```
pool 0.freebsd.pool.ntp.org iburst
pool 2.freebsd.pool.ntp.org iburst
```
2. Replace
```
'#server 127.127.1.0'
```
with
```
'server <YOUR_IP>'
```

<br>

Restart `ntp`:
```
sudo service ntpd restart
```

<br>

## Configure `apache24` *(http)*

```
sudo vim /usr/local/etc/apache24/Includes/httpd.conf
```

Paste:
```
LoadModule wsgi_module /usr/local/libexec/apache24/mod_wsgi.so

## Settings
ServerName FOO.BAR.local

## Default Overrides
ServerSignature Off
ServerTokens Prod
Timeout 30

## Virtual Hosts
<VirtualHost *:80>
    ## custom paths for logs (by default, apache logs are saved in /var/log/, named httpd-access.log and httpd-error.log)
    CustomLog /FOO/BAR/BAZ/<PROJECT_SLUG>/logs/httpd-access.log common
    ErrorLog  /FOO/BAR/BAZ/<PROJECT_SLUG>/logs/httpd-error.log

    ## https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/modwsgi/#serving-files
    # Alias /robots.txt /path/to/mysite.com/static/robots.txt
    # Alias /favicon.ico /FOO/BAR/BAZ/<PROJECT_SLUG>/static/favicon/favicon.ico
    Alias /uploads/ /FOO/BAR/BAZ/<PROJECT_SLUG>/static/uploads/
    # Alias /static/  /FOO/BAR/BAZ/<PROJECT_SLUG>/static/
    <Directory /FOO/BAR/BAZ/<PROJECT_SLUG>/static>
        Require all granted
    </Directory>

    ## user=<REMOTE_USERNAME> group=<REMOTE_USERNAME> processes=2 threads=25 from https://stackoverflow.com/questions/53857711/apache-django-mod-wsgi-errno-13-permission-denied
    WSGIDaemonProcess <PROJECT_SLUG> python-path=/FOO/BAR/BAZ/<PROJECT_SLUG>:/FOO/BAR/BAZ/<PROJECT_SLUG>/venv/lib/python3.9/site-packages/ user=<REMOTE_USERNAME> group=<REMOTE_USERNAME> processes=2 threads=25
    WSGIProcessGroup  <PROJECT_SLUG>
    WSGIScriptAlias   / /FOO/BAR/BAZ/<PROJECT_SLUG>/heart/wsgi.py

    <Directory /FOO/BAR/BAZ/<PROJECT_SLUG>/heart>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

</VirtualHost>

## useful links:
## https://www.digitalocean.com/community/tutorials/how-to-run-a-django-site-with-apache-mod_wsgi-and-mysql-on-freebsd-10-1
## https://www.freshports.org/www/mod_wsgi4
```

<br>

## `live_parse` service

> [link](https://serverfault.com/questions/873185/freebsd-rc-d-script-doesnt-start-as-a-daemon)

> [link](https://unix.stackexchange.com/questions/50478/is-there-an-easy-way-to-create-a-freebsd-rc-script)

> [link](https://unix.stackexchange.com/questions/745327/python-script-as-rc-service-on-freebsd)

<br>

```
sudo vim /usr/local/etc/rc.d/live_parse
```

Paste:

```
#!/bin/sh

# PROVIDE: live_parse
# REQUIRE: DAEMON
# BEFORE: LOGIN
# KEYWORD:

. /etc/rc.subr

name=live_parse
rcvar="${name}_enable"

pidfile="/var/run/${name}.pid"
live_parse_user="<REMOTE_USERNAME>"

command="/FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python"
# command_interpreter=""
command_args="/FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py live-parse &"

stop_cmd="${name}_stop"
status_cmd="${name}_status"

live_parse_status(){
  ## JUMP_1 using live-parse (not live_parse)
  ##        to look for name of custom django command
  ##        (as in .../manage.py live-parse)
  pids="$(pgrep -f 'live-parse')"

  if [ "$pids" ]; then
    printf 'live_parse is running.\n'
    printf 'PID(s): %s\n' "$pids" | xargs
  else
    printf 'live_parse is not running.\n'
    return 1
  fi  
}

live_parse_stop(){
  ## JUMP_1
  pids="$(pgrep -f 'live-parse')"

  if [ "$pids" ]; then
    printf 'Stopping live_parse:\n'

    printf '%s\n' "$pids" | xargs -r kill -9 && {
      printf '  SUCCESS\n' 
    } || {
      printf '  ERROR: did not stop\n'
      return 1
    }

  else
    printf 'live_parse was not running.\n'
    return 1
  fi
}

load_rc_config $name
run_rc_command "$1"
```

Make executable:
```
sudo chmod +x /usr/local/etc/rc.d/live_parse
```

<br>

Add to `/etc/rc.conf`:
```
sudo vim /etc/rc.conf
```

Paste:
```
live_parse_enable="YES"
```

<br>

Restart:
```
sudo service live_parse restart
```

<br>

## *TO BE ADDED*

> Documentation for `sshguard` configs

> Documentation for `pf` configs

> Documentation for 13 -> 14 `FreeBSD` upgrade
