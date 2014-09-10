import whmcsorders

orders = whmcsorders.list_orders()
for order in orders:
    print order
    whmcsorders.delete_order(order['id'])
