# Design Document

## Pagination Strategy

### Why Keyset Pagination?

We evaluated three approaches:

| Criteria | Offset | Cursor (opaque) | Keyset |
|---|---|---|---|
| Performance at depth | O(n) — scans skipped rows | O(log n) | O(log n) — index seek |
| Duplicates on INSERT | Yes — rows shift forward | No | No |
| Missing rows on INSERT | Yes — rows shift forward | No | No |
| Bookmarkable pages | Yes | No | No |
| Implementation complexity | Low | Medium | Medium |

**Offset pagination was rejected** because `OFFSET 100000` forces PostgreSQL to fetch and discard 100,000 rows before returning the requested page. At 200K products, browsing deep pages becomes progressively slower. Worse, if a new product is inserted while the user is browsing, rows shift — causing the user to see duplicates or skip products entirely.

### How Keyset Pagination Works

Products are ordered by `(created_at DESC, id DESC)`. The cursor encodes the `(created_at, id)` of the last product on the current page. The next page query becomes:

```sql
SELECT * FROM products
WHERE (created_at, id) < (:cursor_created_at, :cursor_id)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

This is a **tuple comparison** that PostgreSQL optimizes into an **index range scan** — it seeks directly to the cursor position in the B-tree index, regardless of how many pages deep the user is.

### How Duplicates Are Prevented

Each product has a unique, immutable `(created_at, id)` pair. The keyset condition `< (cursor_created_at, cursor_id)` defines a strict boundary: once a product is "behind" the cursor, it can never appear again on subsequent pages. The cursor advances monotonically — there is no way for a previously-seen product to satisfy the `<` condition on a later page.

### How Missing Products Are Prevented

New products are inserted with `created_at = NOW()`, which is always **newer** than any cursor the user holds. This means new inserts land in the "already browsed" region (before the cursor in DESC order) — they don't displace or push down products the user hasn't seen yet. The user's remaining pages are completely unaffected.

**Why `created_at` and not `updated_at`?** If we sorted by `updated_at`, then updating a product would move it to the front of the list, potentially causing the user to see it twice (once in its original position, once at the top). By sorting on immutable `created_at`, updates cannot change a product's position in the browsing order.

### Why `id` as a Tiebreaker?

`created_at` alone isn't unique — bulk inserts can produce thousands of products with identical timestamps. The UUID `id` serves as a guaranteed-unique tiebreaker, ensuring every product has a distinct position in the sort order. This makes the keyset condition unambiguous.

## Indexing Strategy

### Index 1: `(created_at DESC, id DESC)`

```sql
CREATE INDEX ix_products_created_at_id ON products (created_at DESC, id DESC);
```

**Purpose:** Serves the primary browsing query (no category filter). PostgreSQL can:
1. Seek directly to the cursor position in the B-tree
2. Scan forward to collect `LIMIT` rows
3. Return results without a sort step (index is pre-sorted)

### Index 2: `(category, created_at DESC, id DESC)`

```sql
CREATE INDEX ix_products_category_created_at_id ON products (category, created_at DESC, id DESC);
```

**Purpose:** Serves category-filtered queries. PostgreSQL:
1. Descends the B-tree to the `category = 'Electronics'` subtree
2. Seeks to the cursor position within that subtree
3. Scans forward — no sort, no filter scan

Without this index, PostgreSQL would have to scan the entire `created_at` index and discard non-matching categories.

## Scalability Considerations

- **200K → 2M products**: Keyset pagination remains O(log n). No query changes needed.
- **High write throughput**: Since cursors reference immutable `(created_at, id)`, concurrent inserts don't invalidate existing cursors.
- **Connection pooling**: SQLAlchemy pool (10 + 20 overflow) handles concurrent API requests. For higher load, add a PgBouncer layer.
- **Read replicas**: The read-only browsing queries can be directed to Supabase read replicas without any code changes — just add a second engine.
- **Caching**: Category list and first page can be cached with a short TTL since they change infrequently.
