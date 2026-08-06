#!/bin/bash
# Script to run Alembic migrations
# Usage: ./run_migrations.sh

set -e

echo "🔧 Running Alembic migrations..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to backend directory
cd "$SCRIPT_DIR"

# Set PYTHONPATH to backend directory
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Check if we're in Docker or local
if [ -f "/.dockerenv" ]; then
    echo "📦 Running in Docker container"
    alembic upgrade head
else
    echo "💻 Running locally"
    
    # Check if virtual environment exists and activate it
    if [ -d "venv" ]; then
        echo "✓ Activating virtual environment..."
        source venv/bin/activate
    fi
    
    # Run migrations with PYTHONPATH set
    alembic upgrade head
fi

echo ""
echo "✅ Migrations completed successfully!"
