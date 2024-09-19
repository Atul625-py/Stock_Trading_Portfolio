SET SQL_SAFE_UPDATES = 0;

-- DROP DATABASE IF EXISTS database_schema;
CREATE DATABASE IF NOT EXISTS database_schema;
USE database_schema;


CREATE TABLE Users (
    user_id BIGINT PRIMARY KEY CHECK (user_id >= 100000),  -- Ensures at least 6 digits
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) DEFAULT " ",
    budget DECIMAL(15, 2) DEFAULT 500 CHECK (budget >= 0),  -- Ensures non-negative budget
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Portfolios (
    portfolio_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    portfolio_name VARCHAR(100) NOT NULL,
    profit_loss DECIMAL(15, 2) DEFAULT 0,  -- New column to store profit or loss
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Stocks (
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100),
    market VARCHAR(50),
    current_price DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT,
    stock_id INT,
    transaction_type ENUM('buy', 'sell') NOT NULL,
    quantity INT NOT NULL,
    price_per_share DECIMAL(10, 2) NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES Portfolios(portfolio_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES Stocks(stock_id) ON DELETE CASCADE
);

CREATE TABLE Watchlist (
    watchlist_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    stock_id INT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES Stocks(stock_id) ON DELETE CASCADE
);

CREATE TABLE Alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    stock_id INT,
    alert_type ENUM('price_above', 'price_below') NOT NULL,
    threshold DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES Stocks(stock_id) ON DELETE CASCADE
);

CREATE TABLE Dividends (
    dividend_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT,
    dividend_amount DECIMAL(10, 2),
    payout_date DATE,
    FOREIGN KEY (stock_id) REFERENCES Stocks(stock_id) ON DELETE CASCADE
);

CREATE TABLE UserSettings (
    setting_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    setting_name VARCHAR(100) NOT NULL,
    setting_value VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);


DELIMITER $$

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
END; $$

DELIMITER ;
