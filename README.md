# ZeroCRUD 🚀
![Development Status](https://img.shields.io/badge/status-alpha-red)
[![Tests](https://github.com/sizdr/zerocrud/workflows/Tests/badge.svg)](https://github.com/sizdr/zerocrud/actions)
[![Coverage](https://codecov.io/gh/sizdr/zerocrud/branch/main/graph/badge.svg)](https://codecov.io/gh/sizdr/zerocrud)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Tired of writing the same CRUD boilerplate over and over again? Want to quickly test an idea without dealing with database setup? ZeroCRUD is exactly what you need.

Built on the Repository pattern, it lets you start with basic in-memory CRUD operations and naturally evolve towards complex database queries. Same API, different capabilities as your project grows.

**From prototype to production**: Go from "I have an idea" to "I have a working API" in less than 5 minutes.

## ⚠️ Note
ZeroCRUD is fully functional, but **not yet published on PyPI**. You can install it directly from GitHub for testing

## 🔥 Before vs After

### The problem: Repetitive boilerplate
```python
# 50+ lines for every new entity
class ProductRepository:
    def get_products(self, session: Session) -> list[Product]:
        stmt = select(Product)
        return session.exec(stmt).all()
    
    def get_product_by_id(self, session: Session, product_id: int) -> Product | None:
        return session.get(Product, product_id)
    
    def create_product(self, session: Session, product_data: ProductCreate) -> Product:
        product_obj = Product.model_validate(product_data)
        session.add(product_obj)
        session.commit()
        session.refresh(product_obj)
        return product_obj
    
    def update_product(self, session: Session, product_id: int, product_data: ProductCreate) -> Product | None:
        product_obj = session.get(Product, product_id)
        if not product_obj:
            return None
        for key, value in product_data.model_dump().items():
            setattr(product_obj, key, value)
        session.add(product_obj)
        session.commit()
        session.refresh(product_obj)
        return product_obj
    
    def delete_product(self, session: Session, product_id: int) -> bool:
        product_obj = session.get(Product, product_id)
        if not product_obj:
            return False
        session.delete(product_obj)
        session.commit()
        return True
    # ... and so on for each entity
```

### The solution: Only what really matters
```python
class ProductRepository(CRUDBase[Product]):
    # Complete CRUD included automatically ✨
    # get(), create(), list(), update(), delete(), count()
    
    def get_by_category(self, category: str) -> List[Product]:
        # Only your specific logic
        return self.session.query(Product).filter(Product.category == category).all()
    
    def get_featured_products(self) -> List[Product]:
        # Focus on what adds value
        return self.session.query(Product).filter(Product.featured == True).all()
```

**Result**: From 50+ lines of boilerplate to 3 lines + your specific logic.

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Backends](#-backends)
- [FastAPI Integration](#-fastapi-integration)
- [Advanced Usage](#-advanced-usage)
- [API Reference](#-api-reference)
- [Use Cases](#-use-cases)
- [Contributing](#-contributing)

## 🚀 Installation

```bash
pip install git+https://github.com/sizdr/zerocrud.git
```

## ⚡ Quick Start
Import CRUDBase from zerocrud and extend your own repository.

### Define your model
```python
from sqlmodel import SQLModel
from zerocrud import CRUDBase

class User(SQLModel, table=True):
    id: int = None
    name: str
    email: str
```

### Create and use your CRUD
```python
class UserCRUD(CRUDBase[User]):
    pass

# Instantiate and use
crud = UserCRUD()
user = crud.create({"name": "Ana", "email": "ana@example.com"})
user = crud.get(1)
users = crud.list(limit=10)
```

## 🗄️ Backends

### Memory (ideal for prototypes)
```python
crud = UserCRUD()  # No additional configuration
```

### Database (persistence)
```python
# With your configured SQLModel session
with Session(engine) as session:
    crud = UserCRUD(session=session)
    user = crud.create({"name": "Ana", "email": "ana@example.com"})
    session.commit()
```

## 🔗 FastAPI Integration

### Complete API in minutes
```python
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session

app = FastAPI()

def get_user_crud(session: Session = Depends(get_session)):
    return UserCRUD(session=session)

@app.post("/users/", response_model=User)
async def create_user(user: dict, crud: UserCRUD = Depends(get_user_crud)):
    return crud.create(user)

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, crud: UserCRUD = Depends(get_user_crud)):
    user = crud.get(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

@app.get("/users/", response_model=List[User])
async def list_users(crud: UserCRUD = Depends(get_user_crud)):
    return crud.list()
```

## 🏗️ Advanced Usage

### Repository Pattern for custom queries

```python
class UserRepository(CRUDBase[User]):
    # Basic CRUD included automatically
    
    def get_by_email(self, email: str) -> Optional[User]:
        if self.session:
            # Optimized database query
            return self.session.query(User).filter(User.email == email).first()
        else:
            # In-memory search
            users = self.list()
            return next((u for u in users if u.email == email), None)
    
    def get_active_users(self) -> List[User]:
        if self.session:
            return self.session.query(User).filter(User.is_active == True).all()
        else:
            return [u for u in self.list() if u.is_active]

# Usage
repo = UserRepository(session=session)
ana = repo.get_by_email("ana@example.com")
active_users = repo.get_active_users()
```

## 📚 API Reference

### CRUDBase[T]

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `create(data)` | `data: dict` | `Optional[T]` | Create a new record |
| `get(id)` | `id: int` | `Optional[T]` | Get record by ID |
| `list(skip, limit)` | `skip: int = 0`<br>`limit: int = 100` | `List[T]` | List records with pagination |
| `update(id, data)` | `id: int`<br>`data: dict` | `Optional[T]` | Update existing record |
| `delete(id)` | `id: int` | `bool` | Delete record |
| `count()` | - | `int` | Count total records |
| `storage_type()` | - | `str` | Get current backend type |

### Initialization

```python
# Memory
crud = MyCRUD()

# Database
crud = MyCRUD(session=session)

# Explicitly specify backend
crud = MyCRUD(session=session, storage="database")
```

## 🎯 Use Cases

| Scenario | Example | Setup Time |
|-----------|---------|------------|
| **Rapid prototype** | `crud = TaskCRUD()` | < 1 minute |
| **Demo API** | + FastAPI integration | < 5 minutes |
| **MVP with DB** | + SQLModel session | < 10 minutes |
| **Scalable project** | + Repository pattern | As needed |

## 🤝 Contributing

```bash
git clone https://github.com/sizdr/zerocrud.git
cd zerocrud
pip install -e ".[dev]"
pytest
```

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

[⭐ Give it a star on GitHub](https://github.com/sizdr/zerocrud) if you find this project useful

</div>