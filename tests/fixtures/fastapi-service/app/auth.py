import os

from fastapi import Header, HTTPException


def require_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != os.environ["API_KEY"]:
        raise HTTPException(status_code=401, detail="invalid API key")
