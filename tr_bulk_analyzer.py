#!/usr/bin/env python3
"""
TR Repository Bulk Analyzer
Specialized tool for analyzing multiple TR repositories with automatic prefix
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import tempfile
import os
import threading
from collections import Counter

class TRRepoAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("TR Repository Bulk Analyzer")
        self.root.geometry("700x600")
        self.root.configure(bg='#f0f0f0')
        
        self.analyzing = False
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_frame = tk.Frame(self.root, bg='#f0f0f0')
        title_frame.pack(pady=10)
        
        title_label = tk.Label(title_frame, text="🔍 TR Repository Bulk Analyzer", 
                              font=('Arial', 16, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Auto-prefix: https://github.com/tr/", 
                                 font=('Arial', 12), bg='#f0f0f0', fg='#e74c3c')
        subtitle_label.pack()
        
        # Input Section
        input_frame = tk.LabelFrame(self.root, text="Repository Names", font=('Arial', 12, 'bold'),
                                   bg='#f0f0f0', fg='#2c3e50', padx=15, pady=15)
        input_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        instruction_label = tk.Label(input_frame, 
                                   text="📝 Paste repository names (one per line):\nExample: ras_shared-python-utils", 
                                   bg='#f0f0f0', font=('Arial', 10), justify='left')
        instruction_label.pack(anchor='w', pady=(0, 10))
        
        # Text area for repository names
        self.repo_text = scrolledtext.ScrolledText(input_frame, height=8, font=('Arial', 11),
                                                  bg='white', fg='#2c3e50', wrap=tk.WORD)
        self.repo_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Buttons
        button_frame = tk.Frame(input_frame, bg='#f0f0f0')
        button_frame.pack(fill='x')
        
        self.analyze_btn = tk.Button(button_frame, text="🚀 Analyze All Repositories", 
                                    command=self.start_analysis,
                                    bg='#27ae60', fg='white', font=('Arial', 12, 'bold'), 
                                    padx=20, pady=8)
        self.analyze_btn.pack(side='left')
        
        clear_btn = tk.Button(button_frame, text="Clear", command=self.clear_input,
                             bg='#95a5a6', fg='white', font=('Arial', 10, 'bold'), padx=15)
        clear_btn.pack(side='left', padx=(10, 0))
        
        example_btn = tk.Button(button_frame, text="Load Example", command=self.load_example,
                               bg='#f39c12', fg='white', font=('Arial', 10, 'bold'), padx=15)
        example_btn.pack(side='right')
        
        # Progress Section
        progress_frame = tk.LabelFrame(self.root, text="Progress", font=('Arial', 12, 'bold'),
                                      bg='#f0f0f0', fg='#2c3e50', padx=10, pady=10)
        progress_frame.pack(fill='x', padx=20, pady=10)
        
        self.progress_var = tk.StringVar(value="Ready to analyze TR repositories...")
        self.progress_label = tk.Label(progress_frame, textvariable=self.progress_var,
                                      bg='#f0f0f0', font=('Arial', 10))
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill='x', pady=5)
        
        # Results Section
        results_frame = tk.LabelFrame(self.root, text="Top 10 Contributors", font=('Arial', 12, 'bold'),
                                     bg='#f0f0f0', fg='#2c3e50', padx=10, pady=10)
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=12, font=('Consolas', 10),
                                                     bg='white', fg='#2c3e50')
        self.results_text.pack(fill='both', expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief='sunken', anchor='w',
                             bg='#ecf0f1', font=('Arial', 9))
        status_bar.pack(side='bottom', fill='x')
    
    def clear_input(self):
        """Clear the input text area"""
        self.repo_text.delete(1.0, tk.END)
        self.status_var.set("Input cleared")
    
    def load_example(self):
        """Load example repository names"""
        example_repos = """ras_shared-python-utils
ras_ai_trajectory
ras-search_enhanced-document-retrieval"""
        
        self.repo_text.delete(1.0, tk.END)
        self.repo_text.insert(1.0, example_repos)
        self.status_var.set("Example repositories loaded")
    
    def start_analysis(self):
        """Start the analysis in a separate thread"""
        repo_names = self.get_repo_names()
        
        if not repo_names:
            messagebox.showwarning("No Repositories", "Please enter at least one repository name")
            return
        
        if self.analyzing:
            messagebox.showinfo("Analysis in Progress", "Please wait for the current analysis to complete")
            return
        
        self.analyzing = True
        self.analyze_btn.config(state='disabled', text="Analyzing...")
        self.progress_bar.start()
        self.results_text.delete(1.0, tk.END)
        
        # Start analysis in separate thread
        thread = threading.Thread(target=self.analyze_repositories, args=(repo_names,))
        thread.daemon = True
        thread.start()
    
    def get_repo_names(self):
        """Extract repository names from text area"""
        text_content = self.repo_text.get(1.0, tk.END).strip()
        if not text_content:
            return []
        
        # Split by lines and clean each name
        repo_names = []
        for line in text_content.split('\n'):
            line = line.strip()
            if line:
                # Remove any existing prefixes
                repo_name = line.replace('https://github.com/tr/', '').replace('https://github.com/', '')
                if repo_name:
                    repo_names.append(repo_name)
        
        return repo_names
    
    def analyze_repositories(self, repo_names):
        """Analyze all repositories"""
        all_contributors = Counter()
        successful_repos = []
        failed_repos = []
        
        try:
            total_repos = len(repo_names)
            
            for i, repo_name in enumerate(repo_names, 1):
                url = f"https://github.com/tr/{repo_name}"
                self.progress_var.set(f"Analyzing {i}/{total_repos}: {repo_name}")
                
                contributors = self.analyze_single_repo(url, repo_name)
                
                if contributors:
                    for author, count in contributors.items():
                        all_contributors[author] += count
                    successful_repos.append((repo_name, len(contributors), sum(contributors.values())))
                else:
                    failed_repos.append(repo_name)
            
            # Display results in main thread
            self.root.after(0, self.display_results, all_contributors, successful_repos, failed_repos)
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
    
    def analyze_single_repo(self, github_url, repo_name):
        """Analyze a single repository"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                clone_path = os.path.join(temp_dir, repo_name)
                
                # Clone repository quietly
                result = subprocess.run(['git', 'clone', '--quiet', github_url, clone_path], 
                                      capture_output=True, text=True)
                
                if result.returncode != 0:
                    return {}
                
                # Get contributors
                result = subprocess.run(['git', '-C', clone_path, 'shortlog', '-sn', '--all'], 
                                      capture_output=True, text=True, check=True)
                
                contributors = {}
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.strip().split('\t', 1)
                        if len(parts) == 2:
                            contributors[parts[1]] = int(parts[0])
                
                return contributors
                
        except Exception:
            return {}
    
    def display_results(self, all_contributors, successful_repos, failed_repos):
        """Display analysis results"""
        self.analyzing = False
        self.analyze_btn.config(state='normal', text="🚀 Analyze All Repositories")
        self.progress_bar.stop()
        self.progress_var.set("Analysis complete!")
        
        # Clear results
        self.results_text.delete(1.0, tk.END)
        
        if not all_contributors:
            self.results_text.insert(tk.END, "❌ No contributors found in any repository.\n")
            if failed_repos:
                self.results_text.insert(tk.END, f"\nFailed repositories: {', '.join(failed_repos)}\n")
            return
        
        # Top 10 Contributors
        self.results_text.insert(tk.END, "🏆 TOP 10 CONTRIBUTORS (TR Repositories)\n")
        self.results_text.insert(tk.END, "=" * 50 + "\n\n")
        
        sorted_contributors = sorted(all_contributors.items(), key=lambda x: x[1], reverse=True)
        
        for i, (author, total_commits) in enumerate(sorted_contributors[:10], 1):
            self.results_text.insert(tk.END, f"{i:2d}. {author:<30} {total_commits:>6} commits\n")
        
        # Summary
        total_successful = len(successful_repos)
        total_failed = len(failed_repos)
        total_unique_contributors = len(all_contributors)
        total_commits = sum(all_contributors.values())
        
        self.results_text.insert(tk.END, f"\n{'=' * 50}\n")
        self.results_text.insert(tk.END, "📊 SUMMARY\n")
        self.results_text.insert(tk.END, f"{'=' * 50}\n")
        self.results_text.insert(tk.END, f"✅ Successful: {total_successful} repositories\n")
        if total_failed > 0:
            self.results_text.insert(tk.END, f"❌ Failed: {total_failed} repositories\n")
        self.results_text.insert(tk.END, f"👥 Unique Contributors: {total_unique_contributors}\n")
        self.results_text.insert(tk.END, f"📝 Total Commits: {total_commits}\n")
        
        # Repository breakdown
        if successful_repos:
            self.results_text.insert(tk.END, f"\n{'=' * 50}\n")
            self.results_text.insert(tk.END, "📁 REPOSITORY BREAKDOWN\n")
            self.results_text.insert(tk.END, f"{'=' * 50}\n")
            
            for repo_name, contributors_count, commits_count in successful_repos:
                self.results_text.insert(tk.END, f"📁 {repo_name}: {contributors_count} contributors, {commits_count} commits\n")
        
        if failed_repos:
            self.results_text.insert(tk.END, f"\n❌ Failed repositories: {', '.join(failed_repos)}\n")
        
        self.status_var.set(f"Complete! {total_successful} repos analyzed, {total_unique_contributors} contributors found")
    
    def show_error(self, error_msg):
        """Show error message"""
        self.analyzing = False
        self.analyze_btn.config(state='normal', text="🚀 Analyze All Repositories")
        self.progress_bar.stop()
        self.progress_var.set("Analysis failed!")
        messagebox.showerror("Analysis Error", f"An error occurred:\n{error_msg}")

def main():
    root = tk.Tk()
    app = TRRepoAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
