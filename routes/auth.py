"""
Authentication routes for the Academic Early Warning System
Simple single master user authentication
"""
from flask import Blueprint, jsonify, request
from functools import wraps
import hashlib
import os
import secrets
import time

auth_bp = Blueprint("auth", __name__)

# Master credentials from environment variables
MASTER_USERNAME = os.getenv("MASTER_USERNAME", "admin")
MASTER_PASSWORD_HASH = os.getenv("MASTER_PASSWORD_HASH", None)

# Simple token storage (in production, use Redis or database)
valid_tokens = {}

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

def token_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({"error": "Token de autenticación requerido"}), 401
        
        # Remove "Bearer " prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Check if token is valid and not expired
        if token not in valid_tokens:
            return jsonify({"error": "Token inválido"}), 401
        
        token_data = valid_tokens[token]
        if time.time() > token_data['expires']:
            del valid_tokens[token]
            return jsonify({"error": "Token expirado"}), 401
        
        return f(*args, **kwargs)
    return decorated

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login endpoint for master user
    Expects: { "username": "...", "password": "..." }
    Returns: { "token": "...", "user": {...} }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Datos de login requeridos"}), 400
    
    username = data.get("username", "").strip()
    password = data.get("password", "")
    
    if not username or not password:
        return jsonify({"error": "Usuario y contraseña requeridos"}), 400
    
    # Check credentials
    password_hash = hash_password(password)
    
    # If no master password hash is set, use default (change this in production!)
    expected_hash = MASTER_PASSWORD_HASH or hash_password("SATAdmin2024!")
    
    if username == MASTER_USERNAME and password_hash == expected_hash:
        # Generate token valid for 24 hours
        token = generate_token()
        expires = time.time() + (24 * 60 * 60)  # 24 hours
        
        valid_tokens[token] = {
            "username": username,
            "expires": expires
        }
        
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "username": username,
                "role": "admin",
                "name": "DECE Juan Montalvo"
            },
            "expiresIn": 24 * 60 * 60  # seconds
        })
    
    return jsonify({"error": "Credenciales inválidas"}), 401

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Logout and invalidate token"""
    token = request.headers.get('Authorization')
    
    if token:
        if token.startswith('Bearer '):
            token = token[7:]
        if token in valid_tokens:
            del valid_tokens[token]
    
    return jsonify({"success": True, "message": "Sesión cerrada"})

@auth_bp.route("/verify", methods=["GET"])
def verify_token():
    """Verify if current token is valid"""
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({"valid": False}), 401
    
    if token.startswith('Bearer '):
        token = token[7:]
    
    if token in valid_tokens:
        token_data = valid_tokens[token]
        if time.time() <= token_data['expires']:
            return jsonify({
                "valid": True,
                "user": {
                    "username": token_data['username'],
                    "role": "admin",
                    "name": "DECE Juan Montalvo"
                }
            })
        else:
            del valid_tokens[token]
    
    return jsonify({"valid": False}), 401
