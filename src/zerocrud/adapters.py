"""
CRUD Storage Adapters Module

This module implements the adapter pattern to provide different storage backends
for CRUD operations. The adapters abstract the underlying storage mechanism
(memory, database) while providing a consistent interface.

Architecture:
- CRUDAdapter: Abstract base class defining the interface
- MemoryAdapter: In-memory storage implementation for testing/caching
- DatabaseAdapter: SQLAlchemy/SQLModel database implementation

The adapter pattern allows easy switching between storage backends and
facilitates testing by providing a fast in-memory implementation.

Example:
    ```python
    # Memory storage for testing
    memory_adapter = MemoryAdapter(User)
    user = memory_adapter.create({"name": "Test User"})
    
    # Database storage for production
    db_adapter = DatabaseAdapter(User, session)
    user = db_adapter.create({"name": "Production User"})
    ```
"""

from typing import TypeVar, Optional, List
from abc import abstractmethod, ABC
from sqlmodel import SQLModel, Session, select

# Generic type variable bound to SQLModel for type safety across adapters
T = TypeVar("T", bound=SQLModel)
        

class CRUDAdapter(ABC):
    """
    Abstract base class for CRUD storage adapters.
    
    This class defines the interface that all storage adapters must implement.
    It uses the adapter pattern to provide a consistent API regardless of
    the underlying storage mechanism.
    
    Type Parameters:
        T: The SQLModel class this adapter will operate on
        
    Attributes:
        model: The SQLModel class this adapter manages
        
    Note:
        All methods are abstract and must be implemented by concrete adapters.
        This ensures a consistent interface across different storage backends.
    """
    
    def __init__(self, model_class: type[T]):
        """
        Initialize the adapter with a model class.
        
        Args:
            model_class: The SQLModel class this adapter will manage
        """
        self.model = model_class 
    
    @abstractmethod
    def create(self, data: dict) -> T:
        """
        Create a new record with the provided data.
        
        Args:
            data: Dictionary containing the field values for the new record
            
        Returns:
            The created model instance
            
        Raises:
            Implementation-specific exceptions based on storage backend
        """
        pass
    
    @abstractmethod
    def get(self, id: int) -> Optional[T]:
        """
        Retrieve a single record by its ID.
        
        Args:
            id: The unique identifier of the record to retrieve
            
        Returns:
            The model instance if found, None otherwise
        """
        pass
    
    @abstractmethod
    def list(self, skip: int, limit: int) -> List[T]:
        """
        Retrieve a list of records with pagination support.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of model instances
        """
        pass
    
    @abstractmethod
    def update(self, id: int, data: dict) -> Optional[T]:
        """
        Update an existing record with new data.
        
        Args:
            id: The unique identifier of the record to update
            data: Dictionary containing the fields to update
            
        Returns:
            The updated model instance if successful, None otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """
        Delete a record by its ID.
        
        Args:
            id: The unique identifier of the record to delete
            
        Returns:
            True if the record was successfully deleted, False otherwise
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """
        Get the total number of records.
        
        Returns:
            The total count of records in the storage
        """
        pass


class MemoryAdapter(CRUDAdapter):
    """
    In-memory storage adapter for CRUD operations.
    
    This adapter stores all data in memory using Python lists. It's ideal for:
    - Unit testing (fast, isolated)
    - Caching scenarios
    - Development/prototyping
    - Small datasets that fit in memory
    
    Features:
    - Automatic ID assignment for new records
    - Thread-safe for single-threaded usage
    - No persistence (data lost on restart)
    - O(n) search complexity for most operations
    
    Attributes:
        _data: Internal list storing all records
        _counter: Auto-incrementing counter for ID assignment
        
    Warning:
        This adapter is not thread-safe and data is not persistent.
        Use only for testing or single-threaded applications.
        
    Example:
        ```python
        adapter = MemoryAdapter(User)
        user = adapter.create({"name": "Alice", "email": "alice@example.com"})
        all_users = adapter.list(0, 10)
        ```
    """

    def __init__(self, model_class: type[T]):
        """
        Initialize the memory adapter.
        
        Args:
            model_class: The SQLModel class this adapter will manage
        """
        super().__init__(model_class)
        # Internal storage: list of model instances
        self._data: List[T] = []
        # Auto-incrementing counter for ID assignment
        self._counter: int = 1

    def create(self, data: dict) -> Optional[T]:
        """
        Create a new record in memory storage.
        
        Automatically assigns an ID if not provided using an internal counter.
        The record is validated using the model's validation rules.
        
        Args:
            data: Dictionary containing the field values for the new record
            
        Returns:
            The created and validated model instance
            
        Raises:
            ValidationError: If the data doesn't match the model schema
            
        Example:
            ```python
            user = adapter.create({"name": "Bob", "email": "bob@example.com"})
            print(f"Created user with ID: {user.id}")
            ```
        """

        if "id" in data and data["id"] is not None:
            if (data["id"] > self._counter):
                self._counter = data["id"] + 1
            else: 
                data["id"] = self._counter
                self._counter += 1

        # Auto-assign ID if not provided
        if "id" not in data or data["id"] is None:
            data["id"] = self._counter
            self._counter += 1

        # Validate data using SQLModel validation
        item = self.model.model_validate(data)
        self._data.append(item)
        return item
        
    def get(self, id: int) -> Optional[T]:
        """
        Retrieve a record by ID from memory storage.
        
        Uses linear search through the internal list. Performance is O(n)
        where n is the number of stored records.
        
        Args:
            id: The unique identifier of the record to retrieve
            
        Returns:
            The model instance if found, None otherwise
            
        Example:
            ```python
            user = adapter.get(1)
            if user:
                print(f"Found: {user.name}")
            ```
        """
        return next((item for item in self._data if item.id == id), None)
        
    def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Retrieve a paginated list of records from memory.
        
        Uses Python list slicing for efficient pagination.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of model instances (may be empty)
            
        Example:
            ```python
            # Get first 10 records
            first_page = adapter.list(0, 10)
            
            # Get next 10 records
            second_page = adapter.list(10, 10)
            ```
        """
        return self._data[skip:skip + limit]
    
    def update(self, id: int, data: dict) -> Optional[T]:
        """
        Update an existing record in memory storage.
        
        Finds the record by ID, merges the new data with existing data,
        and replaces the record in the list. Preserves fields not specified
        in the update data.
        
        Args:
            id: The unique identifier of the record to update
            data: Dictionary containing the fields to update and their new values
            
        Returns:
            The updated model instance if successful, None if record not found
            
        Note:
            Uses model_dump() if available (Pydantic v2), falls back to dict()
            for backwards compatibility.
            
        Example:
            ```python
            updated_user = adapter.update(1, {"name": "Alice Smith"})
            if updated_user:
                print(f"Updated: {updated_user.name}")
            ```
        """
        for i, item in enumerate(self._data):
            if item.id == id:
                # Extract current data (handle both Pydantic v1 and v2)
                item_data = item.model_dump() if hasattr(item, 'model_dump') else item.dict()
                
                # Merge with update data
                item_data.update(data)
                
                # Create new validated instance
                updated_item = self.model(**item_data)
                
                # Replace in storage
                self._data[i] = updated_item
                return updated_item
        return None
        
    def delete(self, id: int) -> bool:
        """
        Delete a record from memory storage.
        
        Finds the record by ID and removes it from the internal list.
        
        Args:
            id: The unique identifier of the record to delete
            
        Returns:
            True if the record was found and deleted, False otherwise
            
        Note:
            This operation is O(n) due to the need to find and remove from list.
            
        Example:
            ```python
            if adapter.delete(1):
                print("User deleted successfully")
            else:
                print("User not found")
            ```
        """
        item = self.get(id)
        if item: 
            self._data.remove(item)
            return True
        return False
    
    def count(self) -> int:
        """
        Get the total number of records in memory storage.
        
        Returns:
            The total count of records (integer >= 0)
            
        Example:
            ```python
            total = adapter.count()
            print(f"Total records: {total}")
            ```
        """
        return len(self._data)
    
    
class DatabaseAdapter(CRUDAdapter):
    """
    SQLAlchemy/SQLModel database adapter for CRUD operations.
    
    This adapter provides persistent storage using SQLAlchemy through SQLModel.
    It's designed for production use with full ACID compliance and concurrent access.
    
    Features:
    - Persistent storage in relational databases
    - ACID transactions
    - Concurrent access support
    - Efficient querying with SQL optimization
    - Automatic schema management through SQLModel
    
    Attributes:
        session: SQLModel session for database operations
        
    Note:
        Requires an active database session and proper database setup.
        All operations are immediately committed to the database.
        
    Example:
        ```python
        from sqlmodel import create_engine, Session
        
        engine = create_engine("sqlite:///database.db")
        session = Session(engine)
        
        adapter = DatabaseAdapter(User, session)
        user = adapter.create({"name": "Alice", "email": "alice@example.com"})
        ```
    """

    def __init__(self, model_class: type[T], session: Session):
        """
        Initialize the database adapter.
        
        Args:
            model_class: The SQLModel class this adapter will manage
            session: Active SQLModel session for database operations
            
        Note:
            The session should be properly configured and connected to a database.
            The adapter assumes the session is ready for use.
        """
        super().__init__(model_class)
        self.session = session

    def create(self, data: dict) -> Optional[T]:
        """
        Create a new record in the database.
        
        Creates a new model instance, adds it to the session, commits the
        transaction, and refreshes the instance to get any database-generated
        values (like auto-incremented IDs).
        
        Args:
            data: Dictionary containing the field values for the new record
            
        Returns:
            The created model instance with database-generated values
            
        Raises:
            SQLAlchemyError: For database-related errors
            ValidationError: If the data doesn't match the model schema
            
        Example:
            ```python
            user = adapter.create({"name": "Bob", "email": "bob@example.com"})
            print(f"Created user with ID: {user.id}")
            ```
        """
        item = self.model(**data)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)  # Get database-generated values
        return item
    
    def update(self, id: int, data: dict) -> Optional[T]:
        """
        Update an existing record in the database.
        
        Retrieves the record, updates the specified fields, commits the
        transaction, and refreshes the instance to reflect any database
        changes (like updated timestamps).
        
        Args:
            id: The unique identifier of the record to update
            data: Dictionary containing the fields to update and their new values
            
        Returns:
            The updated model instance if successful, None if record not found
            
        Raises:
            SQLAlchemyError: For database-related errors
            
        Note:
            Only updates fields that exist as attributes on the model.
            This prevents injection of invalid field names.
            
        Example:
            ```python
            updated_user = adapter.update(1, {"name": "Alice Smith"})
            if updated_user:
                print(f"Updated: {updated_user.name}")
            ```
        """
        item = self.get(id)
        if item:
            # Update only existing model attributes
            for key, value in data.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            
            self.session.add(item)
            self.session.commit()
            self.session.refresh(item)  # Get any database updates
            return item
        return None

    def get(self, id: int) -> Optional[T]:
        """
        Retrieve a single record by ID from the database.
        
        Uses SQLAlchemy's efficient get method which utilizes the identity map
        for caching and primary key optimization.
        
        Args:
            id: The unique identifier of the record to retrieve
            
        Returns:
            The model instance if found, None otherwise
            
        Example:
            ```python
            user = adapter.get(1)
            if user:
                print(f"Found: {user.name}")
            ```
        """
        return self.session.get(self.model, id)

    def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Retrieve a paginated list of records from the database.
        
        Uses SQLAlchemy's offset/limit for efficient database-level pagination.
        The query is optimized by the database engine.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of model instances (may be empty)
            
        Example:
            ```python
            # Get first 10 records
            first_page = adapter.list(0, 10)
            
            # Get next 10 records  
            second_page = adapter.list(10, 10)
            ```
        """
        return self.session.exec(select(self.model).offset(skip).limit(limit)).all()

    def delete(self, id: int) -> bool:
        """
        Delete a record from the database.
        
        Retrieves the record by ID, deletes it from the session, and commits
        the transaction. The record is permanently removed from the database.
        
        Args:
            id: The unique identifier of the record to delete
            
        Returns:
            True if the record was found and deleted, False if not found
            
        Raises:
            SQLAlchemyError: For database-related errors
            
        Warning:
            This operation is irreversible. Consider soft deletes for
            important data that might need to be recovered.
            
        Example:
            ```python
            if adapter.delete(1):
                print("User deleted successfully")
            else:
                print("User not found")
            ```
        """
        item = self.get(id)
        if item:
            self.session.delete(item)
            self.session.commit()
            return True
        return False
    
    def count(self) -> int:
        """
        Get the total number of records in the database.
        
        Executes a SELECT query to count all records of this model type.
        
        Returns:
            The total count of records (integer >= 0)
            
        Note:
            This implementation loads all records to count them, which may
            be inefficient for large datasets. Consider using a COUNT query
            for better performance.
            
        TODO:
            Optimize with: SELECT COUNT(*) FROM model_table
            
        Example:
            ```python
            total = adapter.count()
            print(f"Total records: {total}")
            ```
        """
        statement = select(self.model)
        return len(list(self.session.exec(statement).all()))
