"""
Tests for CRUDBase and CRUDMeta.
"""
import pytest
from ..src.zerocrud.core import CRUDBase, CRUDMeta
from ..src.zerocrud.exceptions import ModelTypeRequiredError
from .conftest import User

class TestCRUDMeta:
    """Tests for CRUDMeta metaclass."""
    
    def test_model_extraction_from_generic(self):
        """Test that extracts model from generic parameter."""
        class TestCRUD(CRUDBase[User]):
            pass
        
        assert TestCRUD.model is User
    
    def test_raises_error_without_model(self):
        """Test that raises error without specified model."""
        with pytest.raises(ModelTypeRequiredError):
            class BadCRUD(CRUDBase):
                pass

class TestCRUDBase:
    """Tests for CRUDBase."""
    
    def test_memory_storage_default(self):
        """Test that memory is the default storage."""
        class UserCRUD(CRUDBase[User]):
            pass
        
        crud = UserCRUD()
        assert crud.storage_type() == "memory"
    
    def test_database_storage_with_session(self, db_session):
        """Test that uses database with session."""
        class UserCRUD(CRUDBase[User]):
            pass
        
        crud = UserCRUD(session=db_session)
        assert crud.storage_type() == "database"
    
    def test_explicit_memory_storage(self):
        """Test explicit memory storage."""
        class UserCRUD(CRUDBase[User]):
            pass
        
        crud = UserCRUD(storage="memory")
        assert crud.storage_type() == "memory"
    
    def test_explicit_database_storage_requires_session(self):
        """Test that explicit database requires session."""
        class UserCRUD(CRUDBase[User]):
            pass
        
        with pytest.raises(ValueError, match="Database backend requires a session"):
            UserCRUD(storage="database")