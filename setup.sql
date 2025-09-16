-- Database setup
CREATE DATABASE IF NOT EXISTS bl1tz_store;
USE bl1tz_store;

-- Users table
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),
    image_url VARCHAR(255),
    stock INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories table
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

-- News/Blog table
CREATE TABLE news (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    author VARCHAR(100),
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    featured BOOLEAN DEFAULT FALSE
);

-- Contact uploads table
CREATE TABLE contact_uploads (
    id INT PRIMARY KEY AUTO_INCREMENT,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INT,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_email VARCHAR(255),
    user_name VARCHAR(255),
    subject VARCHAR(255),
    message TEXT
);

-- System configuration table
CREATE TABLE system_config (
    id INT PRIMARY KEY AUTO_INCREMENT,
    config_key VARCHAR(255) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert users
-- PASSWORD (for all users): y0u_c4n_n0w_l0g_1n! 
INSERT INTO users (username, full_name, password, role) VALUES
('w333zard', 'Wzrd.', 'y0u_c4n_n0w_l0g_1n!', 'admin'),
('bl1tz', 'Bl1tz.', 'y0u_c4n_n0w_l0g_1n!', 'admin'),
('kibutsuji_nizam', 'Nijam Databreach', 'y0u_c4n_n0w_l0g_1n!', 'admin'),
('bagaz_infra', 'Bagas Infra', 'y0u_c4n_n0w_l0g_1n!', 'user'),
('rijal_exploit', 'Rijal Exploit', 'y0u_c4n_n0w_l0g_1n!', 'user');

-- Insert categories
INSERT INTO categories (name, description) VALUES
('Electronics', 'Latest electronic gadgets and devices'),
('Fashion', 'Trendy clothing and accessories'),
('Home & Garden', 'Everything for your home and garden'),
('Sports', 'Sports equipment and fitness gear'),
('Books', 'Wide selection of books and magazines'),
('Toys', 'Fun toys for kids and adults'),
('Beauty', 'Beauty and personal care products'),
('Automotive', 'Car accessories and parts'),
('Health', 'Health and wellness products'),
('Music', 'Musical instruments and equipment'),
('Office', 'Office supplies and equipment'),
('Pet Supplies', 'Everything for your pets'),
('Travel', 'Travel accessories and luggage'),
('Food', 'Gourmet food and beverages'),
('Gaming', 'Video games and gaming accessories');

-- Insert products
INSERT INTO products (name, description, price, category, image_url, stock) VALUES
('Lightning Gaming Laptop', 'High-performance gaming laptop with RTX 4070 graphics card and 32GB RAM', 1299.99, 'Electronics', '/static/images/laptop.jpg', 15),
('Wireless Bluetooth Headphones', 'Premium noise-cancelling headphones with 30-hour battery life', 199.99, 'Electronics', '/static/images/headphones.jpg', 50),
('Smart Watch Pro', 'Advanced fitness tracking and notifications with heart rate monitor', 299.99, 'Electronics', '/static/images/smartwatch.jpg', 30),
('Premium Denim Jacket', 'Classic style denim jacket for all seasons, 100% cotton', 89.99, 'Fashion', '/static/images/jacket.jpg', 25),
('Running Sneakers', 'Comfortable running shoes with air cushioning technology', 129.99, 'Fashion', '/static/images/sneakers.jpg', 40),
('Coffee Maker Deluxe', 'Professional coffee brewing system with programmable timer', 179.99, 'Home & Garden', '/static/images/coffee.jpg', 20),
('Yoga Mat Premium', 'Non-slip exercise mat for yoga and fitness, eco-friendly material', 39.99, 'Sports', '/static/images/yoga.jpg', 60),
('Basketball Official', 'Official size basketball for indoor/outdoor courts', 24.99, 'Sports', '/static/images/basketball.jpg', 35),
('Python Programming Guide', 'Complete guide to Python programming for beginners and experts', 49.99, 'Books', '/static/images/python-book.jpg', 45),
('Web Security Handbook', 'Comprehensive web application security guide with practical examples', 59.99, 'Books', '/static/images/security-book.jpg', 28),
('Mechanical Gaming Keyboard', 'RGB backlit mechanical keyboard with blue switches', 149.99, 'Gaming', '/static/images/keyboard.jpg', 22),
('4K Webcam Pro', 'Ultra HD webcam with auto-focus and built-in microphone', 89.99, 'Electronics', '/static/images/webcam.jpg', 18),
('Wireless Charging Station', 'Fast wireless charging pad compatible with all devices', 45.99, 'Electronics', '/static/images/charger.jpg', 55),
('Fitness Tracker Band', 'Water-resistant fitness tracker with sleep monitoring', 79.99, 'Sports', '/static/images/fitness-band.jpg', 42),
('Professional Chef Knife', 'High-carbon steel chef knife with ergonomic handle', 69.99, 'Home & Garden', '/static/images/knife.jpg', 33);

-- Insert news articles
INSERT INTO news (title, content, author, featured) VALUES
('Welcome to bl1tz Store!', 'We are excited to announce the launch of our new e-commerce platform. Discover amazing deals on electronics, fashion, and more! Our journey began with a simple vision: to make premium products accessible to everyone.', 'Admin Team', TRUE),
('Black Friday Sale Coming Soon', 'Get ready for our biggest sale of the year! Up to 70% off on selected items. Mark your calendars for November 24th! This year we are featuring deals across all categories with special flash sales every hour.', 'Marketing Team', TRUE),
('New Gaming Collection', 'Check out our latest gaming laptops and accessories. Perfect for both casual and professional gamers. Featuring the latest RTX graphics cards and high-refresh displays for the ultimate gaming experience.', 'Tech Team', FALSE),
('Summer Fashion Trends', 'Discover the hottest fashion trends for this summer. From casual wear to formal attire, we have it all. Our fashion experts have curated a collection that blends comfort with style.', 'Fashion Team', FALSE),
('Customer Support Hours', 'Our customer support team is available 24/7 to help you with any questions. Try our new AI chat assistant! We have also expanded our live chat support to include multiple languages.', 'Support Team', FALSE),
('Sustainability Initiative', 'bl1tz Store is committed to environmental responsibility. Learn about our new eco-friendly packaging and carbon-neutral shipping options. We are partnering with green logistics companies to reduce our carbon footprint.', 'Green Team', TRUE),
('Mobile App Launch', 'Download our new mobile app for iOS and Android! Get exclusive app-only deals and faster checkout. The app features augmented reality for trying products virtually before purchase.', 'Development Team', FALSE),
('Partnership with Local Artisans', 'We are proud to announce partnerships with local craftspeople and small businesses. Support your community while shopping quality handmade products available exclusively on our platform.', 'Community Team', FALSE),
('Cyber Security Awareness', 'Learn about staying safe while shopping online. Our security team shares tips for protecting your personal information. We use industry-leading encryption to protect all customer data.', 'Security Team', FALSE),
('Holiday Shipping Schedule', 'Important shipping deadlines for holiday delivery. Order by December 20th for guaranteed Christmas delivery. We have added extra shipping partners to handle the holiday rush.', 'Logistics Team', FALSE),
('Customer Loyalty Program', 'Join our new loyalty program and earn points with every purchase! Redeem points for discounts and exclusive access to new products. Premium members get free shipping on all orders.', 'Customer Relations', TRUE),
('Tech Innovation Showcase', 'Visit our innovation lab to see the latest in retail technology. Experience virtual reality shopping and AI-powered product recommendations. Open to the public every Saturday.', 'Innovation Team', FALSE),
('Employee Spotlight', 'Meet Sarah from our customer service team who has been helping customers for over 5 years. Her dedication to excellence exemplifies our commitment to customer satisfaction.', 'HR Team', FALSE),
('International Expansion', 'bl1tz Store is expanding to Europe and Asia! International customers can now enjoy our products with local currency and faster shipping options.', 'Global Team', FALSE),
('Product Quality Assurance', 'Learn about our rigorous quality testing process. Every product undergoes multiple quality checks before reaching our customers. We maintain partnerships with certified testing laboratories.', 'Quality Team', FALSE);

-- Create database user and grant privileges
CREATE USER IF NOT EXISTS 'cbd_user'@'localhost' IDENTIFIED BY 'WINDOW5-BABI';
GRANT ALL PRIVILEGES ON bl1tz_store.* TO 'cbd_user'@'localhost';
FLUSH PRIVILEGES;