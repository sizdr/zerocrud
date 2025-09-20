"""
Base test suite for all adapters.
Ensures consistent behavior across implementations.
"""
import pytest
from abc import ABC

class AdapterTestSuite(ABC):
    """
    Abstract test suite that all adapters must pass.
    
    Each specific adapter inherits from this class and only needs
    to implement the 'adapter' fixture.
    """
    
    @pytest.fixture
    def adapter(self):
        """Must be implemented by each test class."""
        raise NotImplementedError("Subclasses must implement adapter fixture")
    
    def test_create_with_valid_data(self, adapter, sample_user_data):
        """Test that create works with valid data."""
        user = adapter.create(sample_user_data)
        
        assert user is not None
        assert user.name == sample_user_data["name"]
        assert user.email == sample_user_data["email"]
        assert user.id is not None
    
    def test_get_existing_record(self, adapter, sample_user_data):
        """Test that get returns existing record."""
        created_user = adapter.create(sample_user_data)
        retrieved_user = adapter.get(created_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.name == created_user.name
    
    def test_get_nonexistent_record(self, adapter):
        """Test that get returns None for non-existent IDs."""
        result = adapter.get(9999)
        assert result is None
    
    def test_list_pagination(self, adapter):
        """Test that list handles pagination correctly."""
        # Create 15 users
        users = []
        for i in range(15):
            user_data = {"name": f"User{i}", "email": f"user{i}@test.com"}
            users.append(adapter.create(user_data))
        
        # Test pagination
        page1 = adapter.list(skip=0, limit=10)
        page2 = adapter.list(skip=10, limit=10)
        
        assert len(page1) == 10
        assert len(page2) == 5
        
        # Verify they are different records
        page1_ids = {u.id for u in page1}
        page2_ids = {u.id for u in page2}
        assert page1_ids.isdisjoint(page2_ids)
    
    def test_update_existing_record(self, adapter, sample_user_data):
        """Test that update modifies existing record."""
        user = adapter.create(sample_user_data)
        
        updated_user = adapter.update(user.id, {"name": "Updated Name"})
        
        assert updated_user is not None
        assert updated_user.id == user.id
        assert updated_user.name == "Updated Name"
        assert updated_user.email == sample_user_data["email"]  # Unchanged
    
    def test_update_nonexistent_record(self, adapter):
        """Test that update returns None for non-existent IDs."""
        result = adapter.update(9999, {"name": "New Name"})
        assert result is None
    
    def test_delete_existing_record(self, adapter, sample_user_data):
        """Test that delete removes existing record."""
        user = adapter.create(sample_user_data)
        
        deleted = adapter.delete(user.id)
        assert deleted is True
        
        # Verify it no longer exists
        retrieved = adapter.get(user.id)
        assert retrieved is None
    
    def test_delete_nonexistent_record(self, adapter):
        """Test that delete returns False for non-existent IDs."""
        result = adapter.delete(9999)
        assert result is False
    
    def test_count_empty(self, adapter):
        """Test that count returns 0 when there are no records."""
        assert adapter.count() == 0
    
    def test_count_with_records(self, adapter, sample_user_data):
        """Test that count returns correct number of records."""
        assert adapter.count() == 0
        
        adapter.create(sample_user_data)
        assert adapter.count() == 1
        
        adapter.create({**sample_user_data, "email": "other@test.com"})
        assert adapter.count() == 2