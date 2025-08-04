DELIMITER //

CREATE PROCEDURE calculate_monthly_interest()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_user_id INT;
    DECLARE v_chit_no VARCHAR(50);
    DECLARE v_principal DECIMAL(10,2);
    DECLARE v_rate DECIMAL(5,2);
    DECLARE v_interest DECIMAL(10,2);

    DECLARE cur CURSOR FOR
        SELECT user_id, chit_no, total_amount, interest_rate
        FROM mychitfund.interest_tracking
        WHERE month = MONTH(CURDATE())
          AND year = YEAR(CURDATE());

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO v_user_id, v_chit_no, v_principal, v_rate;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Interest Calculation: (P * R * T)/100, T = 1 month
        SET v_interest = (v_principal * v_rate * 1) / 100;

        -- Insert into summary table
        INSERT INTO mychitfund.monthly_interest_summary (
            user_id, chit_no, month, year,
            principal, rate, interest, calculated_at
        ) VALUES (
            v_user_id, v_chit_no, MONTH(CURDATE()), YEAR(CURDATE()),
            v_principal, v_rate, v_interest, NOW()
        );
    END LOOP;

    CLOSE cur;
END //

DELIMITER ;
