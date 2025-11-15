import pytest
from unittest.mock import MagicMock
from bson import ObjectId

# This is needed to make sure the app modules can be imported
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Martin_LLM'))

from app.services.login_service import UserService

@pytest.fixture
def mock_mongo_client(mocker):
    """Fixture to mock the MongoClient and its collections."""
    # Mock the collections
    mock_users_collection = MagicMock()
    mock_conversations_collection = MagicMock()
    
    # Mock the database object
    mock_db = MagicMock()
    mock_db.__getitem__.side_effect = lambda name: {
        "users": mock_users_collection,
        "conversations": mock_conversations_collection
    }.get(name)
    mock_db.list_collection_names.return_value = ["users", "conversations"]

    # Mock the client
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    
    # Patch 'MongoClient' in the login_service module
    mocker.patch('app.services.login_service.MongoClient', return_value=mock_client)
    
    return mock_users_collection, mock_conversations_collection

@pytest.fixture
def user_service(mock_mongo_client):
    """Fixture to get a UserService instance with a mocked DB."""
    # Since MongoClient is patched, this will use the mock.
    service = UserService()
    # Manually assign the mocked collections for direct access in tests
    service.users, service.conversations = mock_mongo_client
    return service

def test_register_user_success(user_service):
    """Test successful user registration."""
    user_service.users.find_one.return_value = None # No existing user
    user_service.users.insert_one.return_value = MagicMock(inserted_id=ObjectId())

    user_id = user_service.register_user("testuser", "password123", "test@test.com")
    
    assert user_id is not None
    user_service.users.find_one.assert_called_once_with({"username": "testuser"})
    user_service.users.insert_one.assert_called_once()
    # Check that the inserted data has the correct structure
    inserted_call = user_service.users.insert_one.call_args[0][0]
    assert inserted_call['username'] == 'testuser'
    assert 'password' in inserted_call
    assert inserted_call['email'] == 'test@test.com'

def test_register_user_failure_already_exists(user_service):
    """Test registration failure when the user already exists."""
    user_service.users.find_one.return_value = {"username": "testuser"} # User exists

    user_id = user_service.register_user("testuser", "password123", "test@test.com")

    assert user_id is None
    user_service.users.find_one.assert_called_once_with({"username": "testuser"})
    user_service.users.insert_one.assert_not_called()

def test_authenticate_user_success(user_service):
    """Test successful user authentication."""
    hashed_password = user_service._hash_password("password123")
    user_doc = {
        "_id": ObjectId(),
        "username": "testuser",
        "password": hashed_password
    }
    user_service.users.find_one.return_value = user_doc

    result = user_service.authenticate_user("testuser", "password123")

    assert result is not None
    assert result[0] == str(user_doc["_id"])
    assert result[1] == "testuser"
    user_service.users.find_one.assert_called_once_with({"username": "testuser"})

def test_authenticate_user_failure_wrong_password(user_service):
    """Test authentication failure with an incorrect password."""
    hashed_password = user_service._hash_password("password123")
    user_doc = {
        "_id": ObjectId(),
        "username": "testuser",
        "password": hashed_password
    }
    user_service.users.find_one.return_value = user_doc

    result = user_service.authenticate_user("testuser", "wrongpassword")

    assert result is None
    user_service.users.find_one.assert_called_once_with({"username": "testuser"})