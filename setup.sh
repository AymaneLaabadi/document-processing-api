#!/bin/bash

set -e
set -x

echo "🚀 Backend Setup Started..."

# Verify if Python Virtual Environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ Virtual Environment is not activated! Please activate it first."
    exit 1
fi

# Show Python environment path
echo "🐍 Using Python environment from: $VIRTUAL_ENV"

# Upgrade pip
echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install SpaCy model
echo "🔄 Installing SpaCy model..."
python -m spacy download en_core_web_sm

# Ensure necessary directories exist
echo "📁 Creating necessary directories..."
mkdir -p data/input data/output data/config logs

echo "✅ Setup Completed Successfully!"
