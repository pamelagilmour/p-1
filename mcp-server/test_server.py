import psycopg2
from psycopg2.extras import RealDictCursor

def test_db_connection():
    """Test database connection directly"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="knowledge_base",
            user="",  # Your Mac username
            password="",
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        
        # Test search
        cursor.execute(
            """SELECT id, title, content, tags 
               FROM knowledge_entries 
               WHERE user_id = %s""",
            (4,)  # Your user ID
        )
        entries = cursor.fetchall()
        
        print(f"Found {len(entries)} entries:")
        for entry in entries:
            print(f"  - {entry['title']} (tags: {entry['tags']})")
        
        cursor.close()
        conn.close()
        print("\n✅ Database connection works!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_db_connection()