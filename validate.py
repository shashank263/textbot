#!/usr/bin/env python3
"""
TestBot Health Check & Validation Script

Validates all components are correctly installed and configured.
"""

import os
import sys
import json
import pickle
from pathlib import Path


def print_header():
    print("""
╔════════════════════════════════════════════════════════════════╗
║          TestBot - Health Check & Validation                  ║
╚════════════════════════════════════════════════════════════════╝
    """)


def check_python_version():
    """Check Python version."""
    print("1️⃣  Python Version")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 9:
        print("   ✅ OK\n")
        return True
    else:
        print("   ❌ Python 3.9+ required\n")
        return False


def check_packages():
    """Check if required packages are installed."""
    print("2️⃣  Required Packages")
    
    packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'pydantic': 'Pydantic',
        'sentence_transformers': 'Sentence Transformers',
        'faiss': 'FAISS',
        'bs4': 'BeautifulSoup4',
        'requests': 'Requests',
        'numpy': 'NumPy',
    }
    
    all_ok = True
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name}")
            all_ok = False
    
    if not all_ok:
        print("\n   Run: pip install -r requirements.txt\n")
    else:
        print()
    
    return all_ok


def check_files():
    """Check if required files exist."""
    print("3️⃣  Project Files")
    
    files = {
        'app/main.py': 'FastAPI App',
        'app/routes/chat.py': 'Chat Routes',
        'app/services/parser.py': 'Parser Service',
        'app/services/retrieval.py': 'Retrieval Service',
        'app/services/ranking.py': 'Ranking Service',
        'app/services/recommender.py': 'Recommender Service',
        'app/services/comparison.py': 'Comparison Service',
        'app/services/guardrails.py': 'Guardrails Service',
        'app/services/llm_service.py': 'LLM Service',
        'app/models/schemas.py': 'API Schemas',
        'scraper/scrape.py': 'Scraper',
        'config.py': 'Configuration',
        'requirements.txt': 'Requirements',
        'README.md': 'Documentation',
    }
    
    all_ok = True
    for file, name in files.items():
        if os.path.exists(file):
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name}")
            all_ok = False
    
    print()
    return all_ok


def check_vectorstore():
    """Check if vectorstore exists."""
    print("4️⃣  Vectorstore Files")
    
    vectorstore_files = {
        'vectorstore/faiss.index': 'FAISS Index',
        'vectorstore/metadata.pkl': 'Metadata',
        'data/processed_catalog.json': 'Processed Catalog',
    }
    
    all_ok = True
    for file, name in vectorstore_files.items():
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   ✅ {name} ({size:,} bytes)")
        else:
            print(f"   ⚠️  {name} (missing)")
            all_ok = False
    
    if not all_ok:
        print("\n   Run: python setup.py\n")
    else:
        print()
    
    return all_ok


def check_catalog():
    """Check if catalog has data."""
    print("5️⃣  SHL Catalog")
    
    try:
        with open('data/shl_catalog.json', 'r') as f:
            catalog = json.load(f)
        
        print(f"   ✅ Catalog loaded")
        print(f"   📊 {len(catalog)} assessments")
        
        # Show sample
        if catalog:
            print(f"   📌 Sample: {catalog[0].get('name')}")
        
        print()
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False


def check_ollama():
    """Check if Ollama is available."""
    print("6️⃣  Ollama (Optional)")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("   ✅ Ollama available")
            data = response.json()
            models = data.get('models', [])
            if models:
                print(f"   📌 Models: {len(models)} installed")
                for model in models[:3]:
                    print(f"      - {model.get('name')}")
            print()
            return True
    except:
        pass
    
    print("   ⚠️  Ollama not available (optional)")
    print("   💡 For enhanced features: ollama serve\n")
    return False  # Not critical


def check_api():
    """Check if API can start."""
    print("7️⃣  API Configuration")
    
    try:
        import fastapi
        from app.main import app
        
        print("   ✅ FastAPI app loads")
        print("   ✅ Routes configured")
        print()
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False


def print_summary(results):
    """Print validation summary."""
    print("="*60)
    print("  Summary")
    print("="*60 + "\n")
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}\n")
    
    if passed == total:
        print("🎉 All checks passed! Ready to run TestBot.\n")
        print("Next steps:")
        print("  1. python -m uvicorn app.main:app --reload")
        print("  2. python test.py")
        print("  3. Visit http://localhost:8000/docs\n")
    else:
        print("⚠️  Some checks failed. Please review above.\n")
        if passed >= total - 1:
            print("💡 Most components are ready.\n")


def main():
    print_header()
    
    results = [
        check_python_version(),
        check_packages(),
        check_files(),
        check_vectorstore(),
        check_catalog(),
        check_ollama(),
        check_api(),
    ]
    
    print_summary(results)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
