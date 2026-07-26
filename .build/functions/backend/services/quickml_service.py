import os
from config import (
    ZOHO_CLIENT_ID,
    ZOHO_CLIENT_SECRET,
    ZOHO_REFRESH_TOKEN,
)
import time
import token
from urllib import response
import requests

from utils.constants import (
    QUICKML_CHAT_URL,
    QUICKML_ORG_ID,
    GLM_MODEL_ID,
)

_token_cache = {
    "access_token": None,
    "expires_at": 0
}


def get_access_token():
    print("CLIENT_ID =", os.getenv("ZOHO_CLIENT_ID"))
    print("CLIENT_SECRET =", os.getenv("ZOHO_CLIENT_SECRET"))
    print("REFRESH_TOKEN =", os.getenv("ZOHO_REFRESH_TOKEN"))

    if (
        _token_cache["access_token"] is not None
        and time.time() < _token_cache["expires_at"]
    ):
        return _token_cache["access_token"]

    response = requests.post(
        "https://accounts.zoho.in/oauth/v2/token",
        data={
            "refresh_token": ZOHO_REFRESH_TOKEN,
            "client_id": ZOHO_CLIENT_ID,
            "client_secret": ZOHO_CLIENT_SECRET,
            "grant_type": "refresh_token",
        },
        timeout=10,
    )

    # response.raise_for_status()

    # token = response.json()

    # _token_cache["access_token"] = token["access_token"]

    if response.status_code != 200:
        raise Exception(
            f"QuickML failed ({response.status_code}): {response.text}"
        )

    token = response.json()

    print("OAuth Response:")
    print(token)

    if "access_token" not in token:
        raise Exception(f"OAuth failed: {token}")

    _token_cache["access_token"] = token["access_token"]



    _token_cache["expires_at"] = (
        time.time()
        + token.get("expires_in", 3600)
        - 60
    )

    return _token_cache["access_token"]


def ask_llm(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 400,
    temperature: float = 0.2,
):

    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "CATALYST-ORG": QUICKML_ORG_ID,
        "Content-Type": "application/json",
    }

    payload = {
        "model": GLM_MODEL_ID,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
        "chat_template_kwargs": {
            "enable_thinking": False
        },
    }
    print("=" * 60)
    print("CLIENT_ID      :", os.getenv("ZOHO_CLIENT_ID"))
    print("CLIENT_SECRET  :", os.getenv("ZOHO_CLIENT_SECRET"))
    print("REFRESH_TOKEN  :", os.getenv("ZOHO_REFRESH_TOKEN"))
    print("TOKEN URL      : https://accounts.zoho.in/oauth/v2/token")
    print("=" * 60)

    response = requests.post(
        QUICKML_CHAT_URL,
        json=payload,
        headers=headers,
        timeout=60,
    )

    print("Status Code:", response.status_code)
    print("Response:", response.text)

    response.raise_for_status()

    result = response.json()

    return result["response"]