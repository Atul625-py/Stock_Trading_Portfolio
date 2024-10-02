// Dynamically load navbar into the page
document.addEventListener("DOMContentLoaded", function() {

document.getElementById('navbar').innerHTML = `
    <div class="navbar">
        {% load static %}
        <link rel="stylesheet" href="{% static 'stock/css/navbar.css' %}"
        <div class="logo">
            <img src="{% static 'stock/images/logo.jpg' %}" alt="Pro Trader X Logo">
        </div>
        
        <ul class="nav-links">
            {% load static %}
            <li><a href="/"><img src="{% static 'stock/images/home.jpg' %}" alt="Home Icon"><span>Home</span></a></li>
            <li><a href="/watchlist/"><img src="{% static 'stock/images/watchlist.jpg' %}" alt="Watchlist Icon"><span>Watchlist</span></a></li>
            <li><a href="/stocks/"><img src="{% static 'stock/images/stocks.jpg' %}" alt="Stocks Icon"><span>Stocks</span></a></li>
            <li><a href="/portfolio/"><img src="{% static 'stock/images/portfolio.jpg' %}" alt="Portfolio Icon"><span>Portfolio</span></a></li>
            <li><a href="/profile/"><img src="{% static 'stock/images/profile.jpg' %}" alt="Profile Icon"><span>Profile</span></a></li>
        </ul>
        <a href="/login/" class="login-btn">Login/Register</a>
    </div>
`});
