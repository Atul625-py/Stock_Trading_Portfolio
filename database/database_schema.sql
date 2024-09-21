SET SQL_SAFE_UPDATES = 0;

-- DROP DATABASE IF EXISTS database_schema;
CREATE DATABASE IF NOT EXISTS database_schema;
USE database_schema;

-- Create Users table
CREATE TABLE IF NOT EXISTS Users (
    user_id BIGINT PRIMARY KEY CHECK (user_id >= 100000),  -- Ensures at least 6 digits
    email VARCHAR(255) UNIQUE NOT NULL,  -- Ensures unique email
    username VARCHAR(50) UNIQUE NOT NULL,  -- Ensures unique username
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) DEFAULT " ",
    budget DECIMAL(15, 2) DEFAULT 500 CHECK (budget >= 0),  -- Ensures non-negative budget
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Portfolios table
CREATE TABLE IF NOT EXISTS Portfolios (
    portfolio_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,  -- Ensure user_id exists
    portfolio_name VARCHAR(100) NOT NULL,
    profit_loss DECIMAL(15, 2) DEFAULT 0,  -- Store profit or loss, defaults to 0
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Create Stocks table
CREATE TABLE IF NOT EXISTS Stocks (
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,  -- Unique stock symbols
    name VARCHAR(100) NOT NULL,  -- Name of the stock cannot be null
    market VARCHAR(50) NOT NULL,  -- Market of the stock cannot be null
    current_price DECIMAL(10, 2) CHECK (current_price >= 0),  -- Ensures positive price
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Transactions table
CREATE TABLE IF NOT EXISTS Transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,  -- Ensure portfolio_id exists
    stock_id INT NOT NULL,  -- Ensure stock_id exists
    transaction_type ENUM('buy', 'sell') NOT NULL,  -- Only 'buy' or 'sell'
    quantity INT NOT NULL CHECK (quantity > 0),  -- Quantity must be greater than 0
    price_per_share DECIMAL(10, 2) NOT NULL CHECK (price_per_share >= 0),  -- Positive price
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES Portfolios(portfolio_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES Stocks(stock_id) ON DELETE CASCADE
);

-- Create Watchlist table
CREATE TABLE IF NOT EXISTS Watchlist (
    watchlist_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,  -- Ensure user_id exists
    stock_id INT NOT NULL,  -- Ensure stock_id exists
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES Stocks(stock_id) ON DELETE CASCADE,
    UNIQUE(user_id, stock_id)  -- Ensure no duplicate entries for the same stock in a user's watchlist
);

-- Create Dividends table
CREATE TABLE IF NOT EXISTS Dividends (
    dividend_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,  -- Ensure stock_id exists
    dividend_amount DECIMAL(10, 2) CHECK (dividend_amount >= 0),  -- Ensure positive dividend amount
    payout_date DATE NOT NULL,
    FOREIGN KEY (stock_id) REFERENCES Stocks(stock_id) ON DELETE CASCADE
);

-- Create UserSettings table
CREATE TABLE IF NOT EXISTS UserSettings (
    setting_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,  -- Ensure user_id exists
    setting_name VARCHAR(100) NOT NULL,
    setting_value VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Ensure SQL_MODE is strict for better constraint enforcement
SET SESSION sql_mode = 'STRICT_ALL_TABLES';

DELIMITER $$

-- Trigger to update profit/loss in portfolio after updating stock price
CREATE TRIGGER update_profit_loss
AFTER UPDATE ON Stocks
FOR EACH ROW
BEGIN
    DECLARE total_cost DECIMAL(15, 2);
    DECLARE total_value DECIMAL(15, 2);
    DECLARE stock_quantity INT;
    DECLARE portfolio_owner BIGINT;

    -- Cursor to iterate through all portfolios that contain the updated stock
    DECLARE cur CURSOR FOR
        SELECT T.portfolio_id, T.quantity, P.user_id 
        FROM Transactions T 
        INNER JOIN Portfolios P ON T.portfolio_id = P.portfolio_id
        WHERE T.stock_id = NEW.stock_id AND T.transaction_type = 'buy';

    -- Open the cursor
    OPEN cur;

    -- Fetch the data from the cursor
    FETCH cur INTO portfolio_owner, stock_quantity;

    -- Loop through all relevant portfolios
    WHILE (cur IS NOT NULL) DO
        -- Calculate total cost of stocks in portfolio
        SELECT SUM(T.quantity * T.price_per_share) INTO total_cost
        FROM Transactions T
        WHERE T.portfolio_id = portfolio_owner AND T.stock_id = NEW.stock_id;

        -- Calculate total current value of stocks in portfolio
        SET total_value = stock_quantity * NEW.current_price;

        -- Update the profit or loss in the Portfolios table
        UPDATE Portfolios
        SET profit_loss = total_value - total_cost
        WHERE portfolio_id = portfolio_owner;

        -- Fetch the next portfolio
        FETCH cur INTO portfolio_owner, stock_quantity;
    END WHILE;

    -- Close the cursor
    CLOSE cur;
END $$

DELIMITER ;

-- Trigger to check if budget exceeds after any transaction
DELIMITER $$

CREATE TRIGGER check_budget_before_transaction
BEFORE INSERT ON Transactions
FOR EACH ROW
BEGIN
    DECLARE user_budget DECIMAL(15, 2);
    DECLARE total_cost DECIMAL(15, 2);

    -- Calculate the total cost of the transaction
    SET total_cost = NEW.quantity * NEW.price_per_share;

    -- Retrieve the user's current budget
    SELECT budget INTO user_budget 
    FROM Users 
    WHERE user_id = (SELECT user_id FROM Portfolios WHERE portfolio_id = NEW.portfolio_id);

    -- Ensure that the user can afford the transaction
    IF user_budget < total_cost THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = "Transaction exceeds user's budget";
    END IF;
END $$

DELIMITER ;

-- Trigger to prevent selling more stocks than available
DELIMITER $$

CREATE TRIGGER prevent_excessive_selling
BEFORE INSERT ON Transactions
FOR EACH ROW
BEGIN
    DECLARE owned_quantity INT;

    -- Check if it's a sell transaction
    IF NEW.transaction_type = 'sell' THEN
        -- Retrieve the quantity of stocks the user currently owns
        SELECT SUM(quantity) INTO owned_quantity
        FROM Transactions
        WHERE portfolio_id = NEW.portfolio_id AND stock_id = NEW.stock_id AND transaction_type = 'buy';

        -- If trying to sell more stocks than owned, raise an error
        IF owned_quantity < NEW.quantity THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'User is attempting to sell more stocks than owned';
        END IF;
    END IF;
END $$

DELIMITER ;