import anthropic
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_db_connection():
    """Create database connection"""
    # Use DATABASE_URL from environment (Railway sets this)
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Railway/Production - use DATABASE_URL
        conn = psycopg2.connect(
            database_url,
            cursor_factory=RealDictCursor
        )
    else:
        # Local development - use individual params
        conn = psycopg2.connect(
            host="localhost",
            database="knowledge_base",
            user="",  # Your Mac username for local
            password="",
            cursor_factory=RealDictCursor
        )
    
    return conn

def get_user_entries(user_id: int) -> list:
    """Get all knowledge entries for a user"""
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
        
        return [dict(entry) for entry in entries]
    except Exception as e:
        print(f"Error fetching entries: {e}")
        return []

def search_entries(user_id: int, query: str) -> list:
    """Search knowledge entries by keyword"""
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
        
        return [dict(entry) for entry in entries]
    except Exception as e:
        print(f"Error searching entries: {e}")
        return []

def search_by_tag(user_id: int, tag: str) -> list:
    """Search entries by tag"""
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
        
        return [dict(entry) for entry in entries]
    except Exception as e:
        print(f"Error searching by tag: {e}")
        return []

# Define tools for Claude
TOOLS = [
    {
        "name": "search_knowledge",
        "description": "Search through the user's knowledge base entries by keyword or topic",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant knowledge entries"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_all_entries",
        "description": "Get all knowledge base entries for the user - use this to get an overview of what the user knows",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "search_by_tag",
        "description": "Find knowledge entries that have a specific tag",
        "input_schema": {
            "type": "object",
            "properties": {
                "tag": {
                    "type": "string",
                    "description": "The tag to search for"
                }
            },
            "required": ["tag"]
        }
    }
]

def process_tool_call(tool_name: str, tool_input: dict, user_id: int) -> str:
    """Process a tool call from Claude"""
    print(f"Claude is calling tool: {tool_name} with {tool_input}")
    
    if tool_name == "search_knowledge":
        entries = search_entries(user_id, tool_input["query"])
        if not entries:
            return f"No entries found matching '{tool_input['query']}'"
        
        results = []
        for entry in entries:
            results.append({
                "id": entry['id'],
                "title": entry['title'],
                "content": str(entry['content']),
                "tags": entry['tags'] if entry['tags'] else [],
                "created_at": str(entry['created_at'])
            })
        return json.dumps({"found": len(results), "results": results})
    
    elif tool_name == "get_all_entries":
        entries = get_user_entries(user_id)
        if not entries:
            return "No entries found in knowledge base"
        
        results = []
        for entry in entries:
            results.append({
                "id": entry['id'],
                "title": entry['title'],
                "content": str(entry['content'])[:200] + "..." if len(str(entry['content'])) > 200 else str(entry['content']),
                "tags": entry['tags'] if entry['tags'] else [],
                "created_at": str(entry['created_at'])
            })
        return json.dumps({"total": len(results), "entries": results})
    
    elif tool_name == "search_by_tag":
        entries = search_by_tag(user_id, tool_input["tag"])
        if not entries:
            return f"No entries found with tag '{tool_input['tag']}'"
        
        results = []
        for entry in entries:
            results.append({
                "id": entry['id'],
                "title": entry['title'],
                "content": str(entry['content']),
                "tags": entry['tags'] if entry['tags'] else [],
                "created_at": str(entry['created_at'])
            })
        return json.dumps({"found": len(results), "results": results})
    
    return f"Unknown tool: {tool_name}"

def chat_with_knowledge_base(message: str, user_id: int) -> str:
    """
    Send a message to Claude with access to the user's knowledge base tools
    Claude will decide which tools to use to answer the question
    """
    print(f"\nUser message: {message}")
    print(f"User ID: {user_id}")
    
    messages = [{"role": "user", "content": message}]
    
    # Agentic loop - Claude may call multiple tools
    while True:
        response = client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=1024,
            system="""You are a helpful AI assistant with access to the user's personal knowledge base. 
            Use the available tools to search and retrieve relevant information to answer questions.
            Always search the knowledge base before answering questions about what the user knows.
            Be concise and helpful in your responses.""",
            tools=TOOLS,
            messages=messages
        )
        
        print(f"Claude response type: {response.stop_reason}")
        
        # If Claude is done, return the response
        if response.stop_reason == "end_turn":
            # Extract text from response
            for block in response.content:
                if hasattr(block, 'text'):
                    return block.text
            return "I couldn't generate a response."
        
        # If Claude wants to use tools
        if response.stop_reason == "tool_use":
            # Add Claude's response to messages
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Process each tool call
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_result = process_tool_call(
                        block.name,
                        block.input,
                        user_id
                    )
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_result
                    })
            
            # Add tool results to messages
            messages.append({
                "role": "user",
                "content": tool_results
            })
            
            # Continue the loop - Claude will process tool results
            continue
        
        # Unexpected stop reason
        break
    
    return "Something went wrong with the AI response."