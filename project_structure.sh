#!/bin/bash

# Root folder
mkdir -p ecommerce_phase_4/exskilence_project
cd ecommerce_phase_4/exskilence_project

# Core backend layers
mkdir -p routes services repositories models validators exceptions middleware config utils

# Templates
mkdir -p templates/auth templates/admin templates/staff templates/customer templates/partials

# Static files
mkdir -p static/css static/js

# Create main app file
touch app.py

# Go back to root for testing config
cd ..

# Testing structure
mkdir -p testing_config/py_tests
mkdir -p testing_config/ui_tests

# Create test files
touch testing_config/py_tests/task.py
touch testing_config/ui_tests/task.json

# Add __init__.py to Python packages
cd exskilence_project
touch routes/__init__.py
touch services/__init__.py
touch repositories/__init__.py
touch models/__init__.py
touch validators/__init__.py
touch exceptions/__init__.py
touch middleware/__init__.py
touch config/__init__.py
touch utils/__init__.py

echo "✅ Phase 4 folder structure created successfully!"
