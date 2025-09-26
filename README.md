# ZeroCRUD 🚀
![Development Status](https://img.shields.io/badge/status-alpha-red)
[![Tests](https://github.com/sizdr/zerocrud/workflows/Tests/badge.svg)](https://github.com/sizdr/zerocrud/actions)
[![Coverage](https://codecov.io/gh/sizdr/zerocrud/branch/main/graph/badge.svg)](https://codecov.io/gh/sizdr/zerocrud)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Tired of writing the same CRUD boilerplate? ZeroCRUD lets you go from prototype to production with the same clean API.

Built on the Repository pattern - start with in-memory operations and evolve to complex database queries as your project grows.

## Quick Start

```python
from zerocrud import CRUDBase
from sqlmodel import SQLModel

class User(SQLModel, table=True):
    id: int = None
    name: str
    email: str

class UserCRUD(CRUDBase[User]):
    pass

# Memory (prototypes)
crud = UserCRUD()
user = crud.create({"name": "Ana", "email": "ana@example.com"})

# Database (production)
crud = UserCRUD(session=session)
```

## Before vs After

**Before: 50+ lines of boilerplate**
```python
class ProductRepository:
    def get_products(self, session):
        # ... lots of repetitive code
    def create_product(self, session, data):
        # ... more boilerplate
    # ... and so on
```

**After: Focus on what matters**
```python
class ProductRepository(CRUDBase[Product]):
    # Complete CRUD included ✨
    
    def get_by_category(self, category: str):
        return self.session.query(Product).filter(Product.category == category).all()
```

## FastAPI Integration

```python
def get_user_crud(session: Session = Depends(get_session)):
    return UserCRUD(session=session)

@app.post("/users/")
async def create_user(user: dict, crud: UserCRUD = Depends(get_user_crud)):
    return crud.create(user)

@app.get("/users/{user_id}")
async def get_user(user_id: int, crud: UserCRUD = Depends(get_user_crud)):
    return crud.get(user_id)
```

## Installation

```bash
pip install git+https://github.com/sizdr/zerocrud.git
```

## Repository Pattern

Extend with custom queries while keeping all basic CRUD:

```python
class UserRepository(CRUDBase[User]):
    # Basic CRUD included automatically ✨
    
    def get_by_email(self, email: str):
        if self.session:
            # Database query
            return self.session.query(User).filter(User.email == email).first()
        else:
            # In-memory search
            return next((u for u in self.list() if u.email == email), None)
    
    def get_active_users(self):
        if self.session:
            return self.session.query(User).filter(User.is_active == True).all()
        else:
            return [u for u in self.list() if u.is_active]

# Usage
repo = UserRepository(session=session)
ana = repo.get_by_email("ana@example.com")
```

## API

- `create(data)` - Create record
- `get(id)` - Get by ID  
- `list(skip, limit)` - List with pagination
- `update(id, data)` - Update record
- `delete(id)` - Delete record
- `count()` - Count records

**Memory**: `crud = MyCRUD()` • **Database**: `crud = MyCRUD(session=session)`

---

⭐ **Star on GitHub** if you find this useful!
