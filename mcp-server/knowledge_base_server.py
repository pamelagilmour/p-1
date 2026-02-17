import psycopg2
from psycopg2.extras import RealDictCursor
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import json

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("knowledge-base")

def get_db_connection():
    """Create database connection"""
    conn = psycopg2.connect(
        host="localhost",
        database="knowledge_base",
        user="",  # Your Mac username
        password="",
        cursor_factory=RealDictCursor
    )
    return conn

# ============ MCP TOOLS ============

@mcp.tool()
def search_knowledge(query: str, user_id: int) -> str:
    """Search through the knowledge base entries by keyword or topic"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT id, title, content, tags, created_at
               FROM knowledge_entries
               WHERE user_id = %s 
               AND (
                   title ILIKE %s 
                   OR content ILIKE %s
               )
               ORDER BY created_at DESC
               LIMIT 5""",
            (user_id, f"%{query}%", f"%{query}%")
        )
        entries = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not entries:
            return f"No entries found matching '{query}'"
        
        results = []
        for entry in entries:
            tags = entry['tags'] if entry['tags'] else []
            results.append({
                "id": entry['id'],
                "title": entry['title'],
                "content": entry['content'],
                "tags": tags,
                "created_at": str(entry['created_at'])
            })
        
        return json.dumps({
            "found": len(results),
            "query": query,
            "results": results
        }, indent=2)
    
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"

@mcp.tool()
def get_all_entries(user_id: int) -> str:
    """Get all knowledge base entries for a specific user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT id, title, content, tags, created_at
               FROM knowledge_entries
               WHERE user_id = %s
               ORDER BY created_at DESC""",
            (user_id,)
        )
        entries = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not entries:
            return "No entries found in knowledge base"
        
        results = []
        for entry in entries:
            tags = entry['tags'] if entry['tags'] else []
            results.append({
                "id": entry['id'],
                "title": entry['title'],
                "content": entry['content'][:200] + "..." if len(entry['content']) > 200 else entry['content'],
                "tags": tags,
                "created_at": str(entry['created_at'])
            })
        
        return json.dumps({
            "total": len(results),
            "entries": results
        }, indent=2)
    
    except Exception as e:
        return f"Error fetching entries: {str(e)}"

@mcp.tool()
def get_entry_by_id(entry_id: int, user_id: int) -> str:
    """Get a specific knowledge entry by its ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT id, title, content, tags, created_at, updated_at
               FROM knowledge_entries
               WHERE id = %s AND user_id = %s""",
            (entry_id, user_id)
        )
        entry = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not entry:
            return f"Entry {entry_id} not found"
        
        tags = entry['tags'] if entry['tags'] else []
        
        return json.dumps({
            "id": entry['id'],
            "title": entry['title'],
            "content": entry['content'],
            "tags": tags,
            "created_at": str(entry['created_at']),
            "updated_at": str(entry['updated_at'])
        }, indent=2)
    
    except Exception as e:
        return f"Error fetching entry: {str(e)}"

@mcp.tool()
def search_by_tag(tag: str, user_id: int) -> str:
    """Find knowledge entries that have a specific tag"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT id, title, content, tags, created_at
               FROM knowledge_entries
               WHERE user_id = %s
               AND tags @> %s::text[]
               ORDER BY created_at DESC""",
            (user_id, [tag])
        )
        entries = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not entries:
            return f"No entries found with tag '{tag}'"
        
        results = []
        for entry in entries:
            tags = entry['tags'] if entry['tags'] else []
            results.append({
                "id": entry['id'],
                "title": entry['title'],
                "content": entry['content'],
                "tags": tags,
                "created_at": str(entry['created_at'])
            })
        
        return json.dumps({
            "tag": tag,
            "found": len(results),
            "results": results
        }, indent=2)
    
    except Exception as e:
        return f"Error searching by tag: {str(e)}"

if __name__ == "__main__":
    mcp.run()