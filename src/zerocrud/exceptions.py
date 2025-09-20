class ModelTypeRequiredError(TypeError):
    """
    Raised when CRUDBase subclass doesn't specify a model type.
    
    This error occurs when creating a CRUDBase subclass without
    providing the model type in the generic parameter.
    
    Example:
    ```python
        # This will raise ModelTypeRequiredError
        class BadCRUD(CRUDBase):
            pass
            
        # Correct way
        class UserCRUD(CRUDBase[User]):
            pass
    ```
    """
