import pytest
from ..src.zerocrud import CRUDBase
from ..src.zerocrud.exceptions import ModelTypeRequiredError
from pydantic import ValidationError

class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_create_with_invalid_data(self, user_repo):
        """Test creation with invalid data"""
    
        with pytest.raises((ValidationError)):
            user_repo.create({"invalid_field": "value"})  # Missing required fields
    
    def test_update_partial_data(self, user_repo, sample_user_data):
        """Test updating with partial data"""
        user = user_repo.create(sample_user_data)
        
        # Update only one field
        updated = user_repo.update(user.id, {"name": "New Name"})
        
        assert updated.name == "New Name"
        assert updated.email == sample_user_data["email"]  # Should remain unchanged
    
    def test_empty_list_operations(self, user_repo):
        """Test operations on empty repository"""
        assert user_repo.list() == []
        assert user_repo.count() == 0
        assert user_repo.get(1) is None
        assert user_repo.delete(1) is False

    def test_empty_model_value(self):
        """Test creation with invalid data"""
        
        with pytest.raises(ModelTypeRequiredError):
            class SomeRepository(CRUDBase):
                pass