--------------------- users_log table --------------------------------
CREATE TABLE IF NOT EXISTS users_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    operation_type VARCHAR(10), -- INSERT, UPDATE, DELETE
    user_id INT,
    name VARCHAR(30),
    google_client_id VARCHAR(255),
    token VARCHAR(255),
    login INT,
    read_access INT,
    write_access INT,
    email VARCHAR(30),
    operation_time DATETIME DEFAULT CURRENT_TIMESTAMP
);


DROP TRIGGER IF EXISTS after_users_insert;
DROP TRIGGER IF EXISTS after_users_update;
DROP TRIGGER IF EXISTS after_users_delete;

-- After INSERT trigger
CREATE TRIGGER after_users_insert
AFTER INSERT ON users
FOR EACH ROW
BEGIN
    INSERT INTO users_log (operation_type, user_id, name, google_client_id, token, login, read_access, write_access, email)
    VALUES ('INSERT', NEW.id, NEW.name, NEW.google_client_id, NEW.token, NEW.login, NEW.read_access, NEW.write_access, NEW.email);
END;

-- After UPDATE trigger
CREATE TRIGGER after_users_update
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    INSERT INTO users_log (operation_type, user_id, name, google_client_id, token, login, read_access, write_access, email)
    VALUES ('UPDATE', NEW.id, NEW.name, NEW.google_client_id, NEW.token, NEW.login, NEW.read_access, NEW.write_access, NEW.email);
END;

-- After DELETE trigger
CREATE TRIGGER after_users_delete
AFTER DELETE ON users
FOR EACH ROW
BEGIN
    INSERT INTO users_log (operation_type, user_id, name, google_client_id, token, login, read_access, write_access, email)
    VALUES ('DELETE', OLD.id, OLD.name, OLD.google_client_id, OLD.token, OLD.login, OLD.read_access, OLD.write_access, OLD.email);
END;


---------------------- event_log table --------------------------------
CREATE TABLE IF NOT EXISTS event_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    operation_type VARCHAR(10), -- INSERT, UPDATE, DELETE
    event_id INT,
    motion_detected BOOLEAN,
    beam_status VARCHAR(50),
    light_status VARCHAR(50),
    manual_control BOOLEAN,
    operation_time DATETIME DEFAULT CURRENT_TIMESTAMP
);


DROP TRIGGER IF EXISTS after_event_insert;
DROP TRIGGER IF EXISTS after_event_update;
DROP TRIGGER IF EXISTS after_event_delete;

-- After INSERT trigger
CREATE TRIGGER after_event_insert
AFTER INSERT ON event
FOR EACH ROW
BEGIN
    INSERT INTO event_log (operation_type, event_id, motion_detected, beam_status, light_status, manual_control)
    VALUES ('INSERT', NEW.id, NEW.motion_detected, NEW.beam_status, NEW.light_status, NEW.manual_control);
END;

-- After UPDATE trigger
CREATE TRIGGER after_event_update
AFTER UPDATE ON event
FOR EACH ROW
BEGIN
    INSERT INTO event_log (operation_type, event_id, motion_detected, beam_status, light_status, manual_control)
    VALUES ('UPDATE', NEW.id, NEW.motion_detected, NEW.beam_status, NEW.light_status, NEW.manual_control);
END;

-- After DELETE trigger
CREATE TRIGGER after_event_delete
AFTER DELETE ON event
FOR EACH ROW
BEGIN
    INSERT INTO event_log (operation_type, event_id, motion_detected, beam_status, light_status, manual_control)
    VALUES ('DELETE', OLD.id, OLD.motion_detected, OLD.beam_status, OLD.light_status, OLD.manual_control);
END;
