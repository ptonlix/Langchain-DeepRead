## 安装 Supervisord

```
pip install supervisor 或者 apt install supervisor
```

## 自身配置

从模板生成

```
echo_supervisord_conf > supervisord.conf
```

配置文件解释

```ini
[unix_http_server]
file=/tmp/supervisor.sock   ; UNIX socket 文件，supervisorctl 会使用
;chmod=0700                 ; socket 文件的 mode，默认是 0700
;chown=nobody:nogroup       ; socket 文件的 owner，格式： uid:gid
;[inet_http_server]         ; HTTP 服务器，提供 web 管理界面
;port=127.0.0.1:9001        ; Web 管理后台运行的 IP 和端口，如果开放到公网，需要注意安全性
;username=user              ; 登录管理后台的用户名
;password=123               ; 登录管理后台的密码
[supervisord]
logfile=/tmp/supervisord.log ; 日志文件，默认是 $CWD/supervisord.log
logfile_maxbytes=50MB        ; 日志文件大小，超出会 rotate，默认 50MB
logfile_backups=10           ; 日志文件保留备份数量默认 10
loglevel=info                ; 日志级别，默认 info，其它: debug,warn,trace
pidfile=/tmp/supervisord.pid ; pid 文件
nodaemon=false               ; 是否在前台启动，默认是 false，即以 daemon 的方式启动
minfds=1024                  ; 可以打开的文件描述符的最小值，默认 1024
minprocs=200                 ; 可以打开的进程数的最小值，默认 200
; the below section must remain in the config file for RPC
; (supervisorctl/web interface) to work, additional interfaces may be
; added by defining them in separate rpcinterface: sections
[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface
[supervisorctl]
serverurl=unix:///tmp/supervisor.sock ; 通过 UNIX socket 连接 supervisord，路径与 unix_http_server 部分的 file 一致
;serverurl=http://127.0.0.1:9001 ; 通过 HTTP 的方式连接 supervisord
; 包含其他的配置文件 一般用于存放下文中守护进程的配置
[include]
files = /etc/supervisor/*.conf
```

### 守护进程的配置

假设有个 java 应用包 web.jar, 项目代码位于 /home/user/projects/ .
创建/etc/supervisor/web.conf 文件，写入：

```ini
[program:web]
directory = /home/user/projects ; 程序的启动目录
command = java -jar web.jar ; 启动命令可以根据实际情况加入相应的参数
;进程名称
process*name = %(program_name)s*%(process_num)02d
;启动设置
numprocs = 1 ;进程数
autostart = true ; 在 supervisord 启动的时候也自动启动
startsecs = 5 ; 启动 5 秒后没有异常退出，就当作已经正常启动了
autorestart = true ; 程序异常退出后自动重启
startretries = 3 ; 启动失败自动重试次数，默认是 3
user = root ; 用哪个用户启动
redirect_stderr = true ; 把 stderr 重定向到 stdout，默认 false
stdout_logfile_maxbytes = 20MB ; stdout 日志文件大小，默认 50MB
stdout_logfile_backups = 20 ; stdout 日志文件备份数
; stdout 日志文件，需要注意当指定目录不存在时无法正常启动，所以需要手动创建目录（supervisord 会自动创建日志文件）
stdout_logfile = /data/logs/usercenter_stdout.log
;停止信号,默认 TERM
;中断:INT (类似于 Ctrl+C)(kill -INT pid)，退出后会将写文件或日志(推荐)
;终止:TERM (kill -TERM pid)
;挂起:HUP (kill -HUP pid),注意与 Ctrl+Z/kill -stop pid 不同
;从容停止:QUIT (kill -QUIT pid)
stopsignal=INT
```

## 操作

```shell
#启动 supervisord 进程
supervisord -c supervisord.conf
#关闭 supervisord 进程（并不会使 supervisord 守护的进程关闭）
supervisorctl -c supervisord.conf shutdown
#重启 supervisord 进程
supervisorctl -c supervisord.conf reload
#进入 supervisorctl 交互终端
supervisorctl
#查看进程状态
supervisorctl status
#停止指定的守护程序
supervisorctl stop <programname>
#启动指定的守护程序
supervisorctl start <programname>
#重启指定的守护程序
supervisorctl restart <programname>
#读取有更新（增加）的配置文件，不会启动新添加的程序
supervisorctl reread
#重启配置文件修改过的程序
supervisorctl update

#如果项目使用了 python 的 pyenv 模块来设置环境，则 supervisord 配置文件中需要指定 python 环境的路径。其中有两种方式指定程序使用的 Python 环境：
#command 使用绝对路径。
#通过 environment 配置 PYTHONPATH。
```

## Tips

### Tips 1: Python 程序环境变量

如果项目使用了 python 的 pyenv 模块来设置环境，则 supervisord 配置文件中需要指定 python 环境的路径
有两种方式指定程序使用的 Python 环境：

command 使用绝对路径。这种方式一目了然。
environment 配置 PYTHONPATH。这种方式可以用来给程序传入环境变量。

```shell
environment=PYTHONPATH=$PYTHONPATH:/home/leon/.pyenv/versions/usercenter/bin/. environment
```

### Tips 2: 后台进程

supervisor 只能管理在前台运行的程序。

### Tips 3: 防止子进程变成孤儿进程

有时候用 Supervisor 托管的程序还会有子进程（如 Tornado），如果只杀死主进程，子进程就可能变成孤儿进程。通过这两项配置来确保所有子进程都能正确停止：

```shell
stopasgroup=true
killasgroup=true
```
