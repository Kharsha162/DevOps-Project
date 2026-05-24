import re
import datetime
import jwt
import os
from werkzeug.security import generate_password_hash, check_password_hash
from app.core.models import User

class RegisterUseCase:
    def __init__(self, user_repository):
        self.user_repo = user_repository

    def execute(self, username, email, password):
        # Validate username
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        
        # Validate email format
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not email or not re.match(email_regex, email):
            raise ValueError("Invalid email format")
            
        # Validate password
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
            
        # Check if username or email already exists
        if self.user_repo.find_by_username(username):
            raise ValueError("Username is already taken")
        if self.user_repo.find_by_email(email):
            raise ValueError("Email is already registered")
            
        # Hash password securely
        hashed_password = generate_password_hash(password)
        
        # Save user to DB
        user = self.user_repo.create(username, email, hashed_password)
        return user.to_dict()


class LoginUseCase:
    def __init__(self, user_repository, session_cache):
        self.user_repo = user_repository
        self.cache = session_cache
        self.jwt_secret = os.getenv("JWT_SECRET", "super-secret-key-998877")

    def execute(self, username_or_email, password):
        if not username_or_email or not password:
            raise ValueError("Credentials are required")

        # Find user by either email or username
        user = self.user_repo.find_by_email(username_or_email)
        if not user:
            user = self.user_repo.find_by_username(username_or_email)
            
        # Verify credentials
        if not user or not check_password_hash(user.hashed_password, password):
            raise ValueError("Invalid username/email or password")
            
        # Generate JWT Token
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)
        payload = {
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "exp": exp_time
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
        
        # Register session in Redis/in-memory cache (with a 2-hour TTL)
        self.cache.set_session(user.id, token, ttl=7200)
        
        return {
            "user": user.to_dict(),
            "token": token,
            "expires_at": exp_time.isoformat()
        }
