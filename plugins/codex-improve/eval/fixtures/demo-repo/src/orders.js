export async function loadOrders(db) {
  const orders = await db.allOrders();
  for (const order of orders) {
    order.customer = await db.customerById(order.customerId);
  }
  return orders;
}
