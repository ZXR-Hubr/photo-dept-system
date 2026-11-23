"""光影摄影部工作平台 - 后端 API

FastAPI + SQLite（标准库），数据真正存服务端数据库，跨浏览器/设备共享。
监听沙箱注入的 PORT，绑定 0.0.0.0。
"""
import os
import json
import sqlite3
from pathlib import Path
from contextlib import contextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "photodept.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

STORES = ["orders", "assets", "plans", "staff", "equip", "activity"]

app = FastAPI(title="光影摄影部工作平台 API", version="1.0")


@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with db() as c:
        for s in STORES:
            c.execute(
                f'CREATE TABLE IF NOT EXISTS "{s}" '
                '(id TEXT PRIMARY KEY, payload TEXT NOT NULL)'
            )


@app.on_event("startup")
def on_startup():
    init_db()
    # 首次启动灌入示例数据（只在全空时）
    with db() as c:
        for s in STORES:
            n = c.execute(f'SELECT COUNT(*) FROM "{s}"').fetchone()[0]
            if n == 0 and s in SEED:
                for obj in SEED[s]:
                    c.execute(
                        f'INSERT OR IGNORE INTO "{s}"(id,payload) VALUES(?,?)',
                        (obj["id"], json.dumps(obj, ensure_ascii=False)),
                    )


def row_obj(row):
    return json.loads(row["payload"]) if row else None


# ---- 通用 CRUD：前端 put/del/get/all 一一对应 ----
@app.get("/api/{store}/all")
def api_all(store: str):
    if store not in STORES:
        return JSONResponse({"error": "unknown store"}, 404)
    with db() as c:
        rows = c.execute(f'SELECT payload FROM "{store}"').fetchall()
    return [row_obj(r) for r in rows]


@app.get("/api/{store}/{item_id}")
def api_get(store: str, item_id: str):
    if store not in STORES:
        return JSONResponse({"error": "unknown store"}, 404)
    with db() as c:
        row = c.execute(f'SELECT payload FROM "{store}" WHERE id=?', (item_id,)).fetchone()
    obj = row_obj(row)
    return obj if obj is not None else JSONResponse({"error": "not found"}, 404)


@app.put("/api/{store}")
async def api_put(store: str, request: Request):
    if store not in STORES:
        return JSONResponse({"error": "unknown store"}, 404)
    obj = await request.json()
    if "id" not in obj:
        return JSONResponse({"error": "missing id"}, 400)
    with db() as c:
        c.execute(
            f'INSERT OR REPLACE INTO "{store}"(id,payload) VALUES(?,?)',
            (str(obj["id"]), json.dumps(obj, ensure_ascii=False)),
        )
    return obj


@app.delete("/api/{store}/{item_id}")
def api_del(store: str, item_id: str):
    if store not in STORES:
        return JSONResponse({"error": "unknown store"}, 404)
    with db() as c:
        c.execute(f'DELETE FROM "{store}" WHERE id=?', (item_id,))
    return {"ok": True}


@app.delete("/api/{store}")
def api_clear(store: str):
    if store not in STORES:
        return JSONResponse({"error": "unknown store"}, 404)
    with db() as c:
        c.execute(f'DELETE FROM "{store}"')
    return {"ok": True}


@app.get("/api/health")
def health():
    counts = {}
    with db() as c:
        for s in STORES:
            counts[s] = c.execute(f'SELECT COUNT(*) FROM "{s}"').fetchone()[0]
    return {"status": "ok", "app": "光影摄影部工作平台", "db": "sqlite", "counts": counts}


# ---- 前端静态托管（放最后，避免覆盖 /api 路由）----
@app.get("/")
def index():
    return FileResponse(BASE_DIR / "index.html")


# ---- 种子数据（与前端原 IndexedDB 版本字段一致）----
from seed import SEED  # noqa: E402

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")), log_config=None)
