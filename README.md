## 部署

### chromedriver

```shell
# 下载谷歌浏览器
yum install https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
# 下载驱动器
wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.109/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip
cd chromedriver-linux64
chmod +x chromedriver
```

### 安装 miniconda

```shell
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
```

```shell
# 创建环境
conda create -n DeepRead python==3.10.11
```

### 设置 pip 源

```shell
mkdir ~/.pip
vim ~/.pip/pip.conf
```

输入源内容：

```shell
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host=mirrors.aliyun.com
```

检查是否生效

```shell
pip config list
```

### 安装 poetry

```shell
# 安装
curl -sSL https://install.python-poetry.org | python3 -

```

### 安装配置 supervisor

```shell
pip install supervisor #安装进程监测工具，需要在base环境下安装
cp Langchain-DeepRead/tool/supervisor.conf /etc/
mkdir /etc/supervisor
cp Langchain-DeepRead/tool/web.conf /etc/ #配置中项目路径参考工程路径
```

### 项目部署

```shell
git clone https://github.com/ptonlix/Langchain-DeepRead.git # 克隆项目
conda activate DeepRead # 激活环境
cd Langchain-DeepRead # 进入项目
poetry install # 安装依赖

supervisord -c /etc/supervisord.conf #启动项目

bash +x tests/deploy_test.sh # 服务启动后测试项目
```
