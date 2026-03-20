from flask import Flask, render_template, request, redirect, url_for, session

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
