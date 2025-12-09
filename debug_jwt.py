from jose import jwt   # ✅ use jose, not jwt

SECRET_KEY = "CHANGE_ME_STRONG_SECRET"  # same as in main.py
ALGORITHM = "HS256"

token = "paste_your_token_here"

decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
print(decoded)