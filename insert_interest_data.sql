CREATE DEFINER=`root`@`localhost` PROCEDURE `insert_interest_data`()
BEGIN
	DECLARE done INT DEFAULT FALSE;
    DECLARE v_user_id INT;
    DECLARE v_chit_no VARCHAR(50);
    DECLARE v_total_amount DECIMAL(10,2);
    DECLARE v_weeks_paid DECIMAL(10,2);
    DECLARE v_interest_rate DECIMAL(5,2) DEFAULT 1.5; -- 1.5% example
    DECLARE v_interest_amount DECIMAL(10,2);
    
    -- Cursor to loop through grouped payment data
    DECLARE cur CURSOR FOR
        SELECT user_id, chit_no, SUM(amount) AS total_amount,MAX(week_no) as weeks_paid
        FROM mychitfund.pay
        WHERE status = 'completed'
        GROUP BY user_id, chit_no;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO v_user_id, v_chit_no, v_total_amount, v_weeks_paid;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Calculate interest
        SET v_interest_amount = (v_total_amount * v_interest_rate) / 100;
		-- Duplicate Checking
        -- Check if the entry already exists
			IF NOT EXISTS (
				SELECT 1 FROM mychitfund.interest_tracking
				WHERE user_id = v_user_id 
				  AND chit_no = v_chit_no 
				  AND month = MONTH(CURDATE()) 
				  AND year = YEAR(CURDATE())
			) THEN
				-- Insert only if not exists
				INSERT INTO mychitfund.interest_tracking (
					user_id, chit_no, month, year, weeks_paid, total_amount, 
					interest_rate, interest_amount, calculated_at, is_paid
				) VALUES (
					v_user_id, v_chit_no, MONTH(CURDATE()), YEAR(CURDATE()), v_weeks_paid,
					v_total_amount, v_interest_rate, v_interest_amount, NOW(), 0
				);
			END IF;

        -- Insert into interest_tracking
        INSERT INTO mychitfund.interest_tracking (
            user_id, chit_no, month, year, weeks_paid, total_amount, 
            interest_rate, interest_amount, calculated_at, is_paid
        ) VALUES (
            v_user_id, v_chit_no, MONTH(CURDATE()), YEAR(CURDATE()), v_weeks_paid,
            v_total_amount, v_interest_rate, v_interest_amount, NOW(), 0
        );
    END LOOP;

    CLOSE cur;
END