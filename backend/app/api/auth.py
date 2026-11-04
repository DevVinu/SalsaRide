from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime
import uuid
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.database import db_manager

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if db_manager.is_connected:
        user = await db_manager.db.users.find_one({"_id": user_id})
        if not user:
            user = await db_manager.db.users.find_one({"id": user_id})
    else:
        user = next((u for u in db_manager.in_memory_store["users"] if u["id"] == user_id), None)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    # Check if user already exists
    if db_manager.is_connected:
        existing = await db_manager.db.users.find_one({"email": user_in.email})
    else:
        existing = next((u for u in db_manager.in_memory_store["users"] if u["email"] == user_in.email), None)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    user_dict = {
        "id": f"usr_{uuid.uuid4().hex[:12]}",
        "email": user_in.email,
        "full_name": user_in.full_name,
        "phone": user_in.phone,
        "hashed_password": hash_password(user_in.password),
        "role": user_in.role.value,
        "location_sharing_enabled": user_in.location_sharing_enabled,
        "is_active": True,
        "created_at": datetime.utcnow()
    }

    if db_manager.is_connected:
        await db_manager.db.users.insert_one(user_dict)
    else:
        db_manager.in_memory_store["users"].append(user_dict)

    token = create_access_token(subject=user_dict["id"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_dict
    }


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    if db_manager.is_connected:
        user = await db_manager.db.users.find_one({"email": credentials.email})
    else:
        user = next((u for u in db_manager.in_memory_store["users"] if u["email"] == credentials.email), None)

    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=user["id"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

