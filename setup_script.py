from pathlib import Path
base = Path('d:/GuideWire_Project')

(base / 'requirements.txt').write_text('Flask==2.3.3\n')

app_py = '''from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'super-secret-key-change-me'

restaurants = [
    {'id': 1, 'name': 'Pasta Paradise', 'location': 'Downtown'},
    {'id': 2, 'name': 'Sushi Republic', 'location': 'Uptown'},
    {'id': 3, 'name': 'Burger House', 'location': 'Midtown'},
]

menu_items = [
    {'id': 1, 'restaurant_id': 1, 'name': 'Spaghetti Carbonara', 'price': 12.5},
    {'id': 2, 'restaurant_id': 1, 'name': 'Fettuccine Alfredo', 'price': 11.0},
    {'id': 3, 'restaurant_id': 2, 'name': 'Salmon Nigiri', 'price': 9.0},
    {'id': 4, 'restaurant_id': 2, 'name': 'Dragon Roll', 'price': 14.5},
    {'id': 5, 'restaurant_id': 3, 'name': 'Classic Cheeseburger', 'price': 10.0},
    {'id': 6, 'restaurant_id': 3, 'name': 'Fries', 'price': 3.5},
]

fake_orders = [
    {'order_id': 1001, 'restaurant': 'Pasta Paradise', 'total': 24.0, 'status': 'DELIVERED'},
    {'order_id': 1002, 'restaurant': 'Sushi Republic', 'total': 29.5, 'status': 'OUT_FOR_DELIVERY'},
]


def get_restaurant(rid):
    return next((r for r in restaurants if r['id'] == rid), None)


def get_items_for_restaurant(rid):
    return [item for item in menu_items if item['restaurant_id'] == rid]


@app.route('/')
def index():
    return render_template('index.html', restaurants=restaurants)


@app.route('/restaurant/<int:restaurant_id>')
def restaurant_detail(restaurant_id):
    rest = get_restaurant(restaurant_id)
    if not rest:
        return 'Restaurant not found', 404
    items = get_items_for_restaurant(restaurant_id)
    return render_template('restaurant.html', restaurant=rest, menu_items=items)


@app.route('/cart')
def cart():
    cart_data = session.get('cart', {})
    items = []
    total = 0.0
    for item_id_str, qty in cart_data.items():
        item = next((i for i in menu_items if i['id'] == int(item_id_str)), None)
        if not item:
            continue
        subtotal = item['price'] * qty
        total += subtotal
        items.append({**item, 'qty': qty, 'subtotal': subtotal})
    return render_template('cart.html', items=items, total=total)


@app.route('/cart/add/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    cart_data = session.get('cart', {})
    cart_data[str(item_id)] = cart_data.get(str(item_id), 0) + 1
    session['cart'] = cart_data
    return redirect(request.referrer or url_for('index'))


@app.route('/cart/remove/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    cart_data = session.get('cart', {})
    cart_data.pop(str(item_id), None)
    session['cart'] = cart_data
    return redirect(url_for('cart'))


@app.route('/cart/clear', methods=['POST'])
def clear_cart():
    session['cart'] = {}
    return redirect(url_for('cart'))


@app.route('/order/place', methods=['POST'])
def place_order():
    session['cart'] = {}
    session['last_order'] = 'Order placed successfully (simulated)'
    return redirect(url_for('orders'))


@app.route('/orders')
def orders():
    message = session.pop('last_order', None)
    return render_template('orders.html', orders=fake_orders, message=message)


if __name__ == '__main__':
    app.run(debug=True)
'''

(base / 'app.py').write_text(app_py)

templates_dir = base / 'templates'
templates_dir.mkdir(exist_ok=True)

(base / 'templates' / 'base.html').write_text("""<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>{% block title %}Food Delivery Mock{% endblock %}</title>
    <link rel='stylesheet' href='{{ url_for('static', filename='css/style.css') }}'>
</head>
<body>
<header>
    <div class='navbar'>
        <a href='{{ url_for('index') }}'>Home</a>
        <a href='{{ url_for('cart') }}'>Cart</a>
        <a href='{{ url_for('orders') }}'>Orders</a>
    </div>
</header>
<div class='container'>
    {% block content %}{% endblock %}
</div>
</body>
</html>
""")

(base / 'templates' / 'index.html').write_text("""{% extends 'base.html' %}
{% block title %}Home{% endblock %}
{% block content %}
<h1>Restaurants</h1>
<div class='list'>
    {% for restaurant in restaurants %}
        <div class='card'>
            <h2>{{ restaurant.name }}</h2>
            <p>{{ restaurant.location }}</p>
            <a class='button' href='{{ url_for('restaurant_detail', restaurant_id=restaurant.id) }}'>View Menu</a>
        </div>
    {% endfor %}
</div>
{% endblock %}
""")

(base / 'templates' / 'restaurant.html').write_text("""{% extends 'base.html' %}
{% block title %}{{ restaurant.name }}{% endblock %}
{% block content %}
<h1>{{ restaurant.name }}</h1>
<p>Location: {{ restaurant.location }}</p>
<h2>Menu</h2>
<div class='list'>
    {% if menu_items %}
        {% for item in menu_items %}
            <div class='card'>
                <h3>{{ item.name }}</h3>
                <p>Price: ${{ '%.2f'|format(item.price) }}</p>
                <form action='{{ url_for('add_to_cart', item_id=item.id) }}' method='post'>
                    <button class='button' type='submit'>Add to Cart</button>
                </form>
            </div>
        {% endfor %}
    {% else %}
        <p>No items available.</p>
    {% endif %}
</div>
{% endblock %}
""")

(base / 'templates' / 'cart.html').write_text("""{% extends 'base.html' %}
{% block title %}Cart{% endblock %}
{% block content %}
<h1>Cart</h1>
{% if items %}
<table>
    <thead><tr><th>Item</th><th>Qty</th><th>Subtotal</th><th>Action</th></tr></thead>
    <tbody>
    {% for item in items %}
        <tr>
            <td>{{ item.name }}</td>
            <td>{{ item.qty }}</td>
            <td>${{ '%.2f'|format(item.subtotal) }}</td>
            <td>
                <form action='{{ url_for('remove_from_cart', item_id=item.id) }}' method='post' style='display:inline;'>
                    <button type='submit'>Remove</button>
                </form>
            </td>
        </tr>
    {% endfor %}
    </tbody>
</table>
<p>Total: ${{ '%.2f'|format(total) }}</p>
<form action='{{ url_for('clear_cart') }}' method='post' style='display:inline;'>
    <button type='submit'>Clear Cart</button>
</form>
<form action='{{ url_for('place_order') }}' method='post' style='display:inline;margin-left:10px;'>
    <button type='submit'>Place Order</button>
</form>
{% else %}
<p>Your cart is empty.</p>
{% endif %}
{% endblock %}
""")

(base / 'templates' / 'orders.html').write_text("""{% extends 'base.html' %}
{% block title %}Orders{% endblock %}
{% block content %}
<h1>Order History</h1>
{% if message %}<p class='success'>{{ message }}</p>{% endif %}
{% if orders %}
<ul>
    {% for order in orders %}
        <li>Order #{{ order.order_id }} - {{ order.restaurant }} - ${{ '%.2f'|format(order.total) }} - {{ order.status }}</li>
    {% endfor %}
</ul>
{% else %}
<p>You have no orders yet.</p>
{% endif %}
{% endblock %}
""")

static_css_dir = base / 'static' / 'css'
static_css_dir.mkdir(parents=True, exist_ok=True)
(static_css_dir / 'style.css').write_text('''body { font-family: Arial, sans-serif; background: #f3f4f6; color: #333; margin:0; padding:0; }
header .navbar { background:#0066cc; padding:15px; display:flex; gap:12px; }
header .navbar a { color: #fff; text-decoration:none; font-weight:bold; }
.container { max-width: 960px; margin: 20px auto; padding: 0 16px; }
.list { display:grid; gap:12px; }
.card { background:#fff; padding:14px; border-radius:8px; border:1px solid #ddd; }
.button { background:#0066cc; color:#fff; border:none; padding:8px 12px; border-radius:4px; cursor:pointer; }
table { width:100%; border-collapse:collapse; margin-bottom: 12px; }
th, td { padding:8px; border: 1px solid #ddd; }
.success { color: #155724; background:#d4edda; padding:8px; border-radius:4px; }
''')

print('files written')
