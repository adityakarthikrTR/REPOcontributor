#!/usr/bin/env python3
"""
Quick Git Repository Contributor Analyzer
Enter a GitHub URL and get the top 5 contributors instantly
"""

import subprocess
import tempfile
import os
import sys
from pathlib import Path

def get_top_contributors(github_url: str, top_n: int = 5):
    """
    Clone a GitHub repository and get top N contributors
    """
    print(f"🔍 Analyzing: {github_url}")
    print("=" * 50)
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_name = github_url.split('/')[-1].replace('.git', '')
        clone_path = os.path.join(temp_dir, repo_name)
        
        try:
            # Clone repository
            print("📥 Cloning repository...")
            subprocess.run([
                'git', 'clone', github_url, clone_path
            ], check=True, capture_output=True)
            
            # Change to repository directory
            os.chdir(clone_path)
            
            # Get contributors
            print("📊 Analyzing contributors...")
            result = subprocess.run([
                'git', 'shortlog', '-sn', '--all'
            ], capture_output=True, text=True, check=True)
            
            # Parse and display top contributors
            contributors = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.strip().split('\t', 1)
                    if len(parts) == 2:
                        count = int(parts[0])
                        author = parts[1]
                        contributors.append((author, count))
            
            # Display top N contributors
            print(f"\n🏆 TOP {top_n} CONTRIBUTORS")
            print("=" * 50)
            
            for i, (author, commits) in enumerate(contributors[:top_n], 1):
                print(f"{i}. {author:<30} {commits:>6} commits")
            
            # Show total stats
            total_commits = sum(count for _, count in contributors)
            total_contributors = len(contributors)
            print(f"\n📈 Repository Stats:")
            print(f"   Total Contributors: {total_contributors}")
            print(f"   Total Commits: {total_commits}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            print("Make sure the repository URL is correct and accessible.")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

def main():
    print("🚀 Quick GitHub Repository Contributor Analyzer")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # URL provided as argument
        github_url = sys.argv[1]
    else:
        # Ask for URL
        github_url = input("Enter GitHub repository URL: ").strip()
    
    if not github_url:
        print("❌ No URL provided!")
        return
    
    # Ensure it's a proper GitHub URL
    if not github_url.startswith('http'):
        if '/' in github_url:
            # Assume it's in format owner/repo
            github_url = f"https://github.com/{github_url}"
        else:
            print("❌ Invalid URL format!")
            return
    
    get_top_contributors(github_url)

if __name__ == "__main__":
    main()
