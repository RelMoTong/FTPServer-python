# FTP服务器

一个带有GUI界面的Python FTP服务器，支持用户管理、权限控制和配置设置。

## 安装说明

### 前提条件

- Python 3.6 或更高版本
- pip (Python包管理器)

### 步骤1: 安装依赖

有几种方法可以安装依赖：

#### 方法1: 使用requirements.txt文件

```bash
pip install -r requirements.txt
```

#### 方法2: 直接安装所需包

```bash
pip install pyftpdlib pytest pytest-cov pillow
```

### 问题排查

#### 如果pip命令不可用:

使用Python模块形式调用pip:

```bash
python -m pip install -r requirements.txt
```

#### 如果您使用虚拟环境:

确保先激活虚拟环境:

- Windows:
  ```
  .venv\Scripts\activate
  ```

- Linux/Mac:
  ```
  source .venv/bin/activate
  ```

#### 如果python命令无法识别:

尝试使用完整路径:

```bash
C:\Path\To\Python\python.exe -m pip install pyftpdlib
```

或者添加Python到环境变量中。

## 运行FTP服务器

安装完成后，可以通过以下命令启动服务器:

```bash
python ftpserver.py
```

## 生成可执行文件

如果你想将此FTP服务器打包成一个独立的.exe文件，以便在没有安装Python的环境中运行：

### 方式1: 使用批处理文件(推荐)

1. 双击项目目录中的`build.bat`文件
2. 等待打包过程完成
3. 在`dist`文件夹中找到打包好的程序

### 方式2: 手动打包

1. 安装PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. 执行打包命令:
   ```bash
   python build_exe.py
   ```

3. 打包完成后，可以在`dist`文件夹中找到FTP服务器的可执行文件和完整分发包。

### 在其他电脑上运行

1. 将`dist\FTP服务器`文件夹复制到目标电脑
2. 双击`FTPServer.exe`即可启动程序
3. 无需安装Python即可运行

## 配置说明

### 服务器配置

服务器配置保存在`config/settings.json`文件中，包括:

- 监听地址和端口
- 最大连接数限制
- 被动模式端口范围
- 超时设置

### 用户管理

用户信息保存在`config/users.json`文件中，包括:

- 用户名和密码
- 主目录路径
- 访问权限

可以通过GUI界面添加或删除用户。

## 使用说明

1. 启动服务器后，会显示GUI界面
2. 在"服务器控制"标签页设置服务器参数
3. 在"用户管理"标签页管理FTP用户账户
4. 点击"启动服务器"按钮启动FTP服务
5. 在"日志"标签页可以查看服务器运行日志

## 权限说明

用户权限使用字母组合表示:

- `e` - 更改目录
- `l` - 列出文件
- `r` - 从服务器检索文件
- `a` - 追加数据到文件
- `d` - 删除文件或目录
- `f` - 重命名文件或目录
- `m` - 创建目录
- `w` - 将文件存储到服务器
- `M` - 更改文件模式
- `T` - 更改文件时间
