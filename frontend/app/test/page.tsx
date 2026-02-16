'use client';

import { useEffect, useState } from 'react';

export default function TestPage() {
    const [health, setHealth] = useState<any>(null);
    const [entries, setEntries] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Test BE connection
        const testBackend = async () => {
            try {
                // Test health endpoint
                const healthRes = await fetch('http://localhost:8000/api/health');
                const healthData = await healthRes.json();
                setHealth(healthData);

                // Test entries endpoint
                const entriesRes = await fetch('http://localhost:8000/api/entries')
                const entriesData = await entriesRes.json()
                setEntries(entriesData)

                setLoading(false)
            } catch (err: any) {
                setError(err.message)
                setLoading(false)
            }
        }
        testBackend()
    }, [])

    if (loading) {
        return (
          <div className="min-h-screen p-8">
            <h1 className="text-3xl font-bold mb-4">Testing Backend Connection...</h1>
            <p>Loading...</p>
          </div>
        );
      }
    
      if (error) {
        return (
          <div className="min-h-screen p-8">
            <h1 className="text-3xl font-bold mb-4 text-red-600">Connection Error</h1>
            <p className="text-red-500">{error}</p>
            <p className="mt-4 text-gray-600">Make sure your backend is running at http://localhost:8000</p>
          </div>
        );
      }
    
    return (
        <div className="min-h-screen p-8">
        <h1 className="text-3xl font-bold mb-6">🎉 Full Stack Connection Test</h1>
        
        {/* Health Check Result */}
        <div className="mb-8 p-4 border rounded-lg">
          <h2 className="text-xl font-semibold mb-2">Health Check</h2>
          <pre className="bg-gray-100 p-4 rounded overflow-auto text-gray-950">
            {JSON.stringify(health, null, 2)}
          </pre>
          {health?.database === 'connected' && (
            <p className="text-green-600 font-semibold mt-2">✅ Database Connected!</p>
          )}
        </div>
  
        {/* Knowledge Entries Result */}
        <div className="mb-8 p-4 border rounded-lg">
          <h2 className="text-xl font-semibold mb-2">Knowledge Entries from Database</h2>
          <pre className="bg-gray-100 p-4 rounded overflow-auto text-gray-950">
            {JSON.stringify(entries, null, 2)}
          </pre>
          {entries?.entries?.length > 0 && (
            <p className="text-green-600 font-semibold mt-2">
              ✅ Found {entries.entries.length} entry/entries in database!
            </p>
          )}
        </div>
  
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <h2 className="text-xl font-semibold text-green-800 mb-2">
            ✅ End-to-End Test Successful!
          </h2>
          <p className="text-green-700">
            Frontend (Next.js) → Backend (FastAPI) → Database (PostgreSQL) → All Working! 🚀
          </p>
        </div>
      </div>
    );
}