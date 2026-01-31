#!/usr/bin/env bash

set -euo pipefail

# Configuration Variables
PROJECT_DIR="app"
BLACK_OPTS="--check --diff --color"
MYPY_OPTS="--strict"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Helper functions
print_header() {
    echo -e "\n${YELLOW}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}[✓] $1${NC}"
}

print_error() {
    echo -e "${RED}[!] $1${NC}"
}

# Check if black is installed
if ! command -v black &> /dev/null; then
    print_error "black is not installed. Install with: pip install black"
    exit 1
fi

# Check if mypy is installed
if ! command -v mypy &> /dev/null; then
    print_error "mypy is not installed. Install with: pip install mypy"
    exit 1
fi

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Directory '$PROJECT_DIR' not found"
    exit 1
fi

# Run linters
print_header "Running Black"
if black $BLACK_OPTS "$PROJECT_DIR"; then
    print_success "Black formatting check passed"
else
    print_error "Black formatting check failed"
    echo "Run 'black $PROJECT_DIR' to auto-format"
    exit 1
fi

print_header "Running MyPy"
if mypy $MYPY_OPTS "$PROJECT_DIR"; then
    print_success "MyPy type checking passed"
else
    print_error "MyPy type checking failed"
    exit 1
fi

print_header "Linting Complete"
print_success "All checks passed!"
