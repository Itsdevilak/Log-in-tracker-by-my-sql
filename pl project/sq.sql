drop database if exists Ak;
CREATE DATABASE Ak;
USE Ak;
-- Create Users table
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,   
    username VARCHAR(255) UNIQUE NOT NULL,     
    password VARCHAR(255) NOT NULL             
);
-- Create LoginAttempts table
CREATE TABLE LoginAttempts (
    attempt_id INT AUTO_INCREMENT PRIMARY KEY,  
    user_id INT NOT NULL,                       
    status ENUM('success', 'failure') NOT NULL,  
    attempt_time DATETIME DEFAULT CURRENT_TIMESTAMP,  
    FOREIGN KEY (user_id) REFERENCES Users(user_id)  
);

-- Insert a new user into the Users table
INSERT INTO Users (username, password) 
VALUES ('testuser', 'hashedpassword');
-- Insert a login attempt into the LoginAttempts table
INSERT INTO LoginAttempts (user_id, status) 
VALUES (1, 'success');  -- Assuming user_id is 1 and login was successful

-- Q1 - see all user 
select * from Users;

-- Q2 - see All user status
SELECT  Users.username,
    SUM(CASE WHEN LoginAttempts.status = 'success' THEN 1 ELSE 0 END) AS success_count,
    SUM(CASE WHEN LoginAttempts.status = 'failure' THEN 1 ELSE 0 END) AS failure_count
FROM Users
LEFT JOIN LoginAttempts ON Users.user_id = LoginAttempts.user_id
GROUP BY Users.username;

-- Q3 - See particular user 
SELECT username,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS success_count,
    SUM(CASE WHEN status = 'failure' THEN 1 ELSE 0 END) AS failure_count
FROM Users LEFT JOIN LoginAttempts ON Users.user_id = LoginAttempts.user_id
WHERE 
    Users.username = 'Alphap'  -- Replace  username for checking
GROUP BY     username;
    
    