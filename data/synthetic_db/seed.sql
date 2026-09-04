INSERT INTO customers (customer_id, name, email) VALUES
  (1, 'Alice Example', 'alice@example.test'),
  (2, 'Bob Example', 'bob@example.test'),
  (3, 'Carol Example', 'carol@example.test');

INSERT INTO orders (order_id, customer_id, item, amount) VALUES
  (101, 1, 'Widget A', 19.99),
  (102, 1, 'Widget B', 5.50),
  (103, 2, 'Gadget X', 49.00),
  (104, 3, 'Gizmo Z', 12.25);
