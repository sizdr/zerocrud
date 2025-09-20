from typing import TypeVar, Generic, get_args, get_origin, Optional, List, Literal
from sqlmodel import SQLModel, Session
from .adapters import DatabaseAdapter, MemoryAdapter
from .exceptions import ModelTypeRequiredError

# Generic type variable bound to SQLModel for type safety
T = TypeVar("T", bound=SQLModel)


class CRUDMeta(type):
    """
    Metaclass for CRUDBase that automatically extracts the model type
    from generic type parameters.
    
    This metaclass inspects the class inheritance chain to find the model type
    specified in the generic parameter (e.g., CRUDBase[User]) and assigns it
    to the `model` class attribute.
    
    Raises:
        ModelTypeRequiredError: If no model type is found in the generic parameters
    """
    
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)

        # Skip processing for the base CRUDBase class itself
        if name == "CRUDBase":
            return

        # Look for generic type parameters in the class inheritance
        if hasattr(cls, "__orig_bases__"):
            for orig_base in cls.__orig_bases__:
                origin = get_origin(orig_base)
                
                # Check if this is inheriting from CRUDBase with generic parameters
                if hasattr(origin, "__name__") and origin.__name__ == "CRUDBase":
                    args = get_args(orig_base)
                    if args:
                        # Extract the first type argument as the model
                        cls.model = args[0]
                        
        # Ensure a model was found, otherwise raise an error
        if not cls.model:
            raise ModelTypeRequiredError("CRUDBase requires a model to function correctly.")


class CRUDBase(Generic[T], metaclass=CRUDMeta):
    """
    Generic CRUD base class that provides common database operations
    with support for multiple storage backends.
    
    This class uses the adapter pattern to support different storage
    implementations (memory, database) while providing a consistent
    interface for CRUD operations.
    
    Type Parameters:
        T: The SQLModel class this CRUD instance will operate on
    
    Attributes:
        model: The SQLModel class extracted from generic parameters
        adapter: The storage adapter instance handling actual operations
    
    Example:
        ```python
        class UserCRUD(CRUDBase[User]):
            pass
        
        # Memory storage (default)
        crud = UserCRUD()
        
        # Database storage
        crud = UserCRUD(session=db_session, storage="database")
        ```
    """
    
    # Will be set by metaclass based on generic parameter
    model: type[T] = None

    def __init__(
        self, 
        session: Optional[Session] = None, 
        storage: Optional[Literal["memory", "database"]] = None,
        **kwargs
    ):
        """
        Initialize the CRUD instance with the specified storage backend.
        
        Args:
            session: SQLModel database session (required for database storage)
            storage: Storage backend type ("memory" or "database")
            **kwargs: Additional arguments passed to adapter constructors
        
        Raises:
            ValueError: If database storage is selected but no session is provided
        
        Note:
            - If no storage is specified but session is provided, defaults to database
            - If neither storage nor session is specified, defaults to memory
        """

        
        # Initialize the appropriate adapter based on storage type
        if storage == "memory":
            self.adapter = MemoryAdapter(self.model)
        elif storage == "database":
            if not session:
                raise ValueError("Database backend requires a session")
            self.adapter = DatabaseAdapter(self.model, session)
            self.session = session
        elif session is not None:
            # Auto-detect database storage when session is provided
            self.adapter = DatabaseAdapter(self.model, session)
            self.session = session
        else: 
            # Default to memory storage
            self.adapter = MemoryAdapter(self.model)

    def create(self, data: dict) -> Optional[T]:
        """
        Create a new record with the provided data.
        
        Args:
            data: Dictionary containing the field values for the new record
        
        Returns:
            The created model instance, or None if creation failed
        
        Example:
            ```python
            user = user_crud.create({"name": "Alice", "email": "alice@example.com"})
            ```
        """
        return self.adapter.create(data)
        
    def get(self, id: int) -> Optional[T]:
        """
        Retrieve a single record by its ID.
        
        Args:
            id: The unique identifier of the record to retrieve
        
        Returns:
            The model instance if found, None otherwise
        
        Example:
            ```python
            user = user_crud.get(1)
            if user:
                print(f"Found user: {user.name}")
            ```
        """
        return self.adapter.get(id)
        
    def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Retrieve a list of records with pagination support.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
        
        Returns:
            List of model instances
        
        Example:
            ```python
            # Get first 10 users
            users = user_crud.list(limit=10)
            
            # Get next 10 users (pagination)
            users = user_crud.list(skip=10, limit=10)
            ```
        """
        return self.adapter.list(skip, limit)
        
    def delete(self, id: int) -> bool:
        """
        Delete a record by its ID.
        
        Args:
            id: The unique identifier of the record to delete
        
        Returns:
            True if the record was successfully deleted, False otherwise
        
        Example:
            ```python
            if user_crud.delete(1):
                print("User deleted successfully")
            else:
                print("User not found or deletion failed")
            ```
        """
        return self.adapter.delete(id)
    
    def storage_type(self) -> str:
        """
        Get the current storage backend type.
        
        Returns:
            String identifier of the storage type ("memory" or "database")
        
        Example:
            ```python
            print(f"Using {user_crud.storage_type()} storage")
            ```
        """
        return type(self.adapter).__name__.replace("Adapter", "").lower()
    
    def update(self, id: int, data: dict) -> Optional[T]:
        """
        Update an existing record with new data.
        
        Args:
            id: The unique identifier of the record to update
            data: Dictionary containing the fields to update and their new values
        
        Returns:
            The updated model instance if successful, None otherwise
        
        Example:
            ```python
            updated_user = user_crud.update(1, {"name": "Alice Smith"})
            if updated_user:
                print(f"Updated user: {updated_user.name}")
            ```
        """
        return self.adapter.update(id, data)
    
    def count(self) -> int:
        """
        Get the total number of records.
        
        Returns:
            The total count of records in the storage
        
        Example:
            ```python
            total_users = user_crud.count()
            print(f"Total users: {total_users}")
            ```
        """
        return self.adapter.count()
