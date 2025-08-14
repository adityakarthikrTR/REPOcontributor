# Troubleshooting Guide

## GitHub Copilot Extension Issues

### Error: "Copilot took too long to get ready. Please ensure you are signed in to GitHub and that the extension GitHub.copilot-chat is installed and enabled."

**This error is NOT related to this repository's code.** This is a VS Code development environment issue with the GitHub Copilot extension.

#### What this error means:
- The GitHub Copilot extension in VS Code is having initialization problems
- You may not be signed in to GitHub in VS Code
- The Copilot extensions may not be properly installed or enabled

#### How to fix it:

1. **Check your GitHub sign-in status in VS Code:**
   - Open VS Code
   - Look at the bottom-left corner for the account icon
   - Click it and ensure you're signed in to GitHub
   - If not signed in, click "Sign in to sync settings" and follow the prompts

2. **Install/Enable GitHub Copilot extensions:**
   - Open VS Code Extensions (Ctrl+Shift+X or Cmd+Shift+X)
   - Search for "GitHub Copilot"
   - Install these extensions:
     - `GitHub Copilot` (by GitHub)
     - `GitHub Copilot Chat` (by GitHub)
   - Ensure both extensions are enabled

3. **Restart VS Code:**
   - Close VS Code completely
   - Reopen it and wait for Copilot to initialize

4. **Check your GitHub Copilot subscription:**
   - Ensure you have an active GitHub Copilot subscription
   - Go to https://github.com/settings/copilot to verify

#### Alternative solutions:
- Try signing out and signing back in to GitHub in VS Code
- Disable and re-enable the Copilot extensions
- Clear VS Code workspace settings and reload
- Update VS Code to the latest version

---

## Repository-Specific Issues

### GUI Tools Not Working (tkinter issues)

If you encounter errors running the GUI tools (`tr_bulk_analyzer.py`, `top_contributors_gui.py`):

**Error symptoms:**
- `ModuleNotFoundError: No module named 'tkinter'`
- GUI windows don't open

**Solutions:**

#### On Ubuntu/Debian:
```bash
sudo apt-get install python3-tk
```

#### On CentOS/RHEL/Fedora:
```bash
sudo yum install tkinter
# or on newer versions:
sudo dnf install python3-tkinter
```

#### On macOS:
```bash
# If using Homebrew:
brew install python-tk
```

#### On Windows:
- tkinter is usually included with Python
- If missing, reinstall Python from python.org with "tcl/tk and IDLE" option checked

### Command-Line Tools

All command-line tools should work without additional dependencies:
- `repo_contributor_analyzer.py` ✅
- Any future CLI tools ✅

### Network/Git Issues

If repository cloning fails:
1. Check your internet connection
2. Ensure Git is installed: `git --version`
3. For private repositories, ensure you have proper authentication
4. Check if the repository URL is correct

---

## Getting Help

If you encounter issues specific to this repository's functionality:
1. Check this troubleshooting guide first
2. Look at the examples in README.md
3. Run tools with `--help` flag for usage information
4. Create an issue on GitHub with:
   - Your operating system
   - Python version (`python3 --version`)
   - Full error message
   - Steps to reproduce the issue