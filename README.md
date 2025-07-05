# Solana Helper Flask API

A simple Flask app providing Solana blockchain utilities.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
python app.py
```

The app will start on `http://localhost:20251`

## Endpoints

### POST /verify_signature

Verify a Solana signature.

**Request:**

```json
{
    "message": "Hello, Solana!",
    "signature": "base58_encoded_signature",
    "public_key": "base58_encoded_public_key"
}
```

**Response:**

```json
{
    "valid": true
}
```

**Curl Example:**

```bash
curl -X POST http://localhost:20251/verify_signature \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, Solana!",
    "signature": "your_hex_encoded_signature_here",
    "public_key": "your_base58_encoded_public_key_here"
  }'
```

### POST /get_balance

Get SOL balance and V2EX token balance for a Solana account.

**Request:**

```json
{
    "public_key": "base58_encoded_public_key"
}
```

**Response:**

```json
{
    "sol_balance": 1.5,
    "v2ex_balance": 1000.0
}
```

**Curl Example:**

```bash
curl -X POST http://localhost:20251/get_balance \
  -H "Content-Type: application/json" \
  -d '{
    "public_key": "4JBz4tAKgAmxjDPHHi9HRLj14RsCQJyuCkCFKnpz7B9s"
  }'
```

## Configuration

The Solana RPC endpoint is configured in `config.py`. Update the `solana_rpc` variable to use your preferred RPC provider.

## Testing

Use the `test_api.py` script to test the endpoints:

```bash
python test_api.py
```

Make sure the Flask app is running before executing the test script.
