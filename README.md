# 光影 · 企业摄影部工作平台

摄影部门工作管理系统，前后端分离架构，可免费部署到 Railway / Render。

- 前端：单页应用（原生 HTML/CSS/JS，无构建步骤）
- 后端：Python FastAPI + SQLite（仅标准库 sqlite3，无需单独数据库服务）
- 数据：服务端持久化，跨浏览器、跨设备共享
- 功能：拍摄工单、素材资产库、拍摄计划、摄影师团队、设备台账、数据统计、备份恢复

## 本地运行

```bash
pip install -r requirements.txt
python main.py
```

浏览器打开 <http://127.0.0.1:8000/> 即可。首次启动自动灌入示例数据。

服务监听 `PORT` 环境变量指定的端口（默认 8000），绑定 `0.0.0.0`。

## 目录结构

```
main.py            FastAPI 后端：SQLite 建表、通用 CRUD API、静态托管、启动时灌种子数据
seed.py            示例数据（与页面字段完全一致）
index.html         前端单页应用（通过 /api 调用后端）
requirements.txt   Python 依赖
railway.json       Railway 部署配置
Procfile           Render 等平台的进程声明
.gitignore         忽略缓存与数据库文件
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查，返回各表记录数 |
| GET | `/api/{store}/all` | 列出某张表全部记录 |
| GET | `/api/{store}/{id}` | 按 id 取单条 |
| PUT | `/api/{store}` | 新增或替换（按 id） |
| DELETE | `/api/{store}/{id}` | 删除单条 |
| DELETE | `/api/{store}` | 清空某张表 |

`store` 取值：`orders` `assets` `plans` `staff` `equip` `activity`

## 部署到 Railway

1. GitHub 新建公开仓库（例如 `photo-dept-system`），把本目录全部文件上传。
2. 登录 Railway → New Project → Deploy from GitHub repo → 选中该仓库。
3. Railway 会自动识别 Python 项目并读取 `railway.json`，启动命令为：

   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

   若手动填写，在 Settings → Deploy → Start Command 中填入上面这条。
4. 无需配置环境变量，`PORT` 由 Railway 自动注入。
5. 部署完成后，在 Settings → Networking 里把域名改成你自己的前缀（例如 `photo-dept.up.railway.app`），或绑定自定义域名。
6. 打开域名即可访问，`/api/health` 可验证后端正常。

## 部署到 Render（备用）

1. New → Web Service，关联同一个 GitHub 仓库。
2. Runtime 选 Python，Build Command 填 `pip install -r requirements.txt`，Start Command 填：

   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

3. 免费层即可，部署后得到 `xxx.onrender.com` 域名。

## 数据持久化说明

SQLite 数据库文件位于服务端的 `data/photodept.db`。免费层平台的文件系统是临时的：

- 重新部署或实例重启后，新增的数据会重置为示例数据；
- 示例数据在每次首次启动时自动重建，所以演示站任何时候打开都有完整内容；
- 需要长期保留真实数据，可付费挂载持久磁盘，或定期用页面「数据与设置 → 导出备份」保存 JSON。

## 前端连接独立后端

默认前端与后端同源部署，页面自动请求 `/api`。若前端单独托管（如 Netlify）、后端独立部署，在 `index.html` 的 `<head>` 中加一行即可指向后端公网地址：

```html
<script>window.API_BASE = 'https://你的后端域名';</script>
```
