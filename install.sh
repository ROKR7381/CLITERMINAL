#!/bin/bash
# install.sh (Linux/macOS)

echo ""
echo "🚀 Installing myagent CLI..."
echo "------------------------------"

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.9+ first:"
    echo "   https://www.python.org/downloads/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo "❌ Python 3.9+ required. Current version: Python $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# 2. Check pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found. Installing..."
    python3 -m ensurepip --upgrade
fi

# 3. Install myagent
echo "📦 Installing myagent from GitHub..."
pip3 install --upgrade git+https://github.com/ROKR7381/CLITERMINAL.git

if [ $? -ne 0 ]; then
    echo "❌ Installation failed!"
    exit 1
fi

echo ""
echo "✅ myagent installed successfully!"
echo ""
echo "👉 Run:"
echo "   myagent"
echo "   myagent tui"
echo "   myagent run 'hello'"
echo ""