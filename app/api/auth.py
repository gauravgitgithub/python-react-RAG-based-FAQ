from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, require_minimum_role
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin, Token, User, UserUpdate
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=User)
async def signup(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user account"""
    auth_service = AuthService(db)
    return await auth_service.create_user(user_create)


@router.post("/login", response_model=Token)
async def login(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token"""
    auth_service = AuthService(db)
    return await auth_service.login(user_login)


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user information"""
    auth_service = AuthService(db)
    
    # Only allow updating email and username for now
    update_data = user_update.dict(exclude_unset=True)
    if "role" in update_data:
        del update_data["role"]  # Don't allow role changes through this endpoint
    
    if update_data:
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        await db.commit()
        await db.refresh(current_user)
    
    return current_user


@router.get("/users", response_model=list[User])
async def get_users(
    current_user: User = Depends(require_minimum_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Get all users (admin only)"""
    auth_service = AuthService(db)
    # This would need to be implemented in AuthService
    # For now, return current user as placeholder
    return [current_user]


@router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_minimum_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Update user (admin only)"""
    auth_service = AuthService(db)
    target_user = await auth_service.get_user_by_id(user_id)
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    if update_data:
        for field, value in update_data.items():
            setattr(target_user, field, value)
        
        await db.commit()
        await db.refresh(target_user)
    
    return target_user 