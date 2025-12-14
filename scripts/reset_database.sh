#!/bin/bash

# Database Reset Script for Development
# This script completely resets the database by clearing all tables

echo "🔄 VisionCrafterAI Database Reset Script"
echo "=========================================="
echo ""

# Check if running in Docker
if [ -f /.dockerenv ]; then
    # Running inside Docker container
    echo "📦 Detected Docker environment"
    python scripts/clear_database.py --all --yes
else
    # Running locally
    echo "💻 Running in local environment"
    
    # Check if virtual environment is activated
    if [[ -z "$VIRTUAL_ENV" ]]; then
        echo "⚠️  Virtual environment not activated"
        echo "Activating virtual environment..."
        source .venv/bin/activate
    fi
    
    python scripts/clear_database.py --all --yes
fi

echo ""
echo "✅ Database reset complete!"
