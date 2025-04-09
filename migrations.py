from sqlalchemy import Column, Integer, DateTime, ForeignKey, text
from sqlalchemy.sql import func
from database import engine
import sqlalchemy


def execute_safe(query, description):
    """Execute a query safely, handling errors"""
    try:
        print(f"Executing: {description}...")
        engine.execute(query)
        print(f"Successfully executed: {description}")
        return True
    except Exception as e:
        if "Duplicate column name" in str(e) or "already exists" in str(e):
            print(f"Skipped (already exists): {description}")
        else:
            print(f"Error executing {description}: {e}")
        return False


def column_exists(table, column):
    """Check if a column exists in a table"""
    try:
        result = engine.execute(f"""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = '{table}' 
            AND COLUMN_NAME = '{column}'
        """)
        return result.scalar() > 0
    except Exception:
        return False


def run_migrations():
    """Run database migrations to add audit fields to existing tables"""
    print("Running database migrations...")
    
    # Add created_at column to users table if it doesn't exist
    if not column_exists('users', 'created_at'):
        execute_safe("""
            ALTER TABLE users 
            ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        """, "Adding created_at to users table")
    
    # Add updated_at column to users table if it doesn't exist
    if not column_exists('users', 'updated_at'):
        execute_safe("""
            ALTER TABLE users 
            ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        """, "Adding updated_at to users table")
    
    # Add created_by column to users table if it doesn't exist
    if not column_exists('users', 'created_by'):
        execute_safe("""
            ALTER TABLE users 
            ADD COLUMN created_by INT,
            ADD CONSTRAINT fk_users_created_by
            FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
        """, "Adding created_by to users table")
    
    # Add updated_by column to users table if it doesn't exist
    if not column_exists('users', 'updated_by'):
        execute_safe("""
            ALTER TABLE users 
            ADD COLUMN updated_by INT,
            ADD CONSTRAINT fk_users_updated_by
            FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
        """, "Adding updated_by to users table")
    
    # Add created_at column to chit_users table if it doesn't exist
    if not column_exists('chit_users', 'created_at'):
        execute_safe("""
            ALTER TABLE chit_users 
            ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        """, "Adding created_at to chit_users table")
    
    # Add updated_at column to chit_users table if it doesn't exist
    if not column_exists('chit_users', 'updated_at'):
        execute_safe("""
            ALTER TABLE chit_users 
            ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        """, "Adding updated_at to chit_users table")
    
    # Add created_by column to chit_users table if it doesn't exist
    if not column_exists('chit_users', 'created_by'):
        execute_safe("""
            ALTER TABLE chit_users 
            ADD COLUMN created_by INT,
            ADD CONSTRAINT fk_chit_users_created_by
            FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
        """, "Adding created_by to chit_users table")
    
    # Add updated_by column to chit_users table if it doesn't exist
    if not column_exists('chit_users', 'updated_by'):
        execute_safe("""
            ALTER TABLE chit_users 
            ADD COLUMN updated_by INT,
            ADD CONSTRAINT fk_chit_users_updated_by
            FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
        """, "Adding updated_by to chit_users table")
    
    # Add foreign key to user_id in chit_users table if it doesn't exist
    try:
        print("Checking foreign key for user_id in chit_users table...")
        result = engine.execute("""
            SELECT COUNT(*) 
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'chit_users' 
            AND COLUMN_NAME = 'user_id' 
            AND REFERENCED_TABLE_NAME = 'users'
        """)
        count = result.scalar()
        
        if count == 0:
            execute_safe("""
                ALTER TABLE chit_users
                ADD CONSTRAINT fk_chit_users_user_id
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            """, "Adding foreign key to user_id in chit_users table")
        else:
            print("Foreign key already exists for user_id in chit_users table")
    except Exception as e:
        print(f"Error checking foreign key for user_id in chit_users table: {e}")
    
    print("Database migrations completed")


if __name__ == "__main__":
    run_migrations()