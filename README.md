# Product Browser

A FastAPI backend serving 200,000 products with offset-based numbered pagination.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure database
cp .env.example .env
# Edit .env with your PostgreSQL connection string

# 3. Seed the database (200,000 products)
python seed.py

# 4. Run the server
uvicorn app.main:app --reload

# 5. Open the UI
# http://localhost:8000
```

## Project Structure

```
project/
├── app/
│   ├── main.py        # FastAPI app, static file serving
│   ├── database.py    # SQLAlchemy engine and session
│   ├── models.py      # Product model with indexes
│   ├── schemas.py     # Pydantic response schemas
│   ├── routes.py      # API endpoints
│   └── services.py    # Offset pagination logic
├── static/
│   ├── index.html     # Frontend UI
│   └── app.js         # Vanilla JS client
├── seed.py            # Bulk data generator
├── requirements.txt
├── .env.example
├── README.md
└── DESIGN.md
```

## API Endpoints

### `GET /health`

```json
{ "status": "ok" }
```

### `GET /products`

Query parameters:

| Param      | Type   | Default | Description                    |
|------------|--------|---------|--------------------------------|
| `limit`    | int    | 20      | Products per page (1-100)      |
| `page`     | int    | 1       | Page number to fetch           |
| `category` | string | null    | Filter by category name        |

Response:

```json
{
  "products": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Premium Headphones 4521",
      "category": "Electronics",
      "price": 149.99,
      "created_at": "2025-08-15T10:30:00Z",
      "updated_at": "2025-09-01T14:00:00Z"
    }
  ],
  "total_count": 200000,
  "page": 1,
  "total_pages": 10000
}
```

### `GET /categories`

```json
["Automotive", "Books", "Clothing", ...]
```

### `GET /`

Serves the HTML frontend.

## API Usage Examples

```bash
# First page
curl http://localhost:8000/products?limit=20

# Next page (use page parameter)
curl "http://localhost:8000/products?limit=20&page=2"

# Filter by category
curl "http://localhost:8000/products?limit=20&category=Electronics"
```

## Database Setup

The application uses PostgreSQL (tested with Supabase). Tables and indexes are created automatically on first startup via `Base.metadata.create_all()`.

To reset the database:

```sql
DROP TABLE IF EXISTS products;
```

Then restart the server and re-run `python seed.py`.

## Deployment

1. Set `DATABASE_URL` as an environment variable
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

For production, use Gunicorn with Uvicorn workers:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
