"""
Setup script for initializing the SlideForge application.
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path


def setup_environment():
    """Set up the application environment."""
    print("Setting up SlideForge environment...")
    
    # Create required directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file with default configuration...")
        with open(env_file, "w") as f:
            f.write("# SlideForge Environment Variables\n")
            f.write("DEBUG=true\n")
            f.write("SECRET_KEY=development_secret_key_change_in_production\n")
            f.write("# Database Configuration\n")
            f.write("# Uncomment for PostgreSQL in production\n")
            f.write("# DATABASE_URI=postgresql://postgres:postgres@localhost/slideforge\n")
            f.write("# LLM API Keys\n")
            f.write("# OPENAI_API_KEY=your_openai_api_key\n")
            f.write("# ANTHROPIC_API_KEY=your_anthropic_api_key\n")
    
    print("Environment setup complete.")


def setup_database():
    """Set up the database with initial schema."""
    print("Setting up database...")
    
    try:
        # Initialize Alembic if needed
        if not os.path.exists("migrations/versions"):
            print("Initializing Alembic...")
            subprocess.run(["alembic", "init", "migrations"], check=True)
        
        # Run migrations
        print("Running database migrations...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        
        print("Database setup complete.")
    except subprocess.CalledProcessError as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)


def create_superuser():
    """Create a superuser for the application."""
    print("Creating superuser...")
    
    try:
        from slideforge.db.session import SessionLocal
        from slideforge.db.models.user import User
        from slideforge.core.security import get_password_hash
        
        db = SessionLocal()
        
        # Check if superuser already exists
        superuser = db.query(User).filter(User.is_superuser == True).first()
        if superuser:
            print(f"Superuser already exists: {superuser.email}")
            return
        
        # Get superuser details
        email = input("Enter superuser email: ")
        password = input("Enter superuser password: ")
        full_name = input("Enter superuser full name (optional): ")
        
        # Create superuser
        superuser = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_active=True,
            is_superuser=True,
        )
        
        db.add(superuser)
        db.commit()
        
        print(f"Superuser {email} created successfully.")
    
    except Exception as e:
        print(f"Error creating superuser: {e}")
        sys.exit(1)
    finally:
        db.close()


def main():
    """Main entry point for setup script."""
    parser = argparse.ArgumentParser(description="Set up SlideForge application")
    parser.add_argument("--skip-env", action="store_true", help="Skip environment setup")
    parser.add_argument("--skip-db", action="store_true", help="Skip database setup")
    parser.add_argument("--skip-superuser", action="store_true", help="Skip superuser creation")
    
    args = parser.parse_args()
    
    print("SlideForge Setup")
    print("===============")
    
    if not args.skip_env:
        setup_environment()
    
    if not args.skip_db:
        setup_database()
    
    if not args.skip_superuser:
        create_superuser()
    
    print("Setup complete! You can now run the application using:")
    print("python run.py")


if __name__ == "__main__":
    main()