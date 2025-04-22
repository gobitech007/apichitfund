import pymysql
from datetime import datetime, timedelta
import random

def test_interest_calculation():
    """
    Test the interest calculation functionality by:
    1. Creating test data (users, chits, payments)
    2. Running the interest calculation procedure
    3. Verifying the results
    """
    # Database connection parameters
    db_params = {
        'host': 'localhost',
        'user': 'root',
        'password': 'admin',
        'database': 'mychitfund',
    }
    
    try:
        # Connect to the database
        connection = pymysql.connect(**db_params)
        
        try:
            with connection.cursor() as cursor:
                # Get current month and year
                current_date = datetime.now()
                current_month = current_date.month
                current_year = current_date.year
                
                # Check if we have test data
                cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'test@example.com'")
                user_count = cursor.fetchone()[0]
                
                # Create test user if needed
                user_id = None
                if user_count == 0:
                    print("Creating test user...")
                    cursor.execute("""
                        INSERT INTO users (fullname, email, phone, aadhar, dob, password, pin, role)
                        VALUES ('Test User', 'test@example.com', '9876543210', '123456789012', '1990-01-01', 'password', 1234, 'user')
                    """)
                    connection.commit()
                    user_id = cursor.lastrowid
                else:
                    cursor.execute("SELECT user_id FROM users WHERE email = 'test@example.com'")
                    user_id = cursor.fetchone()[0]
                
                print(f"Using test user with ID: {user_id}")
                
                # Create test chit if needed
                cursor.execute(f"SELECT COUNT(*) FROM chit_users WHERE user_id = {user_id}")
                chit_count = cursor.fetchone()[0]
                
                chit_id = None
                chit_no = None
                if chit_count == 0:
                    print("Creating test chit...")
                    chit_no = random.randint(1000, 9999)
                    cursor.execute(f"""
                        INSERT INTO chit_users (user_id, chit_no, amount)
                        VALUES ({user_id}, {chit_no}, 500)
                    """)
                    connection.commit()
                    chit_id = cursor.lastrowid
                else:
                    cursor.execute(f"SELECT chit_id, chit_no FROM chit_users WHERE user_id = {user_id} LIMIT 1")
                    result = cursor.fetchone()
                    chit_id = result[0]
                    chit_no = result[1]
                
                print(f"Using chit with ID: {chit_id}, Chit No: {chit_no}")
                
                # Create test payments for the current month
                print("Creating test payments...")
                # Delete existing test payments for this month
                cursor.execute(f"""
                    DELETE FROM pay 
                    WHERE user_id = {user_id} 
                    AND chit_no = {chit_no}
                    AND MONTH(created_at) = {current_month}
                    AND YEAR(created_at) = {current_year}
                """)
                connection.commit()
                
                # Create 4 weekly payments
                base_date = datetime(current_year, current_month, 1)
                for week in range(1, 5):
                    payment_date = base_date + timedelta(days=week*7)
                    cursor.execute(f"""
                        INSERT INTO pay (user_id, chit_no, amount, week_no, pay_type, status, created_at)
                        VALUES ({user_id}, {chit_no}, 500, {week}, 'UPI', 'completed', '{payment_date.strftime('%Y-%m-%d %H:%M:%S')}')
                    """)
                connection.commit()
                print("Created 4 weekly payments of ₹500 each")
                
                # Run the interest calculation procedure
                print(f"Calculating interest for month {current_month}, year {current_year}...")
                cursor.execute(f"CALL CalculateMonthlyInterest({current_month}, {current_year})")
                
                # Fetch and display the results
                results = cursor.fetchall()
                if results:
                    print("\nInterest Calculation Results:")
                    column_names = [desc[0] for desc in cursor.description]
                    for result in results:
                        for i, value in enumerate(result):
                            print(f"{column_names[i]}: {value}")
                        print("-" * 40)
                else:
                    print("No interest records were calculated.")
                
                # Verify the interest calculation
                cursor.execute(f"""
                    SELECT weeks_paid, total_amount, interest_amount
                    FROM interest_tracking
                    WHERE user_id = {user_id}
                    AND chit_id = {chit_id}
                    AND month = {current_month}
                    AND year = {current_year}
                """)
                
                interest_record = cursor.fetchone()
                if interest_record:
                    weeks_paid = interest_record[0]
                    total_amount = interest_record[1]
                    interest_amount = interest_record[2]
                    
                    print("\nVerification:")
                    print(f"Weeks paid: {weeks_paid} (Expected: 4)")
                    print(f"Total amount: ₹{total_amount} (Expected: ₹2000)")
                    print(f"Interest amount (1%): ₹{interest_amount} (Expected: ₹20)")
                    
                    # Verify calculations
                    expected_total = 4 * 500  # 4 weeks * ₹500
                    expected_interest = expected_total * 0.01  # 1% of total
                    
                    if weeks_paid == 4 and total_amount == expected_total and interest_amount == expected_interest:
                        print("\nTest PASSED! Interest calculation is working correctly.")
                    else:
                        print("\nTest FAILED! Interest calculation has issues.")
                else:
                    print("\nTest FAILED! No interest record was found.")
            
        except Exception as e:
            print(f"Error during test: {e}")
        finally:
            connection.close()
            
    except Exception as e:
        print(f"Error connecting to the database: {e}")

if __name__ == "__main__":
    test_interest_calculation()