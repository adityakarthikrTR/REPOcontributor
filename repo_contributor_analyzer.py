#!/usr/bin/env python3
"""
Git Repository Contributor Analyzer
Analyzes multiple Git repositories to find top contributors by commit count
"""

import os
import subprocess
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import argparse

def get_git_contributors(repo_path: str) -> Dict[str, int]:
    """
    Get contributors and their commit counts from a local Git repository
    """
    try:
        # Change to repository directory
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        # Get commit authors with count
        result = subprocess.run([
            'git', 'shortlog', '-sn', '--all'
        ], capture_output=True, text=True, check=True)
        
        contributors = {}
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                parts = line.strip().split('\t', 1)
                if len(parts) == 2:
                    count = int(parts[0])
                    author = parts[1]
                    contributors[author] = count
        
        os.chdir(original_dir)
        return contributors
        
    except subprocess.CalledProcessError as e:
        print(f"Error analyzing {repo_path}: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error analyzing {repo_path}: {e}")
        return {}

def get_repo_info(repo_path: str) -> Dict:
    """
    Get basic repository information
    """
    try:
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        # Get repository name
        repo_name = Path(repo_path).name
        
        # Get total commits
        total_commits = subprocess.run([
            'git', 'rev-list', '--all', '--count'
        ], capture_output=True, text=True, check=True)
        
        # Get current branch
        current_branch = subprocess.run([
            'git', 'branch', '--show-current'
        ], capture_output=True, text=True, check=True)
        
        # Get remote URL if available
        try:
            remote_url = subprocess.run([
                'git', 'remote', 'get-url', 'origin'
            ], capture_output=True, text=True, check=True)
            remote_url = remote_url.stdout.strip()
        except:
            remote_url = "No remote"
        
        os.chdir(original_dir)
        
        return {
            'name': repo_name,
            'path': repo_path,
            'total_commits': int(total_commits.stdout.strip()) if total_commits.stdout.strip() else 0,
            'current_branch': current_branch.stdout.strip() if current_branch.stdout.strip() else 'unknown',
            'remote_url': remote_url
        }
        
    except Exception as e:
        print(f"Error getting repo info for {repo_path}: {e}")
        return {
            'name': Path(repo_path).name,
            'path': repo_path,
            'total_commits': 0,
            'current_branch': 'unknown',
            'remote_url': 'unknown'
        }

def find_git_repos(search_path: str, max_depth: int = 3) -> List[str]:
    """
    Find all Git repositories in the given path
    """
    git_repos = []
    search_path = Path(search_path)
    
    # First check if the search path itself is a git repository
    if (search_path / '.git').exists():
        git_repos.append(str(search_path))
        print(f"Found Git repo: {search_path}")
        return git_repos
    
    def scan_directory(path: Path, current_depth: int):
        if current_depth > max_depth:
            return
            
        try:
            for item in path.iterdir():
                if item.is_dir():
                    # Check if this is a Git repository
                    if (item / '.git').exists():
                        git_repos.append(str(item))
                        print(f"Found Git repo: {item}")
                    else:
                        # Recursively scan subdirectories
                        scan_directory(item, current_depth + 1)
        except PermissionError:
            print(f"Permission denied: {path}")
        except Exception as e:
            print(f"Error scanning {path}: {e}")
    
    scan_directory(search_path, 0)
    return git_repos

def analyze_repositories(repo_paths: List[str]) -> Tuple[Dict, List[Dict]]:
    """
    Analyze multiple repositories and return aggregated contributor data
    """
    all_contributors = Counter()
    repo_details = []
    
    for repo_path in repo_paths:
        print(f"\nAnalyzing: {repo_path}")
        
        # Get repository info
        repo_info = get_repo_info(repo_path)
        
        # Get contributors
        contributors = get_git_contributors(repo_path)
        
        if contributors:
            # Add to global count
            for author, count in contributors.items():
                all_contributors[author] += count
            
            # Store repo details
            repo_info['contributors'] = contributors
            repo_info['top_contributor'] = max(contributors.items(), key=lambda x: x[1])
            repo_details.append(repo_info)
            
            print(f"  - {len(contributors)} contributors, {repo_info['total_commits']} total commits")
        else:
            print(f"  - No contributors found or error occurred")
    
    return dict(all_contributors), repo_details

def print_results(all_contributors: Dict[str, int], repo_details: List[Dict]):
    """
    Print formatted results
    """
    if not all_contributors:
        print("No contributors found!")
        return
    
    print("\n" + "="*80)
    print("🏆 TOP CONTRIBUTORS ACROSS ALL REPOSITORIES")
    print("="*80)
    
    # Sort contributors by total commits
    sorted_contributors = sorted(all_contributors.items(), key=lambda x: x[1], reverse=True)
    
    for i, (author, total_commits) in enumerate(sorted_contributors[:20], 1):
        print(f"{i:2d}. {author:<40} {total_commits:>6} commits")
    
    print("\n" + "="*80)
    print("📊 REPOSITORY BREAKDOWN")
    print("="*80)
    
    # Sort repos by total commits
    repo_details.sort(key=lambda x: x['total_commits'], reverse=True)
    
    for repo in repo_details:
        print(f"\n📁 {repo['name']}")
        print(f"   Path: {repo['path']}")
        print(f"   Total commits: {repo['total_commits']}")
        print(f"   Branch: {repo['current_branch']}")
        if repo['remote_url'] != 'No remote':
            print(f"   Remote: {repo['remote_url']}")
        
        if 'top_contributor' in repo:
            author, commits = repo['top_contributor']
            print(f"   Top contributor: {author} ({commits} commits)")

def save_to_json(all_contributors: Dict[str, int], repo_details: List[Dict], output_file: str):
    """
    Save results to JSON file
    """
    data = {
        'analysis_date': str(Path.cwd()),
        'total_repositories': len(repo_details),
        'total_unique_contributors': len(all_contributors),
        'top_contributors': dict(sorted(all_contributors.items(), key=lambda x: x[1], reverse=True)),
        'repositories': repo_details
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Analyze Git repositories to find top contributors')
    parser.add_argument('path', nargs='?', default='.', help='Path to search for Git repositories (default: current directory)')
    parser.add_argument('--depth', type=int, default=3, help='Maximum depth to search for repositories (default: 3)')
    parser.add_argument('--output', '-o', help='Output JSON file name')
    
    args = parser.parse_args()
    
    print("🔍 Git Repository Contributor Analyzer")
    print("="*50)
    
    # Find all Git repositories
    print(f"Searching for Git repositories in: {args.path}")
    print(f"Maximum search depth: {args.depth}")
    
    repo_paths = find_git_repos(args.path, args.depth)
    
    if not repo_paths:
        print("❌ No Git repositories found!")
        return
    
    print(f"\n✅ Found {len(repo_paths)} Git repositories")
    
    # Analyze repositories
    all_contributors, repo_details = analyze_repositories(repo_paths)
    
    # Print results
    print_results(all_contributors, repo_details)
    
    # Save to JSON if requested
    if args.output:
        save_to_json(all_contributors, repo_details, args.output)
    
    print(f"\n🎉 Analysis complete! Analyzed {len(repo_details)} repositories.")

if __name__ == "__main__":
    main()
