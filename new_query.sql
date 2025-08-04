CREATE TABLE IF NOT EXISTS monthly_interest_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    chit_no VARCHAR(50),
    month INT,
    year INT,
    principal DECIMAL(10,2),
    rate DECIMAL(5,2),
    interest DECIMAL(10,2),
    calculated_at DATETIME
);

CALL calculate_monthly_interest();

