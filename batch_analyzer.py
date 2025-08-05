#!/usr/bin/env python3
"""
Batch Repository Contributor Analyzer
Usage: python batch_analyzer.py url1 url2 url3 ...
"""

import subprocess
import tempfile
import os
import sys
from collections import Counter

def analyze_repo(github_url: str):
    """Quick analysis of a single repository"""
    print(f"📥 {github_url}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_name = github_url.split('/')[-1].replace('.git', '')
        clone_path = os.path.join(temp_dir, repo_name)
        
        try:
            # Clone quietly
            subprocess.run(['git', 'clone', '--quiet', github_url, clone_path], 
                         check=True, capture_output=True)
            
            # Get contributors
            result = subprocess.run(['git', '-C', clone_path, 'shortlog', '-sn', '--all'], 
                                  capture_output=True, text=True, check=True)
            
            contributors = {}
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.strip().split('\t', 1)
                    if len(parts) == 2:
                        contributors[parts[1]] = int(parts[0])
            
            print(f"   ✅ {len(contributors)} contributors")
            return contributors
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {}

def main():
    if len(sys.argv) < 2:
        print("Usage: python batch_analyzer.py <url1> <url2> <url3> ...")
        print("Example: python batch_analyzer.py https://github.com/user/repo1 user/repo2")
        return
    
    urls = []
    for arg in sys.argv[1:]:
        if not arg.startswith('http') and '/' in arg:
            arg = f"https://github.com/{arg}"
        urls.append(arg)
    
    print("🔍 Batch Repository Analysis")
    print("=" * 50)
    
    all_contributors = Counter()
    
    for url in urls:
        contributors = analyze_repo(url)
        for author, count in contributors.items():
            all_contributors[author] += count
    
    print("\n🏆 TOP 10 CONTRIBUTORS")
    print("=" * 50)
    
    for i, (author, commits) in enumerate(all_contributors.most_common(10), 1):
        print(f"{i:2d}. {author:<30} {commits:>6} commits")
    
    print(f"\nTotal: {len(all_contributors)} contributors, {sum(all_contributors.values())} commits")

if __name__ == "__main__":
    main()
