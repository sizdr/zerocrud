"""
Global pytest configuration and shared fixtures.
"""
import pytest
from sqlmodel import SQLModel, create_engine, Session, Field
from ..src.zerocrud.adapters import MemoryAdapter, DatabaseAdapter
from ..src.zerocrud import CRUDBase

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str

class UserRepository(CRUDBase[User]): 
    pass

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {"name": "Test User", "email": "test@example.com"}

@pytest.fixture
def db_session():
    """Temporary database session for tests."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    
    session = Session(engine)
    yield session
    session.close()
    engine.dispose()

@pytest.fixture
def memory_adapter():
    """MemoryAdapter configured for tests."""
    return MemoryAdapter(User)

@pytest.fixture  
def db_adapter(db_session):
    """DatabaseAdapter configured for tests."""
    return DatabaseAdapter(User, db_session)

@pytest.fixture  
def user_repo():
    """UserRepository configured for tests."""
    return UserRepository()