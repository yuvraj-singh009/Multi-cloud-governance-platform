from app.database import get_supabase

db = get_supabase()

result = db.table("cloud_accounts").select("*").execute()

print("Supabase connection successful!")
print(result.data)