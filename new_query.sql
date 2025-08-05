

ALTER TABLE mychitfund.interest_tracking
ADD UNIQUE KEY unique_interest (user_id, chit_no, month, year);

SET GLOBAL event_scheduler = ON;

SHOW EVENTS FROM mychitfund;
SHOW CREATE EVENT run_interest_every_10_days;
INSERT INTO procedure_log (message, created_at) VALUES ('Procedure ran', NOW());


SHOW VARIABLES LIKE 'event_scheduler';

CREATE EVENT IF NOT EXISTS mychitfund.run_interest_every_10_days
ON SCHEDULE
    EVERY 10 DAY
STARTS CURRENT_TIMESTAMP
DO
    CALL mychitfund.insert_interest_data();
    
CREATE EVENT IF NOT EXISTS mychitfund.calculate_monthly_interest
ON SCHEDULE
    EVERY 30 DAY
STARTS CURRENT_TIMESTAMP
DO
    CALL mychitfund.calculate_monthly_interest();

ALTER EVENT mychitfund.run_interest_every_10_days
ON SCHEDULE
    EVERY 1 DAY
STARTS CURRENT_TIMESTAMP;
ALTER EVENT mychitfund.run_interest_every_10_days
ON SCHEDULE
    EVERY 1 DAY
    STARTS TIMESTAMP(CURRENT_DATE, '12:00:00');
    
    SELECT @@global.time_zone, @@session.time_zone;

SET SQL_SAFE_UPDATES = 0;
CALL mychitfund.calculate_monthly_interest();
SET SQL_SAFE_UPDATES = 1;

ALTER TABLE mychitfund.monthly_interest_summary
ADD INDEX idx_summary_keys (user_id, chit_no, month, year);