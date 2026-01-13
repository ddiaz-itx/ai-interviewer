# Python Version Issue - Quick Fix Guide

## Problem
The project requires Python 3.11+, but your system has Python 3.8.10.

## Solution

### Option 1: Automated Installation (Recommended)

Run the Python installation script:

```bash
chmod +x install-python311.sh
./install-python311.sh
```

Then run the setup again:

```bash
./setup-backend.sh
```

### Option 2: Manual Installation

Install Python 3.11 manually:

```bash
# Update package list
sudo apt update

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Verify installation
python3.11 --version
```

Then configure Poetry to use Python 3.11:

```bash
cd backend
poetry env use python3.11
poetry install
```

### Option 3: Using pyenv (Alternative)

If you prefer managing multiple Python versions with pyenv:

```bash
# Install pyenv (if not installed)
curl https://pyenv.run | bash

# Add to ~/.bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Reload shell
source ~/.bashrc

# Install Python 3.11
pyenv install 3.11.7

# Set as local version for this project
cd ~/trainings/ai-interviewer
pyenv local 3.11.7

# Verify
python --version  # Should show 3.11.7

# Now run setup
./setup-backend.sh
```

## Verification

After installation, verify Python 3.11 is available:

```bash
python3.11 --version
```

You should see: `Python 3.11.x`

## Continue Setup

Once Python 3.11 is installed, the setup script will automatically:
1. Detect Python 3.11
2. Configure Poetry to use it
3. Install all dependencies
4. Set up the database

Just run:

```bash
./setup-backend.sh
```
