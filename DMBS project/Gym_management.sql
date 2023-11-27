CREATE DATABASE IF NOT EXISTS gym_management_system;
USE gym_management_system;
CREATE TABLE IF NOT EXISTS MembershipPlan (
    MembershipPlan_id INT PRIMARY KEY AUTO_INCREMENT,
    Member_id INT,
    plan_name VARCHAR(50),
    membership_start_date DATE,
    membership_end_date DATE,
    diet_plan TEXT,
    Gymsession_id INT,
	FOREIGN KEY (Member_id) REFERENCES Member(Member_id),
    FOREIGN KEY (Gymsession_id) REFERENCES GymSession(Gymsession_id)
);

CREATE TABLE IF NOT EXISTS Member
(
	Member_id INT PRIMARY KEY AUTO_INCREMENT,
    membership_id INT,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    date_of_birth DATE,
    contact_number VARCHAR(15),
    gender VARCHAR(10),
    Payments_id INT,
    member_address TEXT,
    FOREIGN KEY (membership_id) REFERENCES MembershipPlan (MembershipPlan_id),
    FOREIGN KEY (Payments_id) REFERENCES Payments(Payments_id)
);

CREATE TABLE IF NOT EXISTS GymSession (
    GymSession_id INT PRIMARY KEY AUTO_INCREMENT,
    session_timings TIME,
    session_name VARCHAR(50),
    Equipment_id INT,
    Trainer_id INT,
    FOREIGN KEY (Equipment_id) REFERENCES Equipment(Equipment_id),
    FOREIGN KEY (Trainer_id) REFERENCES Trainer(Trainer_id)
);

CREATE TABLE IF NOT EXISTS Trainer (
    Trainer_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    date_of_birth DATE,
    gender VARCHAR(10),
    contact_number VARCHAR(15),
    address VARCHAR(255),
    specialization VARCHAR(50),
    shift VARCHAR(20),
    salary DECIMAL(10, 2),
    hired_date DATE
);

CREATE TABLE IF NOT EXISTS Equipment (
    Equipment_id INT PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL,
    description TEXT,
    EquipmentStatus VARCHAR(20) DEFAULT 'Available',
    Staff_id INT,
    FOREIGN KEY (Staff_id) REFERENCES Staff(Staff_id)
);

CREATE TABLE IF NOT EXISTS Staff (
    Staff_id INT PRIMARY KEY,
    contact_number VARCHAR(15),
    position VARCHAR(50),
    salary DECIMAL(10, 2),
    date_of_birth DATE,
    hire_date DATE,
    gender VARCHAR(10),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    staff_address VARCHAR(255),
    staff_shift VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS Payments (
    Payments_id INT PRIMARY KEY,
    Member_id INT,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date DATE NOT NULL,
    FOREIGN KEY (Member_id) REFERENCES Member(Member_id)
);

DELIMITER //

CREATE TRIGGER after_insert_member
AFTER INSERT ON Member
FOR EACH ROW
BEGIN
     -- Insert a new record into Payments table when a new Member is added
     INSERT INTO Payments (Payments_id, Member_id, amount, payment_date)
     VALUES (NEW.Payments_id, NEW.Member_id, 10000, CURDATE());
END;

//

CREATE TRIGGER after_update_gym_session
AFTER UPDATE ON GymSession
FOR EACH ROW
BEGIN
    IF NEW.Equipment_id IS NOT NULL THEN
        -- Check if there are any active sessions for the equipment
        IF NOT EXISTS (
            SELECT 1
            FROM GymSession
            WHERE Equipment_id = NEW.Equipment_id AND Gymsession_id <> NEW.Gymsession_id
        ) THEN
            -- Update equipment status if no active sessions
            UPDATE Equipment SET EquipmentStatus = 'Booked' WHERE Equipment_id = NEW.Equipment_id;
        END IF;
    END IF;
END;

//

DELIMITER ;

-- Example of a JOIN operation: Selecting members and their associated plans
SELECT
    Member.first_name,
    Member.last_name,
    MembershipPlan.plan_name
FROM
    Member
	JOIN MembershipPlan ON Member.membership_id = MembershipPlan.MembershipPlan_id;

-- Selecting gym sessions with associated trainer details
SELECT
    GymSession.session_name,
    Trainer.first_name AS trainer_first_name,
    Trainer.last_name AS trainer_last_name
FROM
    GymSession
	JOIN Trainer ON GymSession.Trainer_id = Trainer.Trainer_id;
    
-- To calculate the total number of members in the gym
SELECT COUNT(*) AS total_members
FROM Member;

SELECT Member.Member_id, Member.first_name, MembershipPlan.plan_name, GymSession.Gymsession_id, Trainer.first_name AS Trainer
FROM Member
JOIN MembershipPlan ON Member.membership_id = MembershipPlan.MembershipPlan_id
JOIN GymSession ON MembershipPlan.Gymsession_id = GymSession.Gymsession_id
JOIN Trainer ON GymSession.Trainer_id = Trainer.Trainer_id;
