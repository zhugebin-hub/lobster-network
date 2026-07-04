#!/usr/bin/env python3
"""DuckDuckGo Search CLI Tool"""

import sys
import argparse

try:
    from duckduckgo_search import DDGS
except ImportError:
    print("Error: duckduckgo-search library not installed.", file=sys.stderr)
    print("Run: pip3 install --user duckduckgo-search", file=sys.stderr)
    sys.exit(1)

def search(query, num_results=10, region="us"):
    """Search DuckDuckGo and return results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, region=f"wt-{region}", max_results=num_results))
            return results
    except Exception as e:
        print(f"Search error: {e}", file=sys.stderr)
        return []

def main():
    parser = argparse.ArgumentParser(description="DuckDuckGo Search")
    parser.add_argument("query", nargs="+", help="Search query")
    parser.add_argument("--num", "-n", type=int, default=10, help="Number of results (default: 10)")
    parser.add_argument("--region", "-r", default="us", help="Region code (default: us)")
    
    args = parser.parse_args()
    query = " ".join(args.query)
    
    results = search(query, num_results=args.num, region=args.region)
    
    if not results:
        print("No results found.")
        return
    
    for i, r in enumerate(results, 1):
        print(f"\n[{i}] {r.get('title', 'N/A')}")
        print(f"    URL: {r.get('href', 'N/A')}")
        print(f"    {r.get('body', 'N/A')[:200]}...")

if __name__ == "__main__":
    main()
