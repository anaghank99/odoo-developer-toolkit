# Odoo XPath Lab

A small FastAPI web tool for validating Odoo XML, testing XPath expressions,
showing matched nodes and simulating Odoo view inheritance positions.

## Features

- XML syntax validation
- XPath syntax validation
- Match count and matched-node preview
- `inside`, `before`, `after`, `replace`, and `attributes`
- Odoo-specific XPath warnings
- Safe XML parsing
- Browser interface
- Automated tests
- Docker and Render configuration

## Local installation

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Browser test

Click **Load example**, then click **Test XPath**.

The XPath:

```xml
//field[@name='partner_id']
```

with position `after` and this new XML:

```xml
<field name="customer_reference"/>
```

should generate XML where `customer_reference` appears immediately after
`partner_id`.

## Test attributes

Use:

```xml
//field[@name='partner_id']
```

Select `attributes` and paste:

```xml
<attribute name="string">Customer</attribute>
<attribute name="required">1</attribute>
```

## Automated tests

```bash
pytest -v
```

## API test with curl

```bash
curl -X POST http://127.0.0.1:8000/api/test-xpath   -H "Content-Type: application/json"   -d '{
    "base_xml": "<form><sheet><field name=\"partner_id\"/></sheet></form>",
    "xpath_expression": "//field[@name=\"partner_id\"]",
    "position": "after",
    "inherited_xml": "<field name=\"customer_reference\"/>"
  }'
```

## Docker

Build:

```bash
docker build -t odoo-xpath-lab .
```

Run:

```bash
docker run --rm -p 8000:8000 odoo-xpath-lab
```

Then open:

```text
http://127.0.0.1:8000
```

## Render deployment

1. Push this project to GitHub.
2. Sign in to Render.
3. Create a new Web Service.
4. Select the GitHub repository.
5. Build command:

```bash
pip install -r requirements.txt
```

6. Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The included `render.yaml` can also be used for a Blueprint deployment.

## Important limitation

This tool simulates XPath changes against supplied XML. It does not reproduce
the complete Odoo view-resolution process involving multiple inherited views,
priority, security groups, Studio customizations, or version-specific metadata.
