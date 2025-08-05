# GitHub Repository Contributor Analyzer

A collection of Python tools to analyze GitHub repositories and find top contributors across multiple repositories.

## 🚀 Tools Included

### 1. `repo_contributor_analyzer.py`
**Comprehensive repository analyzer for local Git repositories**
- Scans directories for Git repositories
- Analyzes contributor statistics
- Supports JSON output
- Command-line interface

```bash
python repo_contributor_analyzer.py [path] --output results.json
```

### 2. `quick_contributors.py`
**Quick single repository analyzer**
- Takes a GitHub URL and shows top 5 contributors
- Fast and simple

```bash
python quick_contributors.py https://github.com/owner/repo
```

### 3. `multi_repo_analyzer.py`
**Interactive multi-repository analyzer**
- Interactive prompts for multiple URLs
- Detailed repository breakdown
- Progress tracking

```bash
python multi_repo_analyzer.py
```

### 4. `batch_analyzer.py`
**Command-line batch processor**
- Batch process multiple repositories
- Supports short format (owner/repo)
- Quick results

```bash
python batch_analyzer.py repo1 repo2 repo3
python batch_analyzer.py https://github.com/owner/repo1 owner/repo2
```

### 5. `github_analyzer_gui.py`
**Full-featured GUI application**
- User-friendly graphical interface
- Multi-line URL input
- Real-time progress tracking
- Detailed results display

```bash
python github_analyzer_gui.py
```

### 6. `tr_bulk_analyzer.py`
**Specialized TR repository analyzer**
- Purpose-built for TR organization repositories
- Auto-prefixes `https://github.com/tr/`
- Bulk paste repository names
- Clean, focused interface

```bash
python tr_bulk_analyzer.py
```

## 📋 Features

- ✅ **Multiple Input Methods**: Command line, interactive, GUI, bulk paste
- ✅ **Auto-prefixing**: Automatic URL completion for TR repositories
- ✅ **Bulk Processing**: Handle multiple repositories at once
- ✅ **Progress Tracking**: Real-time analysis progress
- ✅ **Error Handling**: Graceful handling of failed repositories
- ✅ **Export Options**: JSON output support
- ✅ **Cross-platform**: Works on Windows, macOS, and Linux

## 🔧 Requirements

- Python 3.7+
- Git installed and accessible from command line
- Internet connection for cloning repositories
- tkinter (usually included with Python) for GUI tools

## 📊 Output

All tools provide:
- **Top Contributors**: Ranked list of contributors by commit count
- **Repository Statistics**: Total commits, contributors, etc.
- **Summary Information**: Aggregated statistics across all analyzed repositories

## 🎯 Use Cases

1. **Project Management**: Identify key contributors across multiple projects
2. **Team Analysis**: Understand contribution patterns
3. **Repository Auditing**: Quick overview of repository activity
4. **Bulk Analysis**: Analyze entire organization repositories at once

## 🚀 Quick Start

1. **For single repository analysis:**
   ```bash
   python quick_contributors.py https://github.com/user/repo
   ```

2. **For multiple repositories with GUI:**
   ```bash
   python github_analyzer_gui.py
   ```

3. **For TR repositories specifically:**
   ```bash
   python tr_bulk_analyzer.py
   # Then paste repository names like: ras_shared-python-utils
   ```

## 📝 Examples

### Command Line Batch Analysis
```bash
python batch_analyzer.py microsoft/vscode facebook/react google/tensorflow
```

### TR Repository Analysis
```bash
python tr_bulk_analyzer.py
# In the GUI, paste:
# ras_shared-python-utils
# ras_ai_trajectory
# ras-search_enhanced-document-retrieval
```

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📄 License

This project is open source and available under the MIT License.
