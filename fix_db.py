import psycopg2
import getpass

def fix_db():
    print("--- Fixing PostgreSQL 15+ Permissions ---")
    password = getpass.getpass("Enter password for 'postgres' superuser (it will be hidden as you type): ")
    try:
        # Connect as superuser
        conn = psycopg2.connect(
            dbname="shopconnect",
            user="postgres",
            password=password,
            host="localhost",
            port="5432"
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        print("Changing database owner to 'shopconnect_user'...")
        cur.execute("ALTER DATABASE shopconnect OWNER TO shopconnect_user;")
        
        print("Granting public schema permissions...")
        cur.execute("GRANT ALL ON SCHEMA public TO shopconnect_user;")
        
        print("\nSUCCESS! Permissions have been fixed.")
        print("You can now safely run: python manage.py migrate")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure your PostgreSQL server is running and the password is correct.")

if __name__ == "__main__":
    fix_db()
