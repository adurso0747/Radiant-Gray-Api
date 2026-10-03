"""
security.py
------------
Gates admin-only endpoints (currently just the submissions list, see
routers/admin.py) behind a single shared API key, passed as the
X-API-Key header — not full user auth, since the only "user" is the
band checking things via curl or a quick script. Reusable as a
dependency on any future admin-only route.
"""

from fastapi import Header, HTTPException, status

from .config import settings


async def require_admin_api_key(x_api_key: str = Header(default="")) -> None:
    if not x_api_key or x_api_key != settings.admin_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
