import jwt

jwt_secret = "raggy-secret-2026"

payload = {
    "user_id": "TEST-001",
    "role": "admin"
}

token = jwt.encode(payload, jwt_secret, algorithm="HS256")
print(token)
