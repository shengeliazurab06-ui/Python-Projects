import sqlite3
import os

def view_data():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "casino_data.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n=== USER DATABASE ===")
        print(f"{'Username':<15} | {'Password':<15} | {'Balance'}")
        print("-" * 50)
        
        cursor.execute("SELECT * FROM users")
        for row in cursor.fetchall():
            print(f"{row[0]:<15} | {row[1]:<15} | {row[2]}")
            
        conn.close()
        input("\nPress Enter to exit...")
        
    except Exception as e:
        print(f"Failed to read database: {e}")

if __name__ == "__main__":
    view_data()