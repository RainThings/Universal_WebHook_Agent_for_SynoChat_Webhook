# Universal_WebHook_Agent_for_SynoChat_Webhook
# Convert any webhook to Synology Chat webhook incoming
## 通过运行此程序你可以将大多数webhook请求经过它的转换传入SynologyChat平台的webhook
> [!WARNING]
> ### 声明<br/>
> 本程序未经严格测试，不保证其可用性、可靠性或性能。程序以“原样”提供，不附带任何明示或暗示的担保，包括但不限于安全性、适用性或特定用途的适用性。开发者不对因使用本程序而导致的任何损失承担责任。此外，因使用或转发本程序处理的信息内容而引发的任何后果，均由使用者自行承担责任。<br/>
> ### Announce<br/>
> This program has not undergone rigorous testing and comes with no guarantees regarding its usability, reliability, or performance. It is provided "as is" without any explicit or implied warranties, including but not limited to guarantees of security, suitability, or fitness for a particular purpose. The developer assumes no responsibility for any losses incurred as a result of using this program. Furthermore, the user bears sole responsibility for any consequences arising from the use or forwarding of information processed by this program.

---
##使用方法
> [!IMPORTANT]
> 原wenhook URL：https://example.com:5001/webapi/entry.cgi?api=SYNO.Chat.External&method=incoming&version=2&token=exampaletoken
> 组合后URL：http://<server_ip:port>/webhook?target_url=https://example.com:5001/webapi/entry.cgi?api=SYNO.Chat.External&method=incoming&version=2&token=exampaletoken
> URL传入：http://<server_ip:port>/webhook?target_url=<Original_URL>
---
简易安装步骤：


### **1. 安装必要工具**
> [!NOTE]
>确保已安装以下软件：
>
> - **Python 3.x**（推荐 Python 3.8+）
> - **pip**（Python 包管理工具）
> - **virtualenv**（用于创建隔离的 Python 环境）
> - **Supervisor**（进程管理工具，用于后台运行 Flask 应用并记录日志）
> - **Gunicorn**（生产环境推荐的 WSGI 服务器）

---

### **2. 配置 Flask 应用的运行环境**

#### **步骤 2.1：创建一个虚拟环境**
在服务器的项目目录下运行以下命令：
```bash
python3 -m venv venv
```

#### **步骤 2.2：激活虚拟环境并安装依赖**
```bash
source venv/bin/activate
pip install flask requests
```

#### **步骤 2.3：安装 Gunicorn**
```bash
pip install gunicorn
```

#### **步骤 2.4：测试运行**
使用 Gunicorn 测试运行 Flask 应用：
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```
- `-w 4`: 使用 4 个工作进程。
- `-b 0.0.0.0:5000`: 绑定到所有网络接口的 5000 端口。
- `app:app`: `app` 是文件名，第二个 `app` 是 Flask 应用的实例名。

访问的服务器地址 `http://<server_ip>:5000` 确保应用正常工作。

---

### **3. 配置 Supervisor 以后台运行 Flask 应用**

#### **步骤 3.1：安装 Supervisor**
```bash
sudo apt update
sudo apt install supervisor
```

#### **步骤 3.2：创建 Supervisor 配置文件**
创建一个新的配置文件，例如 `/etc/supervisor/conf.d/flask_app.conf`：
```bash
sudo nano /etc/supervisor/conf.d/flask_app.conf
```

添加以下内容：
```ini
[program:flask_app]
command=/path/to/your/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
directory=/path/to/your/project
user=your_username
autostart=true
autorestart=true
stderr_logfile=/var/log/flask_app.err.log
stdout_logfile=/var/log/flask_app.out.log
```

将以下内容替换为实际路径和用户名：
- `/path/to/your/venv`: 虚拟环境路径。
- `/path/to/your/project`: Flask 项目路径。
- `your_username`: 运行 Flask 应用的用户。

#### **步骤 3.3：启动 Supervisor 并加载配置**
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start flask_app
```

查看运行状态：
```bash
sudo supervisorctl status
```

---

### **4. 配置防火墙**
确保服务器的防火墙允许所需的端口（例如 5000）：
```bash
sudo ufw allow 5000
```

---

### **5. 日志管理**
日志文件路径在 `/var/log/flask_app.out.log` 和 `/var/log/flask_app.err.log`。
- 查看标准输出日志：
  ```bash
  tail -f /var/log/flask_app.out.log
  ```
- 查看错误日志：
  ```bash
  tail -f /var/log/flask_app.err.log
  ```

---

### **6. 使用反向代理（可选）**
>[!NOTE]
>生产环境推荐使用 Nginx 作为反向代理，以提供更好的性能和安全性。

#### **6.1：安装 Nginx**
```bash
sudo apt install nginx
```

#### **6.2：配置 Nginx**
创建一个新的配置文件，例如 `/etc/nginx/sites-available/flask_app`：
```bash
sudo nano /etc/nginx/sites-available/flask_app
```

添加以下内容：
```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

启用配置并重启 Nginx：
```bash
sudo ln -s /etc/nginx/sites-available/flask_app /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

访问 `http://your_domain_or_ip`，应用应该正常工作。
