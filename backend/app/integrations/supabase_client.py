from app.db.supabase import get_supabase

# Re-export para conveniencia al importar desde integrations
__all__ = ["get_supabase"]
