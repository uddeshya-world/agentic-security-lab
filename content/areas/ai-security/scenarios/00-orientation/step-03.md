## A tool is just an API the model can call

Ask the database tool to describe itself:

```bash
curl -s http://127.0.0.1:8101/schema
```

Notice what the schema **allows**. In vulnerable mode the `db_tool` accepts a
free-form `filter` string. That means the model (or anything that can steer the
model) can put *arbitrary SQL* into a query.

This is the core lesson of the whole Area in one observation: **the tool schema
is a security control surface.** A permissive schema is an open door — it does
not matter how well-behaved the model usually is.

Keep this in mind: everything you exploit next is downstream of a schema that
said "yes" when it should have said "only this shape."
