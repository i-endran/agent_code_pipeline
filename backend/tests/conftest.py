"""
Tests Configuration

Pytest fixtures and configuration for testing.
"""

import pytest
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set test environment
os.environ['APP_ENV'] = 'dev'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
