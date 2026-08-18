import psycopg2

try:
    # Latch directly into your running Docker database warehouse!
    conn = psycopg2.connect(
        host="localhost",
        port="5433",
        database="postgres",
        user="postgres",
        password="postgres"
    )
    cursor = conn.cursor()
    
    # 🏢 1. Build a brand new 'employees' infrastructure table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INT PRIMARY KEY,
            name VARCHAR(50),
            department VARCHAR(50),
            salary INT,
            status VARCHAR(20)
        );
    """)
    
    # 📦 2. Bulk seed a messy enterprise corporate team roster
    mock_data = [
        (1, 'Alice', 'Engineering', 120000, 'ACTIVE'),
        (2, 'Bob', 'Engineering', 95000, 'INACTIVE'),
        (3, 'Charlie', 'Marketing', 70000, 'ACTIVE'),
        (4, 'David', 'Sales', 85000, 'ACTIVE'),
        (5, 'Eve', 'Engineering', 140000, 'ACTIVE'),
        (6, 'Frank', 'HR', 65000, 'INACTIVE'),
        (7, 'Grace', 'Sales', 90000, 'ACTIVE'),
    ]
    
    for emp in mock_data:
        cursor.execute("""
            INSERT INTO employees (id, name, department, salary, status) 
            VALUES (%s, %s, %s, %s, %s) 
            ON CONFLICT (id) DO NOTHING;
        """, emp)
    conn.commit() # Lock the new rows into the Docker hardware sandbox!
    
    # 🚀 3. Fire a complex query to search for high-earning ACTIVE Engineers!
    cursor.execute("""
        SELECT name, salary FROM employees 
        WHERE department = 'Engineering' AND salary >= 120000 AND status = 'ACTIVE' 
        ORDER BY salary DESC;
    """)
    rows = cursor.fetchall()
    
    print("\n🏆 COMPANY SIMULATION SEEDED & TESTED SUCCESSFULLY!")
    print("HIGH-EARNING ACTIVE ENGINEERS RETURNED:", rows)
    
    cursor.close()
    conn.close()

except Exception as e:
    print("\n🛑 SIMULATION ERROR:", e)