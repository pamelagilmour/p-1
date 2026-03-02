"""
Run the audit logs migration
Creates the audit_logs table with proper indexes
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    """Run the audit logs migration"""
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        conn = psycopg2.connect(database_url)
    else:
        conn = psycopg2.connect(
            host="localhost",
            database="knowledge_base",
            user="",
            password=""
        )
    
    cursor = conn.cursor()
    
    # Read migration file
    with open('migrations/create_audit_logs.sql', 'r') as f:
        migration_sql = f.read()
    
    try:
        cursor.execute(migration_sql)
        conn.commit()
        print("✅ Audit logs table created successfully!")
        
        # Verify table was created
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'audit_logs'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print(f"\n📋 Created {len(columns)} columns:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        # Check indexes
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'audit_logs'
        """)
        indexes = cursor.fetchall()
        print(f"\n🔍 Created {len(indexes)} indexes:")
        for idx in indexes:
            print(f"  - {idx[0]}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_migration()
