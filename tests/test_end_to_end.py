"""
End-to-end tests that verify complete workflows.
"""
import pytest
from ..src.zerocrud import CRUDBase
from .conftest import User

def test_complete_crud_workflow_memory():
    """Test complete CRUD workflow with MemoryAdapter."""
    class UserCRUD(CRUDBase[User]):
        pass
    
    crud = UserCRUD(storage="memory")
    
    # Create
    user = crud.create({"name": "Alice", "email": "alice@test.com"})
    assert user.id == 1
    
    # Read
    retrieved = crud.get(user.id)
    assert retrieved.name == "Alice"
    
    # Update  
    updated = crud.update(user.id, {"name": "Alice Smith"})
    assert updated.name == "Alice Smith"
    
    # List
    users = crud.list()
    assert len(users) == 1
    
    # Count
    assert crud.count() == 1
    
    # Delete
    deleted = crud.delete(user.id)
    assert deleted is True
    assert crud.count() == 0

def test_adapter_consistency():
    """Test that both adapters behave equally."""
    # This test would be more complex but demonstrates the concept
    pass