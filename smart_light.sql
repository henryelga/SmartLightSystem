-- create the database
CREATE DATABASE IF NOT EXISTS smart_light;

USE smart_light;

-- users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30),
    google_client_id VARCHAR(255) UNIQUE,
    token VARCHAR(255),
    login INT,
    read_access INT, 
    write_access INT, 
    email VARCHAR(30)
);

-- event table
CREATE TABLE event (
    id INT AUTO_INCREMENT PRIMARY KEY,
    motion_detected BOOLEAN,
    beam_status VARCHAR(50),
    light_status VARCHAR(50),
    manual_control BOOLEAN,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
