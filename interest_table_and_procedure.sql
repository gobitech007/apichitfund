

CREATE PROCEDURE `new_procedure`()
BEGIN
    SELECT 
        it.interest_id,
        it.user_id,
        it.chit_id,
        it.chit_no,
        it.month,
        it.year,
        it.weeks_paid,
        it.total_amount,
        it.interest_rate,
        it.interest_amount,
        it.calculated_at,
        it.is_paid,
        it.paid_at,
        
        p.pay_id,
        p.amount,
        p.week_no,
        p.pay_type,
        p.pay_card,
        p.pay_card_name,
        p.pay_expiry_no,
        p.pay_qr,
        p.transaction_id,
        p.status,
        p.created_at AS pay_created_at,
        p.updated_at AS pay_updated_at,
        p.created_by,
        p.updated_by

    FROM 
        mychitfund.interest_tracking it
    LEFT JOIN 
        mychitfund.pay p 
        ON it.user_id = p.user_id AND it.chit_no = p.chit_no;
END 
