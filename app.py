from flask import Flask, request, jsonify
import base58
import nacl.signing
import nacl.encoding
from solana.rpc.api import Client
from solders.pubkey import Pubkey
import config
import requests
import json
import time
import pylibmc

app = Flask(__name__)
client = Client(config.solana_rpc)

# Initialize memcached client
try:
    mc = pylibmc.Client([config.memcached_server], binary=True)
except Exception as e:
    print(f"Warning: Could not connect to memcached: {e}")
    mc = None


def get_token_balance(address: str, token_mint: str) -> float:
    """Get token balance for a specific token mint."""
    try:
        # Use the RPC API directly for token accounts
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                address,
                {
                    "mint": token_mint
                },
                {
                    "encoding": "jsonParsed"
                }
            ]
        }
        
        # Add retry logic for rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            response = requests.post(
                config.solana_rpc,
                json=payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            # Check if request was successful
            if response.status_code != 200:
                if attempt < max_retries - 1:
                    print(f"Request failed (attempt {attempt + 1}), retrying...")
                    time.sleep(2)
                    continue
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            data = response.json()
            
            # Check for RPC errors
            if "error" in data:
                error_info = data["error"]
                if attempt < max_retries - 1:
                    error_msg = error_info.get('message', 'Unknown error')
                    print(f"RPC error (attempt {attempt + 1}): {error_msg}")
                    time.sleep(2)
                    continue
                else:
                    error_msg = error_info.get('message', 'Unknown error')
                    raise Exception(f"RPC Error: {error_msg}")
            
            # Successfully got response
            if "result" in data and data["result"]["value"]:
                total_balance = 0.0
                for account in data["result"]["value"]:
                    account_data = account["account"]["data"]["parsed"]
                    parsed_info = account_data["info"]
                    token_amount = parsed_info["tokenAmount"]
                    ui_amount = token_amount["uiAmount"]
                    balance = float(ui_amount) if ui_amount else 0.0
                    total_balance += balance
                return total_balance
            
            # No token accounts found (this is normal, not an error)
            return 0.0
        
        # If we get here, all retries failed
        raise Exception("All retry attempts failed")
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error getting token balance: {str(e)}")
    except Exception as e:
        raise Exception(f"Error getting token balance: {str(e)}")


@app.route('/verify_signature', methods=['POST'])
def verify_signature():
    data = request.json
    print(f"Received data for signature verification: {data}")
    try:
        # Decode the public key (should be Base58)
        public_key_bytes = base58.b58decode(data['public_key'])
        
        # Try to decode signature as hex first, then Base58
        signature_str = data['signature']
        try:
            # Check if it's hex (128 chars = 64 bytes when hex decoded)
            hex_chars = '0123456789abcdefABCDEF'
            if (len(signature_str) == 128 and
                    all(c in hex_chars for c in signature_str)):
                signature_bytes = bytes.fromhex(signature_str)
            else:
                # Try Base58 decoding
                signature_bytes = base58.b58decode(signature_str)
        except Exception:
            # If neither works, try the other format
            try:
                signature_bytes = bytes.fromhex(signature_str)
            except Exception:
                signature_bytes = base58.b58decode(signature_str)
        
        message_bytes = data['message'].encode('utf-8')

        # Create a verify key object
        verify_key = nacl.signing.VerifyKey(public_key_bytes)

        # Verify the signature
        verify_key.verify(message_bytes, signature_bytes)
        return jsonify({'valid': True})
    except Exception as e:
        print(f"Error verifying signature: {e}")
        return jsonify({'valid': False})


@app.route('/get_balance', methods=['POST'])
def get_balance():
    data = request.json
    public_key_str = data['public_key']
    
    # Check cache first
    cache_key = f"sol:{public_key_str}"
    if mc:
        try:
            cached_result = mc.get(cache_key)
            if cached_result:
                return jsonify(cached_result)
        except Exception as e:
            print(f"Cache read error: {e}")
    
    try:
        # Convert string to Pubkey object for SOL balance
        public_key = Pubkey.from_string(public_key_str)
    except Exception:
        return jsonify({'error': 'Invalid public key format'}), 400

    # Get SOL balance
    try:
        balance_response = client.get_balance(public_key)
        sol_balance = balance_response.value / 1e9  # Convert lamports to SOL
    except Exception as e:
        return jsonify({'error': f'Failed to get SOL balance: {str(e)}'}), 500

    # Get V2EX token balance using the working implementation
    v2ex_mint = "9raUVuzeWUk53co63M4WXLWPWE4Xc6Lpn7RS9dnkpump"
    try:
        v2ex_balance = get_token_balance(public_key_str, v2ex_mint)
    except Exception as e:
        print(f"Error getting V2EX balance: {str(e)}")
        v2ex_balance = 0

    result = {
        'sol_balance': sol_balance,
        'v2ex_balance': v2ex_balance
    }
    
    # Cache the result for 15 seconds
    if mc:
        try:
            mc.set(cache_key, result, time=15)
        except Exception as e:
            print(f"Cache write error: {e}")

    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=20251, debug=True)
