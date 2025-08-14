#!/usr/bin/env python3
"""
TR Repository Top Contributors Analyzer - Streamlit Version
Simple web app to find top contributors for each repository
"""

import streamlit as st
import subprocess
import tempfile
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
import re

def is_bot_or_automated(author_name):
    """
    Determine if a contributor is likely a bot or automated system
    """
    author_lower = author_name.lower()
    
    # Common bot indicators
    bot_patterns = [
        r'.*\[bot\].*',  # [bot] in name
        r'.*bot.*',      # contains 'bot'
        r'dependabot',   # dependabot
        r'github-actions',  # GitHub Actions
        r'workflow.*automation',  # workflow automation
        r'dynamic.*readme',  # Dynamic Readme
        r'auto.*',       # auto-something
        r'ci.*',         # CI systems
        r'deploy.*',     # deployment systems
        r'.*automation.*', # automation in name
        r'renovate',     # Renovate bot
        r'greenkeeper',  # Greenkeeper
        r'codecov',      # Codecov
        r'snyk',         # Snyk bot
        r'whitesource',  # WhiteSource
        r'.*deploy.*',   # deployment bots
    ]
    
    # Check if author matches any bot pattern
    for pattern in bot_patterns:
        if re.match(pattern, author_lower):
            return True
    
    # Check for numeric-only usernames (often system accounts)
    if re.match(r'^\d+$', author_name.strip()):
        return True
    
    return False

def get_top_human_contributor(all_contributors):
    """
    Find the top human contributor by filtering out bots and automated systems
    """
    human_contributors = {}
    
    for author, commits in all_contributors.items():
        if not is_bot_or_automated(author):
            human_contributors[author] = commits
    
    if human_contributors:
        return max(human_contributors.items(), key=lambda x: x[1])
    return None

# Page configuration
st.set_page_config(
    page_title="TR Repository Top Contributors Analyzer",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 2rem;
    }
    .repo-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .success-metric {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
    }
    .error-metric {
        background: linear-gradient(90deg, #ff416c 0%, #ff4b2b 100%);
    }
</style>
""", unsafe_allow_html=True)

def analyze_single_repo(repo_name, progress_callback=None, since: str | None = None):
    """Analyze a single repository and return top contributors"""
    try:
        url = f"https://github.com/tr/{repo_name}"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            clone_path = os.path.join(temp_dir, repo_name)
            
            if progress_callback:
                progress_callback(f"Cloning {repo_name}...")
            
            # Clone repository
            clone_cmd = ['git', 'clone', '--quiet', url, clone_path]
            clone_result = subprocess.run(clone_cmd, capture_output=True, 
                                        text=True, timeout=45)
            
            if clone_result.returncode != 0:
                return None
            
            if progress_callback:
                progress_callback(f"Analyzing contributors for {repo_name}...")
            
            # Get contributors (optionally time-bounded)
            git_cmd = ['git', '-C', clone_path, 'shortlog', '-sn', '--all']
            if since:
                # Pass a human-readable range like "2 months ago" safely
                git_cmd.extend(['--since', since])
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
            
    except Exception as e:
        return None

def create_contributor_chart(repo_data, top_n=10):
    """Create a bar chart for top contributors"""
    if not repo_data or not repo_data['contributors']:
        return None
    
    # Sort contributors and get top N
    sorted_contributors = sorted(repo_data['contributors'].items(), 
                               key=lambda x: x[1], reverse=True)[:top_n]
    
    if not sorted_contributors:
        return None
    
    # Create DataFrame
    df = pd.DataFrame(sorted_contributors, columns=['Author', 'Commits'])
    df['Percentage'] = (df['Commits'] / repo_data['total_commits'] * 100).round(1)
    
    # Create horizontal bar chart
    fig = px.bar(df, 
                 x='Commits', 
                 y='Author', 
                 orientation='h',
                 color='Commits',
                 color_continuous_scale='viridis',
                 title=f"Top {len(df)} Contributors - {repo_data['name']}",
                 labels={'Commits': 'Number of Commits', 'Author': 'Contributors'},
                 text='Commits')
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=max(400, len(df) * 40),
        showlegend=False
    )
    
    fig.update_traces(texttemplate='%{text} (%{customdata}%)', 
                     textposition="outside",
                     customdata=df['Percentage'])
    
    return fig

def display_repo_results(repo_data):
    """Display results for a single repository in Streamlit"""
    if not repo_data:
        return
    
    st.markdown(f"""
    <div class="repo-card">
        <h3>📁 {repo_data['name'].upper()}</h3>
        <p><strong>🌐 Repository:</strong> <a href="{repo_data['url']}" target="_blank">{repo_data['url']}</a></p>
        <p><strong>📊 Statistics:</strong> {repo_data['total_commits']:,} total commits | {repo_data['contributor_count']} contributors</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create metrics columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Commits", f"{repo_data['total_commits']:,}")
    
    with col2:
        st.metric("Contributors", repo_data['contributor_count'])
    
    with col3:
        if repo_data['contributors']:
            top_contributor = max(repo_data['contributors'].items(), key=lambda x: x[1])
            st.metric("Top Contributor", top_contributor[0], f"{top_contributor[1]} commits")
    
    # Display chart
    chart = create_contributor_chart(repo_data)
    if chart:
        st.plotly_chart(chart, use_container_width=True)
    
    # Display top contributors table
    if repo_data['contributors']:
        sorted_contributors = sorted(repo_data['contributors'].items(), 
                                   key=lambda x: x[1], reverse=True)[:10]
        
        df = pd.DataFrame(sorted_contributors, columns=['Author', 'Commits'])
        df['Percentage'] = (df['Commits'] / repo_data['total_commits'] * 100).round(1)
        df['Rank'] = range(1, len(df) + 1)
        df = df[['Rank', 'Author', 'Commits', 'Percentage']]
        
        st.subheader("🏆 Top Contributors")
        st.dataframe(df, use_container_width=True, hide_index=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🏆 TR Repository Top Contributors Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Find top contributors for each TR repository</p>', unsafe_allow_html=True)
    
    # Sidebar for input
    st.sidebar.header("📝 Repository Configuration")
    
    # Repository input
    repo_input = st.sidebar.text_area(
        "Enter TR repository names (one per line):",
        placeholder="tr-api\ntr-dashboard\ntr-leaderboard",
        height=150,
        help="Enter repository names without the 'tr/' prefix. Auto-prefix will be applied."
    )
    
    # Example repositories button
    if st.sidebar.button("📝 Load Example Repositories"):
        example_repos = """ras_shared-python-utils
ras_ai_trajectory
ras-search_enhanced-document-retrieval"""
        st.session_state['repo_input'] = example_repos
        st.rerun()
    
    # Clear button
    if st.sidebar.button("🗑️ Clear All"):
        if 'repo_input' in st.session_state:
            del st.session_state['repo_input']
        if 'analysis_results' in st.session_state:
            del st.session_state['analysis_results']
        st.rerun()
    
    # Analysis settings
    st.sidebar.header("⚙️ Analysis Settings")
    max_contributors = st.sidebar.slider("Max contributors to show", 5, 20, 10)
    show_charts = st.sidebar.checkbox("Show charts", value=True)

    # Time range selection
    st.sidebar.header("🕒 Time Range")
    time_range_option = st.sidebar.radio(
        "Select commit time range",
        ["All time", "Last 2 months", "Last 6 months"],
        index=0
    )
    since_value = None
    if time_range_option == "Last 2 months":
        since_value = "2 months ago"
    elif time_range_option == "Last 6 months":
        since_value = "6 months ago"
    
    # Process repository input
    repo_names = []
    if repo_input:
        for line in repo_input.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Clean repo name
                repo = line.replace('https://github.com/tr/', '').replace('https://github.com/', '')
                repo = repo.strip('/')
                if repo:
                    repo_names.append(repo)
    
    # Analysis button
    if st.sidebar.button("🚀 Analyze Repositories", type="primary", disabled=not repo_names):
        if repo_names:
            # Initialize session state for results
            if 'analysis_results' not in st.session_state:
                st.session_state['analysis_results'] = {}
            
            # Create progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Stats containers
            col1, col2, col3 = st.columns(3)
            with col1:
                total_repos_metric = st.empty()
            with col2:
                analyzed_metric = st.empty()
            with col3:
                failed_metric = st.empty()
            
            successful_repos = []
            failed_repos = []
            
            # Analyze each repository
            for i, repo_name in enumerate(repo_names):
                status_text.text(f"Analyzing {repo_name}...")
                progress_bar.progress((i + 1) / len(repo_names))
                
                # Update metrics
                total_repos_metric.metric("📊 Total Repos", len(repo_names))
                analyzed_metric.metric("✅ Analyzed", len(successful_repos))
                failed_metric.metric("❌ Failed", len(failed_repos))
                
                # Analyze repository
                result = analyze_single_repo(repo_name, since=since_value)
                
                if result:
                    successful_repos.append(result)
                    st.session_state['analysis_results'][repo_name] = result
                else:
                    failed_repos.append(repo_name)
                
                # Update metrics after analysis
                analyzed_metric.metric("✅ Analyzed", len(successful_repos))
                failed_metric.metric("❌ Failed", len(failed_repos))
            
            # Final status
            status_text.text(f"✅ Analysis complete! {len(successful_repos)} successful, {len(failed_repos)} failed")
            progress_bar.progress(1.0)
            
            # Store results in session state
            st.session_state['successful_repos'] = successful_repos
            st.session_state['failed_repos'] = failed_repos
            st.session_state['analysis_date'] = datetime.now().isoformat()
            st.session_state['analysis_range'] = time_range_option
    
    # Display results if available
    if 'successful_repos' in st.session_state and st.session_state['successful_repos']:
        st.header("📊 Analysis Results")
        # Show selected time range
        selected_range = st.session_state.get('analysis_range', 'All time')
        st.caption(f"Time range: {selected_range}")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_commits = sum(repo['total_commits'] for repo in st.session_state['successful_repos'])
        total_contributors = len(set(
            author for repo in st.session_state['successful_repos'] 
            for author in repo['contributors'].keys()
        ))
        
        with col1:
            st.metric("🏆 Repositories Analyzed", len(st.session_state['successful_repos']))
        with col2:
            st.metric("📊 Total Commits", f"{total_commits:,}")
        with col3:
            st.metric("👥 Unique Contributors", total_contributors)
        with col4:
            st.metric("📅 Analysis Date", st.session_state.get('analysis_date', 'Unknown')[:10])
        
        # Display each repository
        for repo_data in st.session_state['successful_repos']:
            display_repo_results(repo_data)
            st.markdown("---")
        
        # Overall Top Contributors Summary
        st.header("🏆 Overall Top Contributors Across All Repositories")
        
        # Aggregate all contributors across repositories
        all_contributors = {}
        for repo_data in st.session_state['successful_repos']:
            for author, commits in repo_data['contributors'].items():
                if author in all_contributors:
                    all_contributors[author] += commits
                else:
                    all_contributors[author] = commits
        
        if all_contributors:
            # Sort contributors by total commits
            sorted_all_contributors = sorted(all_contributors.items(), 
                                           key=lambda x: x[1], reverse=True)
            
            # Create overall top contributors chart
            top_overall = sorted_all_contributors[:10]
            df_overall = pd.DataFrame(top_overall, columns=['Author', 'Total Commits'])
            df_overall['Percentage'] = (df_overall['Total Commits'] / total_commits * 100).round(1)
            
            # Display overall top contributor
            top_contributor = sorted_all_contributors[0]
            st.success(f"🥇 **Overall Top Contributor:** {top_contributor[0]} with {top_contributor[1]:,} commits ({(top_contributor[1]/total_commits*100):.1f}% of all commits)")
            
            # Find and display top human developer
            top_human = get_top_human_contributor(all_contributors)
            if top_human:
                human_percentage = (top_human[1] / total_commits * 100) if total_commits > 0 else 0
                st.info(f"👨‍💻 **Top Human Developer:** {top_human[0]} with {top_human[1]:,} commits ({human_percentage:.1f}% of all commits)")
                
                # Show the distinction if top contributor is not human
                if is_bot_or_automated(top_contributor[0]):
                    bot_vs_human_diff = top_contributor[1] - top_human[1]
                    st.caption(f"ℹ️ *Note: Top contributor appears to be automated. Top human has {bot_vs_human_diff:,} fewer commits than the top automated contributor.*")
            else:
                st.warning("⚠️ No human contributors identified (all appear to be bots or automated systems)")
            
            # Create overall contributors chart
            fig_overall = px.bar(df_overall, 
                               x='Total Commits', 
                               y='Author', 
                               orientation='h',
                               color='Total Commits',
                               color_continuous_scale='plasma',
                               title="🏆 Top 10 Contributors Across All Repositories",
                               labels={'Total Commits': 'Total Commits', 'Author': 'Contributors'},
                               text='Total Commits')
            
            fig_overall.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                height=max(400, len(df_overall) * 40),
                showlegend=False
            )
            
            fig_overall.update_traces(texttemplate='%{text} (%{customdata}%)', 
                                    textposition="outside",
                                    customdata=df_overall['Percentage'])
            
            st.plotly_chart(fig_overall, use_container_width=True)
            
            # Display overall top contributors table
            df_overall['Rank'] = range(1, len(df_overall) + 1)
            df_overall = df_overall[['Rank', 'Author', 'Total Commits', 'Percentage']]
            
            st.subheader("📋 Overall Top Contributors Table")
            st.dataframe(df_overall, use_container_width=True, hide_index=True)
            
            # Create and display human contributors section
            st.subheader("👨‍💻 Top Human Developers")
            
            # Filter human contributors
            human_contributors = {}
            for author, commits in all_contributors.items():
                if not is_bot_or_automated(author):
                    human_contributors[author] = commits
            
            if human_contributors:
                # Sort human contributors
                sorted_human_contributors = sorted(human_contributors.items(), 
                                                 key=lambda x: x[1], reverse=True)[:10]
                
                # Create human contributors chart
                df_human = pd.DataFrame(sorted_human_contributors, columns=['Author', 'Total Commits'])
                df_human['Percentage'] = (df_human['Total Commits'] / total_commits * 100).round(1)
                df_human['Rank'] = range(1, len(df_human) + 1)
                
                # Human contributors chart
                fig_human = px.bar(df_human, 
                                 x='Total Commits', 
                                 y='Author', 
                                 orientation='h',
                                 color='Total Commits',
                                 color_continuous_scale='viridis',
                                 title="👨‍💻 Top 10 Human Developers",
                                 labels={'Total Commits': 'Total Commits', 'Author': 'Human Developers'},
                                 text='Total Commits')
                
                fig_human.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    height=max(400, len(df_human) * 40),
                    showlegend=False
                )
                
                fig_human.update_traces(texttemplate='%{text} (%{customdata}%)', 
                                      textposition="outside",
                                      customdata=df_human['Percentage'])
                
                st.plotly_chart(fig_human, use_container_width=True)
                
                # Human contributors table
                df_human_display = df_human[['Rank', 'Author', 'Total Commits', 'Percentage']]
                st.dataframe(df_human_display, use_container_width=True, hide_index=True)
                
                # Show stats comparison
                total_human_commits = sum(human_contributors.values())
                human_commit_percentage = (total_human_commits / total_commits * 100) if total_commits > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("👥 Human Contributors", len(human_contributors))
                with col2:
                    st.metric("💻 Human Commits", f"{total_human_commits:,}")
                with col3:
                    st.metric("📊 Human vs Total", f"{human_commit_percentage:.1f}%")
                
            else:
                st.warning("⚠️ No human contributors identified in the analysis.")
            
            # Show repository distribution for top contributor
            if len(st.session_state['successful_repos']) > 1:
                st.subheader(f"📊 {top_contributor[0]}'s Contribution Distribution")
                
                top_author_repos = []
                for repo_data in st.session_state['successful_repos']:
                    if top_contributor[0] in repo_data['contributors']:
                        commits = repo_data['contributors'][top_contributor[0]]
                        top_author_repos.append({
                            'Repository': repo_data['name'],
                            'Commits': commits,
                            'Percentage': round(commits / top_contributor[1] * 100, 1)
                        })
                
                if top_author_repos:
                    df_author_dist = pd.DataFrame(top_author_repos)
                    
                    # Pie chart for top contributor's distribution
                    fig_pie = px.pie(df_author_dist, 
                                   values='Commits', 
                                   names='Repository',
                                   title=f"{top_contributor[0]}'s Commits by Repository")
                    st.plotly_chart(fig_pie, use_container_width=True)
        
        # Download results
        if st.button("💾 Download Results as JSON"):
            # Calculate overall top contributors for JSON export
            all_contributors_for_export = {}
            for repo_data in st.session_state['successful_repos']:
                for author, commits in repo_data['contributors'].items():
                    if author in all_contributors_for_export:
                        all_contributors_for_export[author] += commits
                    else:
                        all_contributors_for_export[author] = commits
            
            # Sort for export
            sorted_contributors_export = sorted(all_contributors_for_export.items(), 
                                              key=lambda x: x[1], reverse=True)
            
            overall_top_contributor = sorted_contributors_export[0] if sorted_contributors_export else None
            
            # Find top human contributor for export
            top_human_export = get_top_human_contributor(all_contributors_for_export)
            
            results_data = {
                'analysis_date': st.session_state.get('analysis_date'),
                'successful_repos': st.session_state['successful_repos'],
                'failed_repos': st.session_state.get('failed_repos', []),
                'summary': {
                    'total_repositories_analyzed': len(st.session_state['successful_repos']),
                    'total_commits': total_commits,
                    'unique_contributors': total_contributors,
                    'overall_top_contributor': {
                        'name': overall_top_contributor[0] if overall_top_contributor else None,
                        'total_commits': overall_top_contributor[1] if overall_top_contributor else 0,
                        'percentage': round(overall_top_contributor[1] / total_commits * 100, 1) if overall_top_contributor and total_commits > 0 else 0,
                        'is_automated': is_bot_or_automated(overall_top_contributor[0]) if overall_top_contributor else False
                    },
                    'top_human_developer': {
                        'name': top_human_export[0] if top_human_export else None,
                        'total_commits': top_human_export[1] if top_human_export else 0,
                        'percentage': round(top_human_export[1] / total_commits * 100, 1) if top_human_export and total_commits > 0 else 0
                    }
                },
                'overall_top_contributors': dict(sorted_contributors_export[:20]),  # Top 20 overall
                'top_human_contributors': dict(sorted([(k, v) for k, v in all_contributors_for_export.items() if not is_bot_or_automated(k)], key=lambda x: x[1], reverse=True)[:10])  # Top 10 humans
            }
            
            json_str = json.dumps(results_data, indent=2, default=str)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"tr_contributor_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        # Show failed repositories if any
        if 'failed_repos' in st.session_state and st.session_state['failed_repos']:
            st.warning(f"⚠️ Failed to analyze {len(st.session_state['failed_repos'])} repositories: {', '.join(st.session_state['failed_repos'])}")
    
    # Instructions
    if not repo_names:
        st.info("""
        ### 🚀 How to use:
        1. **Enter repository names** in the sidebar (one per line)
        2. **Click "Load Example"** to see sample repositories
        3. **Click "Analyze Repositories"** to start the analysis
        4. **View results** with charts and tables below
        5. **Download results** as JSON for further analysis
        
        ### 💡 Tips:
        - Repository names are auto-prefixed with `https://github.com/tr/`
        - Analysis may take a few minutes for multiple repositories
        - Results include top contributors with commit counts and percentages
        """)

if __name__ == "__main__":
    main()
