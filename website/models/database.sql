CREATE DATABASE poultry_auth;

-- Use the database
USE poultry_auth;

-- Create the users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255),
    username VARCHAR(255) NOT NULL UNIQUE,
    phone int,
    email VARCHAR(255) NOT NULL,
    profile_photo VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

use poultry_auth;
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

use poultry_auth;
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sort_description TEXT NOT NULL,
    full_description TEXT NOT NULL,
    product_tags VARCHAR(255) NOT NULL,
    image_url VARCHAR(255) NOT NULL
);

USE poultry_auth;
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category_id INT NOT NULL,
    slug VARCHAR(255),
    sort_description TEXT,
    colors VARCHAR(255),
    sizes VARCHAR(255),
    price DECIMAL(10, 2),
    quantity INT,
    full_detail TEXT,
    product_tags TEXT,
    image_url VARCHAR(255) -- Add this line for the image URL
);


use poultry_auth;
CREATE TABLE blogs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_url VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    blog_date DATE NOT NULL
);

