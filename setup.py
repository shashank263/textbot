#!/usr/bin/env python3
"""
TestBot Setup Script

Guides through complete setup:
1. Scrape SHL catalog
2. Generate embeddings
3. Create FAISS index
4. Verify vectorstore
5. Check Ollama availability
"""

import os
import sys
import json
import pickle
import subprocess
from pathlib import Path


def print_banner():
    """Print welcome banner."""
    print("""
╔════════════════════════════════════════════════════════════════╗
║       TestBot - SHL Assessment Recommendation Chatbot          ║
║                    Setup & Initialization                       ║
╚════════════════════════════════════════════════════════════════╝
    """)


def print_section(title):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def check_python_version():
    """Verify Python version."""
    print_section("1. Checking Python Version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ ERROR: Python 3.9+ required")
        sys.exit(1)
    
    print("✅ Python version OK\n")


def check_dependencies():
    """Check if required packages are installed."""
    print_section("2. Checking Dependencies")
    
    required = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'sentence_transformers',
        'faiss',
        'bs4',
        'requests',
        'numpy',
        'ollama',
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package if package != 'bs4' else 'bs4.element')
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies installed\n")
    return True


def scrape_catalog():
    """Scrape SHL catalog."""
    print_section("3. Scraping SHL Catalog")
    
    try:
        from scraper.scrape import SHLScraper
        
        scraper = SHLScraper("data/shl_catalog.json")
        catalog = scraper.scrape()
        scraper.save_catalog()
        
        print(f"✅ Scraped {len(catalog)} assessments")
        print(f"✅ Saved to: data/shl_catalog.json\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False


def generate_embeddings():
    """Generate embeddings and FAISS index."""
    print_section("4. Generating Embeddings & FAISS Index")
    
    try:
        from app.services.retrieval import CatalogProcessor
        
        processor = CatalogProcessor()
        
        print("Loading and processing catalog...")
        processor.process_catalog()
        
        print("Generating embeddings (this may take 1-2 minutes)...")
        processor.generate_embeddings()
        
        print("Creating FAISS index...")
        processor.save_embeddings_and_metadata("vectorstore")
        
        print("✅ Vectorstore ready\n")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False


def verify_vectorstore():
    """Verify vectorstore files exist."""
    print_section("5. Verifying Vectorstore")
    
    files = [
        "data/shl_catalog.json",
        "data/processed_catalog.json",
        "vectorstore/faiss.index",
        "vectorstore/metadata.pkl"
    ]
    
    all_ok = True
    for file in files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} ({size:,} bytes)")
        else:
            print(f"❌ {file} (MISSING)")
            all_ok = False
    
    print()
    return all_ok


def check_ollama():
    """Check if Ollama service is available."""
    print_section("6. Checking Ollama (Optional)")
    
    try:
        from app.services.llm_service import LLMService
        
        llm = LLMService()
        
        if llm.is_available():
            print("✅ Ollama service available at http://localhost:11434")
            print("✅ Enhanced conversation features enabled\n")
            return True
        else:
            print("⚠️  Ollama not available")
            print("   TestBot will work with fallback responses")
            print("   To enable: ollama serve (in another terminal)")
            print("   Then: ollama pull llama3\n")
            return False
            
    except Exception as e:
        print(f"⚠️  Ollama check failed: {e}\n")
        return False


def print_next_steps():
    """Print next steps."""
    print_section("Setup Complete!")
    
    print("""
🎉 TestBot is ready to run!

Next steps:

1. Start the server:
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

2. In another terminal (optional, for enhanced features):
   ollama serve

3. Test the API:
   curl -X POST http://localhost:8000/chat \\
     -H "Content-Type: application/json" \\
     -d '{"messages": [{"role": "user", "content": "Hiring Java developer"}]}'

4. View API documentation:
   http://localhost:8000/docs

5. Check health:
   curl http://localhost:8000/health

For more info, see README.md

    """)


def main():
    """Run full setup."""
    print_banner()
    
    # Change to testbot directory
    testbot_dir = Path(__file__).parent
    os.chdir(testbot_dir)
    
    # Run checks
    check_python_version()
    
    if not check_dependencies():
        print("\n❌ Please install dependencies first:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Run setup
    if not scrape_catalog():
        print("⚠️  Scraping failed, but continuing...")
    
    if not generate_embeddings():
        print("❌ Embedding generation failed")
        sys.exit(1)
    
    if not verify_vectorstore():
        print("⚠️  Some files missing, but setup may still work")
    
    check_ollama()
    
    print_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
