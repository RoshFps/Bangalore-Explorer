-- Bangalore Explorer database schema (MySQL 8+)
CREATE DATABASE IF NOT EXISTS trip_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE trip_app;

CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(32)  NOT NULL UNIQUE,
    email         VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,          -- scrypt hash, never plaintext
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS HOTELS   (NAME VARCHAR(120) NOT NULL, LOCATION VARCHAR(80) NOT NULL, AVG_PRICE INT NOT NULL, INDEX (LOCATION));
CREATE TABLE IF NOT EXISTS GAMES    (NAME VARCHAR(120) NOT NULL, PLACE    VARCHAR(80) NOT NULL, PRICE     INT NOT NULL, INDEX (PLACE));
CREATE TABLE IF NOT EXISTS MALLS    (NAME VARCHAR(120) NOT NULL, PLACE    VARCHAR(80) NOT NULL, AVG_PRICE INT NOT NULL, INDEX (PLACE));
CREATE TABLE IF NOT EXISTS HANGOUTS (NAME VARCHAR(120) NOT NULL, PLACE    VARCHAR(80) NOT NULL, PRICE     INT NOT NULL, INDEX (PLACE));
CREATE TABLE IF NOT EXISTS bus      (bus_no VARCHAR(20) NOT NULL, stops VARCHAR(80) NOT NULL, INDEX (stops));

-- Least-privilege account for the app (run as an admin, change the password):
-- CREATE USER 'trip_app'@'localhost' IDENTIFIED BY 'change-me';
-- GRANT SELECT ON trip_app.* TO 'trip_app'@'localhost';
-- GRANT INSERT ON trip_app.users TO 'trip_app'@'localhost';

-- Migrating from the old plaintext `password` column:
-- ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NULL;
-- ALTER TABLE users DROP COLUMN password;   -- existing users must sign up again
