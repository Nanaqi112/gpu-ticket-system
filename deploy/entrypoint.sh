#!/bin/sh
set -e

echo "[entrypoint] 等待数据库就绪..."
python - <<'PY'
import os
import sys
import time

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connections

last_error = None
for _ in range(60):
    try:
        connections['default'].cursor().close()
        print('[entrypoint] 数据库已就绪')
        sys.exit(0)
    except Exception as exc:  # 数据库尚未启动或网络未就绪
        last_error = exc
        time.sleep(1)

print(f'[entrypoint] 数据库连接失败: {last_error}', file=sys.stderr)
sys.exit(1)
PY

echo "[entrypoint] 执行数据库迁移..."
python manage.py migrate --noinput

echo "[entrypoint] 启动 nginx + gunicorn..."
exec /usr/bin/supervisord -c /etc/supervisor/app.conf
