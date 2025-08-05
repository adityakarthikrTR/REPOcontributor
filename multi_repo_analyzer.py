#!/usr/bin/env python3
"""
Multi-Repository Contributor Analyzer
Simple interface to analyze multiple GitHub repositories and get top 10 contributors
"""

import subprocess
import tempfile
import os
from pathlib import Path
from collections import Counter

def get_contributors_from_url(github_url: str):
    """
    Clone a GitHub repository and get all contributors
    Returns dictionary of {author: commit_count}
    """
    print(f"📥 Analyzing: {github_url}")
    
    # Create temporary directory for this repo
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_name = github_url.split('/')[-1].replace('.git', '')
        clone_path = os.path.join(temp_dir, repo_name)
        
        try:
            # Clone repository quietly
            subprocess.run([
                'git', 'clone', '--quiet', github_url, clone_path
            ], check=True, capture_output=True)
            
            # Change to repository directory
            original_dir = os.getcwd()
            os.chdir(clone_path)
            
            # Get contributors
            result = subprocess.run([
                'git', 'shortlog', '-sn', '--all'
            ], capture_output=True, text=True, check=True)
            
            # Parse contributors
            contributors = {}
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.strip().split('\t', 1)
                    if len(parts) == 2:
                        count = int(parts[0])
                        author = parts[1]
                        contributors[author] = count
            
            os.chdir(original_dir)
            print(f"   ✅ Found {len(contributors)} contributors")
            return contributors, repo_name
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Error cloning {github_url}: {e}")
            return {}, repo_name
        except Exception as e:
            print(f"   ❌ Unexpected error with {github_url}: {e}")
            return {}, repo_name

def analyze_multiple_repositories(urls):
    """
    Analyze multiple repositories and combine contributor data
    """
    all_contributors = Counter()
    repo_summaries = []
    
    print("🔍 Multi-Repository Contributor Analysis")
    print("=" * 60)
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing repository...")
        contributors, repo_name = get_contributors_from_url(url)
        
        if contributors:
            # Add to global count
            for author, count in contributors.items():
                all_contributors[author] += count
            
            # Store summary
            top_contributor = max(contributors.items(), key=lambda x: x[1])
            total_commits = sum(contributors.values())
            
            repo_summaries.append({
                'name': repo_name,
                'url': url,
                'contributors': len(contributors),
                'total_commits': total_commits,
                'top_contributor': top_contributor
            })
    
    return all_contributors, repo_summaries

def display_results(all_contributors, repo_summaries):
    """
    Display the combined results
    """
    print("\n" + "=" * 60)
    print("🏆 TOP 10 CONTRIBUTORS ACROSS ALL REPOSITORIES")
    print("=" * 60)
    
    if not all_contributors:
        print("❌ No contributors found!")
        return
    
    # Sort and display top 10
    sorted_contributors = sorted(all_contributors.items(), key=lambda x: x[1], reverse=True)
    
    for i, (author, total_commits) in enumerate(sorted_contributors[:10], 1):
        print(f"{i:2d}. {author:<35} {total_commits:>6} commits")
    
    # Summary statistics
    total_repos = len(repo_summaries)
    total_unique_contributors = len(all_contributors)
    total_commits = sum(all_contributors.values())
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY STATISTICS")
    print("=" * 60)
    print(f"Total Repositories Analyzed: {total_repos}")
    print(f"Total Unique Contributors: {total_unique_contributors}")
    print(f"Total Commits: {total_commits}")
    
    print("\n" + "=" * 60)
    print("📁 REPOSITORY BREAKDOWN")
    print("=" * 60)
    
    for repo in repo_summaries:
        print(f"\n📁 {repo['name']}")
        print(f"   URL: {repo['url']}")
        print(f"   Contributors: {repo['contributors']}")
        print(f"   Total Commits: {repo['total_commits']}")
        if repo['top_contributor']:
            author, commits = repo['top_contributor']
            print(f"   Top Contributor: {author} ({commits} commits)")

def get_urls_from_user():
    """
    Get multiple URLs from user input
    """
    print("🚀 Multi-Repository Contributor Analyzer")
    print("=" * 60)
    print("Enter GitHub repository URLs (one per line)")
    print("Press Enter twice when done, or type 'done' to finish")
    print("=" * 60)
    
    urls = []
    while True:
        url = input(f"Repository #{len(urls) + 1}: ").strip()
        
        if not url or url.lower() == 'done':
            break
            
        # Clean and validate URL
        if not url.startswith('http'):
            if '/' in url:
                # Assume it's in format owner/repo
                url = f"https://github.com/{url}"
            else:
                print("❌ Invalid URL format! Use: https://github.com/owner/repo or owner/repo")
                continue
        
        urls.append(url)
        print(f"   ✅ Added: {url}")
    
    return urls

def main():
    # Get URLs from user
    urls = get_urls_from_user()
    
    if not urls:
        print("❌ No URLs provided!")
        return
    
    print(f"\n🎯 Ready to analyze {len(urls)} repositories...")
    input("Press Enter to start analysis...")
    
    # Analyze repositories
    all_contributors, repo_summaries = analyze_multiple_repositories(urls)
    
    # Display results
    display_results(all_contributors, repo_summaries)
    
    print(f"\n🎉 Analysis complete!")

if __name__ == "__main__":
    main()
