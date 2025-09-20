"""
Specific tests for MemoryAdapter.
Inherits the base suite and adds implementation-specific tests.
"""
import pytest
from .conftest import User
from .test_adapters import AdapterTestSuite
from ..src.zerocrud.adapters import MemoryAdapter

class TestMemoryAdapter(AdapterTestSuite):
    """Specific tests for MemoryAdapter."""
    
    @pytest.fixture
    def adapter(self, memory_adapter):
        """Implements the fixture required by AdapterTestSuite."""
        return memory_adapter
    
    def test_memory_isolation(self):
        """Test that different instances are isolated."""
        adapter1 = MemoryAdapter(User)
        adapter2 = MemoryAdapter(User)
        
        adapter1.create({"name": "User1", "email": "user1@test.com"})
        
        assert adapter1.count() == 1
        assert adapter2.count() == 0  # Isolated
    
    def test_id_auto_increment(self, adapter):
        """Test that IDs auto-increment correctly."""
        user1 = adapter.create({"name": "User1", "email": "user1@test.com"})
        user2 = adapter.create({"name": "User2", "email": "user2@test.com"})
        
        assert user1.id == 1
        assert user2.id == 2
    
    def test_id_counter_persists_after_delete(self, adapter):
        """Test that counter doesn't reset after deletion."""
        user1 = adapter.create({"name": "User1", "email": "user1@test.com"})
        adapter.delete(user1.id)
        
        user2 = adapter.create({"name": "User2", "email": "user2@test.com"})
        
        # Counter continued forward
        assert user2.id == 2
    
    def test_manual_id_assignment(self, adapter):
        """Test that ID can be assigned manually."""
        user = adapter.create({"id": 100, "name": "User100", "email": "user100@test.com"})
        
        assert user.id == 100
        
        # Counter adjusts
        next_user = adapter.create({"name": "NextUser", "email": "next@test.com"})
        assert next_user.id == 101  # Counter continued from where it was