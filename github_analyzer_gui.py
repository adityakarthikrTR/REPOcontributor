#!/usr/bin/env python3
"""
GUI Repository Contributor Analyzer
Simple graphical interface to analyze multiple GitHub repositories
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import tempfile
import os
import threading
from collections import Counter
from pathlib import Path

class GitHubAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Repository Contributor Analyzer")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.urls = []
        self.analyzing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_frame = tk.Frame(self.root, bg='#f0f0f0')
        title_frame.pack(pady=10)
        
        title_label = tk.Label(title_frame, text="🔍 GitHub Repository Contributor Analyzer", 
                              font=('Arial', 16, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Analyze multiple repositories to find top contributors", 
                                 font=('Arial', 10), bg='#f0f0f0', fg='#7f8c8d')
        subtitle_label.pack()
        
        # URL Input Section
        input_frame = tk.LabelFrame(self.root, text="Repository URLs", font=('Arial', 12, 'bold'),
                                   bg='#f0f0f0', fg='#2c3e50', padx=10, pady=10)
        input_frame.pack(fill='x', padx=20, pady=10)
        
        # URL entry
        url_entry_frame = tk.Frame(input_frame, bg='#f0f0f0')
        url_entry_frame.pack(fill='x', pady=5)
        
        tk.Label(url_entry_frame, text="Enter repository names (one per line):", bg='#f0f0f0', font=('Arial', 10)).pack(anchor='w')
        tk.Label(url_entry_frame, text="Auto-prefix: https://github.com/tr/", bg='#f0f0f0', font=('Arial', 9), fg='#7f8c8d').pack(anchor='w')
        
        # Multi-line text area for bulk input
        self.url_text = tk.Text(url_entry_frame, height=4, font=('Arial', 10), wrap=tk.WORD)
        self.url_text.pack(fill='x', pady=5)
        self.url_text.bind('<Control-Return>', self.add_bulk_urls_key)
        
        # Buttons for URL operations
        url_btn_frame = tk.Frame(url_entry_frame, bg='#f0f0f0')
        url_btn_frame.pack(fill='x', pady=5)
        
        add_bulk_btn = tk.Button(url_btn_frame, text="Add All URLs", command=self.add_bulk_urls,
                                bg='#3498db', fg='white', font=('Arial', 9, 'bold'), padx=15)
        add_bulk_btn.pack(side='left')
        
        clear_input_btn = tk.Button(url_btn_frame, text="Clear Input", command=self.clear_input,
                                   bg='#95a5a6', fg='white', font=('Arial', 9, 'bold'), padx=10)
        clear_input_btn.pack(side='left', padx=(10, 0))
        
        # Example text
        example_label = tk.Label(url_entry_frame, text="Example: ras_shared-python-utils, ras_ai_trajectory", 
                                bg='#f0f0f0', font=('Arial', 9), fg='#7f8c8d')
        example_label.pack(anchor='w', pady=(5, 0))
        
        # URL List
        list_frame = tk.Frame(input_frame, bg='#f0f0f0')
        list_frame.pack(fill='both', expand=True, pady=5)
        
        tk.Label(list_frame, text="Repository List:", bg='#f0f0f0', font=('Arial', 10)).pack(anchor='w')
        
        # Listbox with scrollbar
        listbox_frame = tk.Frame(list_frame, bg='#f0f0f0')
        listbox_frame.pack(fill='both', expand=True)
        
        self.url_listbox = tk.Listbox(listbox_frame, height=6, font=('Arial', 9))
        scrollbar = tk.Scrollbar(listbox_frame, orient='vertical', command=self.url_listbox.yview)
        self.url_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.url_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Buttons
        button_frame = tk.Frame(input_frame, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=10)
        
        remove_btn = tk.Button(button_frame, text="Remove Selected", command=self.remove_url,
                              bg='#e74c3c', fg='white', font=('Arial', 9, 'bold'), padx=10)
        remove_btn.pack(side='left')
        
        clear_btn = tk.Button(button_frame, text="Clear All", command=self.clear_urls,
                             bg='#95a5a6', fg='white', font=('Arial', 9, 'bold'), padx=10)
        clear_btn.pack(side='left', padx=(10, 0))
        
        self.analyze_btn = tk.Button(button_frame, text="🚀 Analyze Repositories", command=self.start_analysis,
                                    bg='#27ae60', fg='white', font=('Arial', 11, 'bold'), padx=20)
        self.analyze_btn.pack(side='right')
        
        # Progress Section
        progress_frame = tk.LabelFrame(self.root, text="Analysis Progress", font=('Arial', 12, 'bold'),
                                      bg='#f0f0f0', fg='#2c3e50', padx=10, pady=10)
        progress_frame.pack(fill='x', padx=20, pady=10)
        
        self.progress_var = tk.StringVar(value="Ready to analyze repositories...")
        self.progress_label = tk.Label(progress_frame, textvariable=self.progress_var,
                                      bg='#f0f0f0', font=('Arial', 10))
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill='x', pady=5)
        
        # Results Section
        results_frame = tk.LabelFrame(self.root, text="Top Contributors", font=('Arial', 12, 'bold'),
                                     bg='#f0f0f0', fg='#2c3e50', padx=10, pady=10)
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, font=('Consolas', 10),
                                                     bg='white', fg='#2c3e50')
        self.results_text.pack(fill='both', expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief='sunken', anchor='w',
                             bg='#ecf0f1', font=('Arial', 9))
        status_bar.pack(side='bottom', fill='x')
    
    def add_url_enter(self, event):
        """Add URL when Enter is pressed"""
        self.add_url()
    
    def add_bulk_urls_key(self, event):
        """Add bulk URLs when Ctrl+Enter is pressed"""
        self.add_bulk_urls()
    
    def clear_input(self):
        """Clear the input text area"""
        self.url_text.delete(1.0, tk.END)
    
    def add_bulk_urls(self):
        """Add multiple URLs from text area with tr/ prefix"""
        text_content = self.url_text.get(1.0, tk.END).strip()
        if not text_content:
            return
        
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        added_count = 0
        
        for line in lines:
            # Clean the line - remove any existing prefixes
            repo_name = line.replace('https://github.com/tr/', '').replace('https://github.com/', '')
            
            # Skip if empty after cleaning
            if not repo_name:
                continue
            
            # Add the tr/ prefix
            url = f"https://github.com/tr/{repo_name}"
            
            # Add to list if not duplicate
            if url not in self.urls:
                self.urls.append(url)
                self.url_listbox.insert(tk.END, url)
                added_count += 1
        
        if added_count > 0:
            self.status_var.set(f"Added {added_count} repositories. Total: {len(self.urls)}")
            self.url_text.delete(1.0, tk.END)  # Clear input after successful add
        else:
            messagebox.showinfo("No New URLs", "No new repositories were added (duplicates or empty)")
    
    def add_url(self):
        """Add single URL (legacy method, kept for compatibility)"""
        # This method is now less relevant but kept for any single URL entries
        pass
    
    def remove_url(self):
        """Remove selected URL from the list"""
        selection = self.url_listbox.curselection()
        if selection:
            index = selection[0]
            self.url_listbox.delete(index)
            del self.urls[index]
            self.status_var.set(f"Removed repository. Total: {len(self.urls)}")
    
    def clear_urls(self):
        """Clear all URLs"""
        if self.urls and messagebox.askyesno("Clear All", "Are you sure you want to clear all repositories?"):
            self.urls.clear()
            self.url_listbox.delete(0, tk.END)
            self.status_var.set("Cleared all repositories")
    
    def start_analysis(self):
        """Start the analysis in a separate thread"""
        if not self.urls:
            messagebox.showwarning("No URLs", "Please add at least one repository URL")
            return
        
        if self.analyzing:
            messagebox.showinfo("Analysis in Progress", "Please wait for the current analysis to complete")
            return
        
        self.analyzing = True
        self.analyze_btn.config(state='disabled', text="Analyzing...")
        self.progress_bar.start()
        self.results_text.delete(1.0, tk.END)
        
        # Start analysis in separate thread
        thread = threading.Thread(target=self.analyze_repositories)
        thread.daemon = True
        thread.start()
    
    def analyze_repositories(self):
        """Analyze all repositories"""
        all_contributors = Counter()
        repo_summaries = []
        
        try:
            total_repos = len(self.urls)
            
            for i, url in enumerate(self.urls, 1):
                # Update progress
                self.progress_var.set(f"Analyzing repository {i}/{total_repos}: {url}")
                
                contributors, repo_name = self.analyze_single_repo(url)
                
                if contributors:
                    for author, count in contributors.items():
                        all_contributors[author] += count
                    
                    top_contributor = max(contributors.items(), key=lambda x: x[1])
                    total_commits = sum(contributors.values())
                    
                    repo_summaries.append({
                        'name': repo_name,
                        'url': url,
                        'contributors': len(contributors),
                        'total_commits': total_commits,
                        'top_contributor': top_contributor
                    })
            
            # Display results in main thread
            self.root.after(0, self.display_results, all_contributors, repo_summaries)
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
    
    def analyze_single_repo(self, github_url):
        """Analyze a single repository"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_name = github_url.split('/')[-1].replace('.git', '')
                clone_path = os.path.join(temp_dir, repo_name)
                
                # Clone repository
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
                
                return contributors, repo_name
                
        except Exception as e:
            return {}, github_url.split('/')[-1]
    
    def display_results(self, all_contributors, repo_summaries):
        """Display analysis results"""
        self.analyzing = False
        self.analyze_btn.config(state='normal', text="🚀 Analyze Repositories")
        self.progress_bar.stop()
        self.progress_var.set("Analysis complete!")
        
        # Clear results
        self.results_text.delete(1.0, tk.END)
        
        if not all_contributors:
            self.results_text.insert(tk.END, "❌ No contributors found in any repository.\n")
            return
        
        # Top 10 Contributors
        self.results_text.insert(tk.END, "🏆 TOP 10 CONTRIBUTORS ACROSS ALL REPOSITORIES\n")
        self.results_text.insert(tk.END, "=" * 60 + "\n\n")
        
        sorted_contributors = sorted(all_contributors.items(), key=lambda x: x[1], reverse=True)
        
        for i, (author, total_commits) in enumerate(sorted_contributors[:10], 1):
            self.results_text.insert(tk.END, f"{i:2d}. {author:<35} {total_commits:>6} commits\n")
        
        # Summary Statistics
        total_repos = len(repo_summaries)
        total_unique_contributors = len(all_contributors)
        total_commits = sum(all_contributors.values())
        
        self.results_text.insert(tk.END, f"\n{'=' * 60}\n")
        self.results_text.insert(tk.END, "📊 SUMMARY STATISTICS\n")
        self.results_text.insert(tk.END, f"{'=' * 60}\n")
        self.results_text.insert(tk.END, f"Total Repositories Analyzed: {total_repos}\n")
        self.results_text.insert(tk.END, f"Total Unique Contributors: {total_unique_contributors}\n")
        self.results_text.insert(tk.END, f"Total Commits: {total_commits}\n")
        
        # Repository Breakdown
        self.results_text.insert(tk.END, f"\n{'=' * 60}\n")
        self.results_text.insert(tk.END, "📁 REPOSITORY BREAKDOWN\n")
        self.results_text.insert(tk.END, f"{'=' * 60}\n\n")
        
        for repo in repo_summaries:
            self.results_text.insert(tk.END, f"📁 {repo['name']}\n")
            self.results_text.insert(tk.END, f"   URL: {repo['url']}\n")
            self.results_text.insert(tk.END, f"   Contributors: {repo['contributors']}\n")
            self.results_text.insert(tk.END, f"   Total Commits: {repo['total_commits']}\n")
            if repo['top_contributor']:
                author, commits = repo['top_contributor']
                self.results_text.insert(tk.END, f"   Top Contributor: {author} ({commits} commits)\n")
            self.results_text.insert(tk.END, "\n")
        
        self.status_var.set(f"Analysis complete! Found {total_unique_contributors} contributors across {total_repos} repositories")
    
    def show_error(self, error_msg):
        """Show error message"""
        self.analyzing = False
        self.analyze_btn.config(state='normal', text="🚀 Analyze Repositories")
        self.progress_bar.stop()
        self.progress_var.set("Analysis failed!")
        messagebox.showerror("Analysis Error", f"An error occurred during analysis:\n{error_msg}")

def main():
    root = tk.Tk()
    app = GitHubAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
