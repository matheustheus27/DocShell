#!/usr/bin/env python3
"""
DocShell Backend - Main App Re-export for Backward Compatibility
"""

from scripts.rag.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("scripts.rag.main:app", host="0.0.0.0", port=8080, reload=True)
