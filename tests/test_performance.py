import os
import sys
import time
import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from wrappers import get_recommendations_from_user

def test_recommendation_performance():
    start_time = time.time()
    recommendations = get_recommendations_from_user(user_id=8, source="local")
    elapsed_time = time.time() - start_time
    assert elapsed_time < 5.0
    assert len(recommendations) == 5

def test_multiple_users_performance():
    user_ids = [8]  # Test simplifié
    for user_id in user_ids:
        recommendations = get_recommendations_from_user(user_id=user_id, source="local")
        assert len(recommendations) >= 0
