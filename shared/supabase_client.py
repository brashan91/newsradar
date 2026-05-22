"""
Cliente Supabase compartido. Lee credenciales de env vars.

En GitHub Actions, estas vendrán de Secrets:
  SUPABASE_URL
  SUPABASE_SERVICE_KEY
"""
import os
import sys
from typing import Optional
from supabase import create_client, Client


def get_client() -> Client:
    """Devuelve cliente Supabase autenticado. Falla con mensaje claro si faltan vars."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    
    if not url:
        print("ERROR: SUPABASE_URL no está definido en env vars", file=sys.stderr)
        sys.exit(1)
    if not key:
        print("ERROR: SUPABASE_SERVICE_KEY no está definido en env vars", file=sys.stderr)
        sys.exit(1)
    
    return create_client(url, key)


# Singleton para no reconectar en cada llamada
_client: Optional[Client] = None


def supabase() -> Client:
    global _client
    if _client is None:
        _client = get_client()
    return _client
