-- Create the interest table
CREATE TABLE IF NOT EXISTS interest_tracking (
    interest_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    chit_id INT NOT NULL,
    chit_no INT NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    weeks_paid INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    interest_rate DECIMAL(5, 2) DEFAULT 1.00,
    interest_amount DECIMAL(10, 2) NOT NULL,
    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_paid BOOLEAN DEFAULT FALSE,
    paid_at DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (chit_id) REFERENCES chit_users(chit_id),
    UNIQUE KEY unique_interest_record (user_id, chit_id, month, year)
);

-- Create stored procedure to calculate monthly interest
DELIMITER //

CREATE PROCEDURE CalculateMonthlyInterest(
    IN p_month INT,
    IN p_year INT
)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_user_id INT;
    DECLARE v_chit_id INT;
    DECLARE v_chit_no INT;
    DECLARE v_weeks_paid INT;
    DECLARE v_total_amount DECIMAL(10, 2);
    DECLARE v_interest_amount DECIMAL(10, 2);
    
    -- Cursor to get all distinct user_id and chit_id combinations
    DECLARE user_chit_cursor CURSOR FOR
        SELECT p.user_id, cu.chit_id, cu.chit_no
        FROM pay p
        JOIN chit_users cu ON p.chit_no = cu.chit_no AND p.user_id = cu.user_id
        WHERE MONTH(p.created_at) = p_month AND YEAR(p.created_at) = p_year
        GROUP BY p.user_id, cu.chit_id, cu.chit_no;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    -- Start transaction
    START TRANSACTION;
    
    -- Open cursor
    OPEN user_chit_cursor;
    
    -- Loop through all user-chit combinations
    read_loop: LOOP
        FETCH user_chit_cursor INTO v_user_id, v_chit_id, v_chit_no;
        
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- Calculate weeks paid in the month
        SELECT COUNT(*) INTO v_weeks_paid
        FROM pay p
        WHERE p.user_id = v_user_id 
          AND p.chit_no = v_chit_no
          AND MONTH(p.created_at) = p_month 
          AND YEAR(p.created_at) = p_year
          AND p.status = 'completed';
        
        -- Calculate total amount paid in the month
        SELECT SUM(p.amount) INTO v_total_amount
        FROM pay p
        WHERE p.user_id = v_user_id 
          AND p.chit_no = v_chit_no
          AND MONTH(p.created_at) = p_month 
          AND YEAR(p.created_at) = p_year
          AND p.status = 'completed';
        
        -- Calculate interest (1% of total amount)
        SET v_interest_amount = v_total_amount * 0.01;
        
        -- Check if a record already exists for this user, chit, month, and year
        IF NOT EXISTS (
            SELECT 1 FROM interest_tracking 
            WHERE user_id = v_user_id 
              AND chit_id = v_chit_id 
              AND month = p_month 
              AND year = p_year
        ) THEN
            -- Insert new record
            INSERT INTO interest_tracking (
                user_id, 
                chit_id, 
                chit_no,
                month, 
                year, 
                weeks_paid, 
                total_amount, 
                interest_amount
            ) VALUES (
                v_user_id, 
                v_chit_id, 
                v_chit_no,
                p_month, 
                p_year, 
                v_weeks_paid, 
                v_total_amount, 
                v_interest_amount
            );
        ELSE
            -- Update existing record
            UPDATE interest_tracking
            SET weeks_paid = v_weeks_paid,
                total_amount = v_total_amount,
                interest_amount = v_interest_amount,
                calculated_at = CURRENT_TIMESTAMP
            WHERE user_id = v_user_id 
              AND chit_id = v_chit_id 
              AND month = p_month 
              AND year = p_year;
        END IF;
    END LOOP;
    
    -- Close cursor
    CLOSE user_chit_cursor;
    
    -- Commit transaction
    COMMIT;
    
    -- Return the calculated interest records for the month
    SELECT 
        it.interest_id,
        u.fullname AS user_name,
        it.chit_id,
        it.chit_no,
        it.month,
        it.year,
        it.weeks_paid,
        it.total_amount,
        it.interest_rate,
        it.interest_amount,
        it.is_paid,
        it.calculated_at
    FROM interest_tracking it
    JOIN users u ON it.user_id = u.user_id
    WHERE it.month = p_month AND it.year = p_year
    ORDER BY u.fullname, it.chit_no;
END //

DELIMITER ;

-- Create a procedure to mark interest as paid
DELIMITER //

CREATE PROCEDURE MarkInterestAsPaid(
    IN p_interest_id INT
)
BEGIN
    UPDATE interest_tracking
    SET is_paid = TRUE,
        paid_at = CURRENT_TIMESTAMP
    WHERE interest_id = p_interest_id;
    
    SELECT * FROM interest_tracking WHERE interest_id = p_interest_id;
END //

DELIMITER ;