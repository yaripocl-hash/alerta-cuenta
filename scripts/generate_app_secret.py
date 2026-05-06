"""Genera un APP_SECRET seguro para usar en .env"""
import secrets

secret = secrets.token_urlsafe(64)
print("APP_SECRET generado:")
print(secret)
print()
print("Copia este valor a APP_SECRET en tu archivo .env")
