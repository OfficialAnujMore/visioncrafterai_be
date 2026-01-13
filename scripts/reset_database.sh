#!/bin/bash

# VisionCrafterAI Database Reset Script (Local only)

echo "🔄 VisionCrafterAI Database Reset Script"
echo "=========================================="
echo ""

echo "💻 Running in local environment"

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not activated"
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

python scripts/clear_database.py --all --yes

echo ""
echo "✅ Database reset complete!"