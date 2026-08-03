import assert from "node:assert/strict";
import test from "node:test";

import { loadOrders } from "../src/orders.js";

test("loads customer details", async () => {
  const db = {
    async allOrders() {
      return [{ id: 1, customerId: 7 }];
    },
    async customerById(id) {
      return { id, name: "Example" };
    }
  };
  assert.equal((await loadOrders(db))[0].customer.name, "Example");
});
