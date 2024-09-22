

INSERT INTO Users (user_id, email, username, password_hash, first_name, last_name, role, budget) VALUES
(100001, 'admin1@example.com', 'admin1', 'hashpassword1', 'Admin', 'User', 'admin', 10000),
(100002, 'user1@example.com', 'user1', 'hashpassword2', 'User1', 'One', 'user', 5000),
(100003, 'user2@example.com', 'user2', 'hashpassword3', 'User2', 'Two', 'user', 6000),
(100004, 'user3@example.com', 'user3', 'hashpassword4', 'User3', 'Three', 'user', 7000),
(100005, 'user4@example.com', 'user4', 'hashpassword5', 'User4', 'Four', 'user', 8000);


INSERT INTO Portfolios (user_id, portfolio_name) VALUES
(100001, 'Admin Portfolio'),
(100002, 'User1 Portfolio'),
(100003, 'User2 Portfolio'),
(100004, 'User3 Portfolio'),
(100005, 'User4 Portfolio');

INSERT INTO Stocks (symbol, name, market, current_price, quantity) VALUES
('AAPL', 'Apple Inc.', 'NASDAQ', 150.25, 30),
('GOOGL', 'Alphabet Inc.', 'NASDAQ', 2800.50, 30),
('TSLA', 'Tesla Inc.', 'NASDAQ', 725.00, 30),
('MSFT', 'Microsoft Corp.', 'NASDAQ', 300.00, 30),
('AMZN', 'Amazon.com Inc.', 'NASDAQ', 3400.75, 30);

INSERT INTO Watchlist (user_id, stock_id) VALUES
(100001, 1),
(100001, 2),
(100002, 3),
(100003, 4),
(100004, 5),
(100005, 1);

INSERT INTO Dividends (stock_id, dividend_amount, payout_date) VALUES
(1, 1.50, '2024-09-01'),
(2, 2.75, '2024-08-15'),
(3, 0.50, '2024-07-20'),
(4, 1.20, '2024-06-10'),
(5, 3.10, '2024-05-05');

INSERT INTO UserSettings (user_id, setting_name, setting_value) VALUES
(100001, 'theme', 'dark'),
(100002, 'notification', 'enabled'),
(100003, 'language', 'en'),
(100004, 'theme', 'light'),
(100005, 'notification', 'disabled');

INSERT INTO Transactions (portfolio_id, stock_id, transaction_type, quantity, price_per_share) VALUES
-- Admin Portfolio (User 1: Budget $10,000)
(1, 1, 'buy', 5, 140.50),
(1, 2, 'buy', 2, 2700.00),
(1, 2, 'sell', 2, 2700.00),
(1, 4, 'buy', 2, 290.00),
(1, 5, 'buy', 2, 320.00),

-- User1 Portfolio (User 2: Budget $5,000)
(2, 1, 'buy', 3, 145.75),
(2, 3, 'buy', 2, 720.00),
(2, 3, 'sell', 1, 295.00),
(2, 5, 'buy', 1, 350.00),

-- User2 Portfolio (User 3: Budget $6,000)
(3, 2, 'buy', 2, 270.50),
(3, 3, 'buy', 1, 705.25),
(3, 5, 'buy', 1, 345.00),
(3, 2, 'sell', 1, 150.00),
(3, 4, 'buy', 1, 300.50),

-- User3 Portfolio (User 4: Budget $7,000)
(4, 1, 'buy', 5, 142.75),
(4, 1, 'sell', 1, 280.00),
(4, 3, 'buy', 3, 710.00),
(4, 3, 'sell', 2, 339.00),

-- User4 Portfolio (User 5: Budget $8,000)
(5, 1, 'buy', 5, 148.00), 
(5, 2, 'buy', 2, 985.00),
(5, 2, 'sell', 2, 725.50),
(5, 4, 'buy', 2, 310.00),
(5, 4, 'sell', 1, 350.00),
(5, 3 , 'buy', 4, 751.00);


select * from transactionview;
select * from HomeView;
select * from SoldView;
select * from WatchlistView;
select * from StocksView;
select * from PortfolioView;