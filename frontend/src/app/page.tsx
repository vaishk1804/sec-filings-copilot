"use client";

import { useState } from "react";

export default function Home(){
  const [result,setResult] = useState<string>("");

  async function checkHealth(){
    setResult("Loading...");
    try{
      const base = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"
    
    const res = await fetch(`${base}/health`)
    const data = await res.json();
    setResult(JSON.stringify(data,null,2));
    } catch ( e:any){
      setResult(`Error: ${e?.message || String(e)}`);
    }
  }

  return(
    <main style={{padding:24,fontFamily:"system-ui"}}>
      <h1 style={{fontSize:28,fontWeight: 700}}>SEC Filings Copilot</h1>
      <p style={{marginTop:8, opacity: 0.8}}>
        Day 1: Next.js + FastAPI
      </p>

      <button
      onClick={checkHealth}
      style={{
        marginTop:16,
        padding: "10px 14px",
        borderRadius:10,
        border:"1px solid #ccc",
        cursor: "pointer",

      }}>
        Check Backend Health
      </button>
<pre 
style={{
  marginTop: 16,
  padding: 16,
  borderRadius: 12,
  border: "1px solid #eee",
  background: "#fafafa",
  overflowX: "auto",
}}>{result}</pre>
    </main>

  );
}