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
%wheel ALL=(ALL) NOPASSWD: /usr/sbin/service * restart, /usr/sbin/service * status, /usr/bin/du *, /usr/bin/killall -HUP tor, /usr/local/bin/certbot renew
```

<br>

## Install Packages

```
## exit from root
exit

sudo pkg install -y apache24 bash curl git gpart jq python redis rsync tmux vim wget xfce
sudo pkg install -y pkgconf    ## needed for installing mysql package with pip
sudo pkg install -y syslog-ng p5-Net-Nslookup bind-tools
sudo pkg install -y e2fsprogs    ## this will install chattr and lsattr
sudo pkg install -y xorg xorg-server xorg-apps xorg-drivers
sudo pkg install -y open-vm-tools-nox11    ## for VMs only

## mysql (using ports)
pkg search databases/mysql*
sudo pkg install -y databases/mysql90-server
sudo pkg install -y databases/mysql90-client
##
## mysql (online)
sudo pkg search ^mysql
sudo pkg install -y mysql90-server
sudo pkg install -y mysql90-client

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

## Enable `apache24` and `mysql`

```
sudo vim /etc/rc.conf
```

Paste:
```
apache24_enable="YES"
mysql_enable="YES"
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
## If not running interactively, don't do anything
[[ $- != *i* ]] && return

if [ $UID -gt 0 ]; then
  ## https://superuser.com/a/1519118
  ##
  ## set rgb colors
  ps_cname='167;95;180'
  ps_cdir='88;131;187'
  ps_cexit='236;39;39'
  ##
  ## do NOT change
  ps_code_color_name="\x1b[38;2;${ps_cname}m"
  ps_code_color_dir="\x1b[38;2;${ps_cdir}m"
  ps_code_color_exit="\x1b[38;2;${ps_cexit}m"
  ps_code_color_reset='\x1b[0m'
  ##
  ## do NOT change
  ps_c_name=$(printf "${ps_code_color_name}")
  ps_c_dir=$(printf "${ps_code_color_dir}")
  ps_c_exit=$(printf "${ps_code_color_exit}")
  ps_c_rst=$(printf "${ps_code_color_reset}")
  ##
  PS1='$(
  xt_stts="$?"
  [ "$xt_stts" -gt 0 ] && EXIT=" $xt_stts"
echo "\
\[${ps_c_name}\]\u@\H \[${ps_c_rst}\]\
\[${ps_c_dir}\]\w\[${ps_c_rst}\]\
\[${ps_c_exit}\]${EXIT}\[${ps_c_rst}\] \$ "
)'
  ## previously:
  # PS1='$(xt_stts="$?";[ "$xt_stts" -gt 0 ] && EXIT=" $xt_stts"
  # echo "-=[ \u@\H \w${EXIT} \$ ]=- ")'
fi

export HISTCONTROL=erasedups:ignoredups:ignorespace
export HISTTIMEFORMAT='%Y%m%d%H%M%S '
export LS_FLAGS='-A --color=always'

alias ls="\ls $LS_FLAGS"

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

if [ ! "$(pgrep 'tmux')" ]; then
    tmux
fi
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

## TMUX

```
vim ~/.tmux.conf
```

Paste:
```
# set prefix
set -g prefix C-a
unbind-key C-b
bind-key C-a send-prefix

set  -g base-index 1             ## start windows numbering at 1
set  -g display-time 3000        ## display message time
set  -g display-panes-time 3000  ## display panes time
set  -g clock-mode-style 12      ## 24
set  -g history-limit 50000
setw -g pane-base-index 1        ## start pane numbering at 1
setw -g automatic-rename on      ## rename window to reflect current program

## inactive window
set-window-option -g window-status-style          fg=#ffffff,bg=default
## active window
set-window-option -g window-status-current-style  fg=#000000,bg=default
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

>  In case of `send-pack: unexpected disconnect while reading sideband packet` error:
>  ```
>  ## Step 1:
>  export GIT_TRACE_PACKET=1
>  export GIT_TRACE=1
>  export GIT_CURL_VERBOSE=1
>  
>  ## Step 2:
>  git clone ...
>  ...
>  
>  ## Step 3:
>  unset GIT_TRACE_PACKET GIT_TRACE GIT_CURL_VERBOSE
>  ```
>  [stackoverflow](https://stackoverflow.com/a/67390274/)

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

## unset d for :cut
map d
## set x for :cut
map x :cut

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

## `TOR`

> [andregodinho1.medium.com](https://andregodinho1.medium.com/navigating-anonimized-on-the-web-with-tor-and-privoxy-on-a-kali-linux-20-55b6f7a57269), [forums.freebsd.org](https://forums.freebsd.org/threads/howto-use-tor-network-and-web-proxy.40307/)

<br>

Install:
```
sudo pkg install -y security/tor security/torsocks www/privoxy
```

<br>

Copy sample configuration file:
```
sudo cp /usr/local/etc/tor/torrc.sample /usr/local/etc/tor/torrc
```

<br>

Enable `tor` and `privoxy`:
```
sudo vim /etc/rc.conf
```

Paste:
```
tor_enable="YES"
privoxy_enable="YES"
```

<br>

Start `privoxy` manually, and copy the necessary config files:
```
sudo /usr/local/etc/rc.d/privoxy forcestart
```

<br>

Tell forward-sock which host and port to use (`127.0.0.1:9050`):
```
sudo vim /usr/local/etc/privoxy/config
```

Paste:
```
forward-socks5 / 127.0.0.1:9050 .
```

<br>


```
sudo service tor restart
sudo service privoxy restart
```

<br>

To check `IsTor`:
```
curl -s --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip; echo
```
If ok, it should return:
```
{"IsTor":true,"IP":"<SOME_IP>"}
```

<br>

## `syslog-ng`

> [syslog-ng.github.io](https://syslog-ng.github.io/admin-guide/README), [blog.matrixpost.net](https://blog.matrixpost.net/set-up-a-central-monitoring-server-with-syslog-ng-on-freebsd/)

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

To look out for syntax errors:
```
syslog-ng --syntax-only
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
```

NOTE: If the folders above do not exist, create them:
```
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
    "/FOO/BAR/BAZ/logs/${YEAR}-${MONTH}-${DAY}--${WEEKDAY}.log"
    template("${YEAR}-${MONTH}-${DAY} ${HOUR}:${MIN}:${SEC} ${HOST} (${FACILITY}/${LEVEL}) [${PROGRAM}] ${MSGONLY}\n")
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
    template("${YEAR}-${MONTH}-${DAY} ${HOUR}:${MIN}:${SEC} ${HOST} (${FACILITY}/${LEVEL}) [${PROGRAM}] ${MSGONLY}\n")
    template_escape(no)
  );
};


filter f_short_msg {
  "$(length ${MSG})" < 1024;
};


log {
  source(s_loghost);
  destination(d_host_daily);
};


log {
  source(s_loghost);

  ## filter lines whose MSG length is under 1024
  ## to avoid 'Message too long' error
  ## due to udp limitations
  filter(f_short_msg);

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
- *Using `~` is allowed if we use `-u "$USER"` in the command above*
- *Use absolute paths for shell commands, i.e. `/usr/local/bin/sudo` or `/usr/sbin/service`*
```
## at minute 0 [every hour]
0 * * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py actions --action dumpdata

## at 00:01
1 0 * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py actions --action check-deploy

## at 00:02
2 0 * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py actions --action check-trace

## at every 30th minute
*/30 * * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py actions --action collectstatic

## at minute 1 past hour 0 and 12
1 0,12 * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py actions --action renew

## --------------------
## only on log analyzer

## at minute 1 [every hour]
1 * * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py actions-analyzer --action statistics

## at minute 2 past every hour from 5 through 23 [05:02, 06:02, ..., 23:02]
2 5-23 * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py actions-analyzer --action hourly-parse

## at 00:10
10 0 * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py actions-analyzer --action parse --proxy --restart-services

## --------------------
## only on ticketing

## at 00:10
10 0 * * *  /FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python /FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py close-old-tickets
```

<br>

## Configure `redis`

Enable:
```
sudo vim /etc/rc.conf
```

Paste:
```
redis_enable="YES"
```

<br>

Configure:
```
sudo vim /usr/local/etc/redis.conf
```

Replace
```
# requirepass foobared
```
with
```
requirepass <YOUR_PASSWORD>
```
- *NOTE: no quotes around <YOUR_PASSWORD>*

<br>

Restart:
```
sudo service redis restart
```

<br>

## Configure `ntp` *(for Non-Virtual Servers Only)*

Enable:
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

Configure:
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
#server 127.127.1.0
```
with
```
server <YOUR_IP>
```

<br>

Restart:
```
sudo service ntpd restart
```

<br>

## Configure `apache24` *(http)*

```
sudo vim /usr/local/etc/apache24/Includes/httpd.conf
```

Paste:
> replace `python3.11` with appropriate python version)
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
    WSGIDaemonProcess <PROJECT_SLUG> python-path=/FOO/BAR/BAZ/<PROJECT_SLUG>:/FOO/BAR/BAZ/<PROJECT_SLUG>/venv/lib/python3.11/site-packages/ user=<REMOTE_USERNAME> group=<REMOTE_USERNAME> processes=2 threads=25
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

> [serverfault.com](https://serverfault.com/questions/873185/freebsd-rc-d-script-doesnt-start-as-a-daemon), [unix.stackexchange.com](https://unix.stackexchange.com/questions/50478/is-there-an-easy-way-to-create-a-freebsd-rc-script), [unix.stackexchange.com](https://unix.stackexchange.com/questions/745327/python-script-as-rc-service-on-freebsd)

<br>

```
sudo vim /usr/local/etc/rc.d/live_parse
```

Paste:

```
#!/bin/sh

# PROVIDE: live_parse
# REQUIRE: DAEMON mysql-server
# BEFORE: LOGIN
# KEYWORD:

. /etc/rc.subr

name=live_parse
rcvar="${name}_enable"

pidfile="/var/run/${name}.pid"
live_parse_user="root"

command="/FOO/BAR/BAZ/<PROJECT_SLUG>/venv/bin/python"
# command_interpreter=""
command_args="/FOO/BAR/BAZ/<PROJECT_SLUG>/manage.py live-parse &"

stop_cmd="${name}_stop"
status_cmd="${name}_status"


get_pids(){
  ## using live-parse (not live_parse)
  ## to look for name of custom Django command
  ## (as in .../manage.py live-parse)
  echo "$(pgrep -f 'live-parse')"
}


live_parse_status(){
  pids="$(get_pids)"

  if [ "$pids" ]; then
    printf '%s is running.\n' "$name"
    printf 'PID(s): %s\n' "$pids" | xargs
  else
    printf '%s is not running.\n' "$name"
    return 1
  fi
}


live_parse_stop(){
  pids="$(get_pids)"

  if [ "$pids" ]; then
    printf 'Stopping %s:\n' "$name"

    printf '%s\n' "$pids" | xargs -r kill -9 && {
      rm -f "$pidfile"
      printf '  SUCCESS\n'
    } || {
      printf '  ERROR: did not stop\n'
      return 1
    }

  else
    printf '%s was not running.\n' "$name"
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
