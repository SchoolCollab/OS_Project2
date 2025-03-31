# Alias python to python3 if on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    alias python=python3
fi

# Compile the Python files using -O flag to ignore asserts
python -O source/main.py

# Remove the alias for python3
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    unalias python=python3
fi

# Recursively remove all __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} +