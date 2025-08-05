#!/usr/bin/env python3
"""
TR Repository Top Contributors Analyzer
Simple GUI to find top contributors for each repository
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import tempfile
import os
import threading
import json
from datetime import datetime

class TopContributorsAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("TR Repository Top Contributors Analyzer")
        self.root.geometry("800x700")
        self.root.configure(bg='#f8f9fa')
        
        # Control variables
        self.analyzing = False
        self.stop_requested = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup simple and clean UI"""
        # Title section
        title_frame = tk.Frame(self.root, bg='#f8f9fa', pady=15)
        title_frame.pack(fill='x')
        
        title_label = tk.Label(title_frame, text="🏆 TR Repository Top Contributors", 
                              font=('Arial', 16, 'bold'), bg='#f8f9fa', fg='#2c3e50')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Find top contributors for each TR repository", 
                                 font=('Arial', 11), bg='#f8f9fa', fg='#7f8c8d')
        subtitle_label.pack()
        
        # Input section
        input_frame = tk.LabelFrame(self.root, text=" Repository Names ", 
                                   font=('Arial', 12, 'bold'), bg='#ffffff', 
                                   padx=20, pady=15)
        input_frame.pack(fill='x', padx=20, pady=10)
        
        # Instructions
        instruction_text = "📝 Enter TR repository names (one per line)\n💡 Auto-prefix: https://github.com/tr/"
        instruction_label = tk.Label(input_frame, text=instruction_text, 
                                    font=('Arial', 10), bg='#ffffff', fg='#666666', 
                                    justify='left')
        instruction_label.pack(anchor='w', pady=(0, 10))
        
        # Text input area
        self.repo_text = scrolledtext.ScrolledText(input_frame, height=6, 
                                                  font=('Consolas', 11), bg='#ffffff', 
                                                  fg='#2c3e50', relief='solid', bd=1)
        self.repo_text.pack(fill='both', expand=True, pady=(0, 15))
        
        # Buttons
        button_frame = tk.Frame(input_frame, bg='#ffffff')
        button_frame.pack(fill='x')
        
        self.analyze_btn = tk.Button(button_frame, text="🚀 Analyze Repositories", 
                                    command=self.start_analysis,
                                    bg='#28a745', fg='white', font=('Arial', 12, 'bold'), 
                                    padx=25, pady=10, relief='flat', cursor='hand2')
        self.analyze_btn.pack(side='left', padx=(0, 10))
        
        self.stop_btn = tk.Button(button_frame, text="⏹️ Stop", 
                                 command=self.stop_analysis,
                                 bg='#dc3545', fg='white', font=('Arial', 11, 'bold'), 
                                 padx=20, pady=10, relief='flat', cursor='hand2', 
                                 state='disabled')
        self.stop_btn.pack(side='left', padx=(0, 10))
        
        example_btn = tk.Button(button_frame, text="📝 Load Example", 
                               command=self.load_example,
                               bg='#007bff', fg='white', font=('Arial', 11), 
                               padx=15, pady=10, relief='flat', cursor='hand2')
        example_btn.pack(side='left', padx=(0, 10))
        
        clear_btn = tk.Button(button_frame, text="🗑️ Clear", 
                             command=self.clear_all,
                             bg='#6c757d', fg='white', font=('Arial', 11), 
                             padx=15, pady=10, relief='flat', cursor='hand2')
        clear_btn.pack(side='left')
        
        # Progress section
        progress_frame = tk.LabelFrame(self.root, text=" Analysis Progress ", 
                                      font=('Arial', 12, 'bold'), bg='#ffffff', 
                                      padx=20, pady=15)
        progress_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Ready to analyze repositories...")
        status_label = tk.Label(progress_frame, textvariable=self.status_var,
                               font=('Arial', 11), bg='#ffffff', fg='#2c3e50')
        status_label.pack(anchor='w', pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill='x', pady=(0, 10))
        
        self.stats_var = tk.StringVar(value="Repositories: 0 | Analyzed: 0 | Failed: 0")
        stats_label = tk.Label(progress_frame, textvariable=self.stats_var,
                              font=('Arial', 10), bg='#ffffff', fg='#7f8c8d')
        stats_label.pack(anchor='w')
        
        # Results section
        results_frame = tk.LabelFrame(self.root, text=" Top Contributors by Repository ", 
                                     font=('Arial', 12, 'bold'), bg='#ffffff', 
                                     padx=20, pady=15)
        results_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Results display
        self.results_text = scrolledtext.ScrolledText(results_frame, 
                                                     font=('Consolas', 10), 
                                                     bg='#f8f9fa', fg='#2c3e50',
                                                     relief='solid', bd=1)
        self.results_text.pack(fill='both', expand=True, pady=(0, 15))
        
        # Export button
        export_frame = tk.Frame(results_frame, bg='#ffffff')
        export_frame.pack(fill='x')
        
        self.save_btn = tk.Button(export_frame, text="💾 Save Results", 
                                 command=self.save_results,
                                 bg='#6f42c1', fg='white', font=('Arial', 11, 'bold'), 
                                 padx=20, pady=8, relief='flat', cursor='hand2',
                                 state='disabled')
        self.save_btn.pack(side='right')
    
    def load_example(self):
        """Load example repository names"""
        examples = """ras_shared-python-utils
ras_ai_trajectory
ras-search_enhanced-document-retrieval"""
        
        self.repo_text.delete(1.0, tk.END)
        self.repo_text.insert(1.0, examples)
        self.status_var.set("Example repositories loaded - Ready to analyze!")
    
    def clear_all(self):
        """Clear all inputs and results"""
        self.repo_text.delete(1.0, tk.END)
        self.results_text.delete(1.0, tk.END)
        self.status_var.set("Ready to analyze repositories...")
        self.stats_var.set("Repositories: 0 | Analyzed: 0 | Failed: 0")
        self.progress_bar['value'] = 0
        self.save_btn.config(state='disabled')
    
    def get_repo_names(self):
        """Extract and clean repository names"""
        content = self.repo_text.get(1.0, tk.END).strip()
        if not content:
            return []
        
        repos = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Clean repo name
                repo = line.replace('https://github.com/tr/', '').replace('https://github.com/', '')
                repo = repo.strip('/')
                if repo:
                    repos.append(repo)
        return repos
    
    def start_analysis(self):
        """Start repository analysis"""
        repo_names = self.get_repo_names()
        
        if not repo_names:
            messagebox.showwarning("No Repositories", 
                                 "Please enter at least one repository name!")
            return
        
        if self.analyzing:
            messagebox.showinfo("Analysis Running", 
                              "Analysis is already in progress!")
            return
        
        # Reset states
        self.analyzing = True
        self.stop_requested = False
        self.analyze_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.save_btn.config(state='disabled')
        
        # Setup progress
        self.progress_bar['maximum'] = len(repo_names)
        self.progress_bar['value'] = 0
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        # Start analysis in background thread
        self.analysis_thread = threading.Thread(target=self.analyze_repositories, 
                                               args=(repo_names,))
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
    
    def stop_analysis(self):
        """Stop the analysis"""
        if self.analyzing:
            self.stop_requested = True
            self.status_var.set("Stopping analysis... Please wait.")
    
    def analyze_repositories(self, repo_names):
        """Analyze all repositories"""
        successful_repos = []
        failed_repos = []
        
        try:
            # Display header
            header = f"🏆 TOP CONTRIBUTORS ANALYSIS\n"
            header += f"{'='*60}\n"
            header += f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            header += f"📊 Total Repositories: {len(repo_names)}\n\n"
            
            self.root.after(0, lambda: self.results_text.insert(tk.END, header))
            
            for i, repo_name in enumerate(repo_names):
                if self.stop_requested:
                    break
                
                # Update progress
                progress = f"Analyzing {i+1}/{len(repo_names)}: {repo_name}"
                self.root.after(0, lambda p=progress: self.status_var.set(p))
                self.root.after(0, lambda v=i+1: setattr(self.progress_bar, 'value', v))
                
                # Analyze single repository
                result = self.analyze_single_repo(repo_name)
                
                if result:
                    successful_repos.append(result)
                    self.root.after(0, lambda r=result: self.display_repo_result(r))
                else:
                    failed_repos.append(repo_name)
                    error_msg = f"❌ Failed: {repo_name}\n\n"
                    self.root.after(0, lambda msg=error_msg: self.results_text.insert(tk.END, msg))
                
                # Update stats
                stats = f"Repositories: {i+1} | Analyzed: {len(successful_repos)} | Failed: {len(failed_repos)}"
                self.root.after(0, lambda s=stats: self.stats_var.set(s))
                
                if self.stop_requested:
                    break
            
            # Display summary
            self.root.after(0, lambda: self.display_summary(successful_repos, failed_repos))
            
            # Store results for saving
            self.analysis_results = {
                'successful_repos': successful_repos,
                'failed_repos': failed_repos,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Analysis error: {str(e)}"
            self.root.after(0, lambda: self.status_var.set(error_msg))
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        
        finally:
            self.root.after(0, self.analysis_finished)
    
    def analyze_single_repo(self, repo_name):
        """Analyze a single repository and return top contributors"""
        try:
            url = f"https://github.com/tr/{repo_name}"
            
            with tempfile.TemporaryDirectory() as temp_dir:
                clone_path = os.path.join(temp_dir, repo_name)
                
                # Clone repository
                clone_cmd = ['git', 'clone', '--quiet', url, clone_path]
                clone_result = subprocess.run(clone_cmd, capture_output=True, 
                                            text=True, timeout=45)
                
                if clone_result.returncode != 0:
                    return None
                
                if self.stop_requested:
                    return None
                
                # Get contributors
                git_cmd = ['git', '-C', clone_path, 'shortlog', '-sn', '--all']
                result = subprocess.run(git_cmd, capture_output=True, 
                                      text=True, timeout=30)
                
                if result.returncode != 0:
                    return None
                
                contributors = {}
                total_commits = 0
                
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.strip().split('\t', 1)
                        if len(parts) == 2:
                            count = int(parts[0])
                            author = parts[1]
                            contributors[author] = count
                            total_commits += count
                
                return {
                    'name': repo_name,
                    'url': url,
                    'contributors': contributors,
                    'total_commits': total_commits,
                    'contributor_count': len(contributors)
                }
                
        except Exception:
            return None
    
    def display_repo_result(self, repo_data):
        """Display results for a single repository"""
        result_text = f"📁 {repo_data['name'].upper()}\n"
        result_text += f"🌐 {repo_data['url']}\n"
        result_text += f"📊 {repo_data['total_commits']:,} total commits | {repo_data['contributor_count']} contributors\n\n"
        
        # Sort contributors by commit count
        sorted_contributors = sorted(repo_data['contributors'].items(), 
                                   key=lambda x: x[1], reverse=True)
        
        # Show top 10 contributors (or all if less than 10)
        top_count = min(10, len(sorted_contributors))
        result_text += f"🏆 TOP {top_count} CONTRIBUTORS:\n"
        result_text += f"{'-'*50}\n"
        
        for i, (author, commits) in enumerate(sorted_contributors[:top_count], 1):
            percentage = (commits / repo_data['total_commits'] * 100) if repo_data['total_commits'] > 0 else 0
            result_text += f"{i:2d}. {author:<35} {commits:>4} commits ({percentage:5.1f}%)\n"
        
        if len(sorted_contributors) > 10:
            remaining = len(sorted_contributors) - 10
            result_text += f"    ... and {remaining} more contributors\n"
        
        result_text += f"\n{'='*60}\n\n"
        
        self.results_text.insert(tk.END, result_text)
        self.results_text.see(tk.END)  # Scroll to bottom
    
    def display_summary(self, successful_repos, failed_repos):
        """Display analysis summary"""
        summary_text = f"📋 ANALYSIS SUMMARY\n"
        summary_text += f"{'='*60}\n"
        summary_text += f"✅ Successfully Analyzed: {len(successful_repos)} repositories\n"
        summary_text += f"❌ Failed to Analyze: {len(failed_repos)} repositories\n"
        
        if successful_repos:
            total_commits = sum(repo['total_commits'] for repo in successful_repos)
            total_contributors = sum(repo['contributor_count'] for repo in successful_repos)
            summary_text += f"📝 Total Commits Analyzed: {total_commits:,}\n"
            summary_text += f"👥 Total Contributors Found: {total_contributors:,}\n"
        
        if failed_repos:
            summary_text += f"\n❌ FAILED REPOSITORIES:\n"
            for repo in failed_repos:
                summary_text += f"   • {repo}\n"
        
        summary_text += f"\n🎉 Analysis Complete!\n"
        
        self.results_text.insert(tk.END, summary_text)
        self.results_text.see(tk.END)
    
    def save_results(self):
        """Save results to JSON file"""
        if not hasattr(self, 'analysis_results'):
            messagebox.showwarning("No Data", "No analysis results to save!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tr_top_contributors_{timestamp}.json"
        
        try:
            # Prepare export data
            export_data = {
                'analysis_date': self.analysis_results['analysis_date'],
                'summary': {
                    'total_repositories_processed': len(self.analysis_results['successful_repos']) + len(self.analysis_results['failed_repos']),
                    'successful_repositories': len(self.analysis_results['successful_repos']),
                    'failed_repositories': len(self.analysis_results['failed_repos']),
                    'total_commits': sum(repo['total_commits'] for repo in self.analysis_results['successful_repos']),
                    'total_contributors': sum(repo['contributor_count'] for repo in self.analysis_results['successful_repos'])
                },
                'repositories': self.analysis_results['successful_repos'],
                'failed_repositories': self.analysis_results['failed_repos']
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Success!", f"Results saved to:\n{filename}")
            self.status_var.set(f"Results saved to {filename}")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save results:\n{str(e)}")
    
    def analysis_finished(self):
        """Reset UI after analysis completion"""
        self.analyzing = False
        self.analyze_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        if hasattr(self, 'analysis_results') and self.analysis_results['successful_repos']:
            self.save_btn.config(state='normal')
        
        if self.stop_requested:
            self.status_var.set("Analysis stopped by user")
        else:
            self.status_var.set("Analysis completed successfully!")

def main():
    root = tk.Tk()
    app = TopContributorsAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
