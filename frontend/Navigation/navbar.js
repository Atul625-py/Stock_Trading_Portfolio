// Dynamically load navbar into the page
document.addEventListener("DOMContentLoaded", function() {

document.getElementById('navbar').innerHTML = `
    <div class="navbar">
        <link rel="stylesheet" href="./navbar.css">
        <div class="logo">
            <img src="../../Public/logo.jpg" alt="Pro Trader X Logo">
        </div>
        <ul class="nav-links">
            <li><a href="/frontend/"><img src="../../Public/home.jpg" alt="Home Icon"><span>Home</span></a></li>
            <li><a href="/frontend/watchlist/"><img src="../../Public/watchlist.jpg" alt="Watchlist Icon"><span>Watchlist</span></a></li>
            <li><a href="/frontend/stocks/"><img src="../../Public/stocks.jpg" alt="Stocks Icon"><span>Stocks</span></a></li>
            <li><a href="/frontend/portfolio/"><img src="../../Public/portfolio.jpg" alt="Portfolio Icon"><span>Portfolio</span></a></li>
            <li><a href="/frontend/profile/"><img src="../../Public/profile.jpg" alt="Profile Icon"><span>Profile</span></a></li>
        </ul>
        <a href="/frontend/login/" class="login-btn">Login/Register</a>
    </div>
`});
