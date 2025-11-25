import pymysql
import os

def apply_sql_script():
    """
    Apply the SQL script to create the interest table and stored procedures.
    """
    # Database connection parameters
    db_params = {
        'host': 'db',
        'port': 3306,
        'user': 'root',
        'password': 'admin',
        'database': 'mychitfund',
    }
    
    try:
        # Connect to the database
        connection = pymysql.connect(**db_params)
        
        try:
            # Read the SQL script
            with open('interest_table_and_procedure.sql', 'r') as file:
                sql_script = file.read()
            
            # Split the script by delimiter
            statements = sql_script.split('DELIMITER //')
            
            with connection.cursor() as cursor:
                # Execute the first part (table creation)
                if len(statements) > 0:
                    cursor.execute(statements[0])
                    connection.commit()
                    print("Table creation executed successfully.")
                
                # Execute stored procedures
                if len(statements) > 1:
                    for i in range(1, len(statements)):
                        # Split by DELIMITER ;
                        proc_parts = statements[i].split('DELIMITER ;')
                        if len(proc_parts) > 0:
                            # Extract the procedure definition
                            proc_def = proc_parts[0].strip()
                            if proc_def:
                                cursor.execute(proc_def)
                                connection.commit()
                                print(f"Stored procedure {i} executed successfully.")
            
            print("SQL script applied successfully!")
            
        except Exception as e:
            print(f"Error executing SQL script: {e}")
        finally:
            connection.close()
            
    except Exception as e:
        print(f"Error connecting to the database: {e}")

if __name__ == "__main__":
    apply_sql_script()