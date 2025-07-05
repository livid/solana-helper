Simple Python 3.12 Flask app provides several endpoints for Solana:

## /verify_signature

Input a JSON dictionary with the following keys:

- message
- signature
- public_key

Output will be a JSON dictionary with a single key:

- valid: boolean indicating if the signature is valid

## /get_balance

Input a JSON dictionary with the following keys:

- public_key: the public key of the Solana account

Output will be a JSON dictionary with a single key:

- balance: the balance of the Solana account
- v2ex_balance: the balance of the V2EX coin (CA: 9raUVuzeWUk53co63M4WXLWPWE4Xc6Lpn7RS9dnkpump)

---

## How To Test

The server is already running on port 20251.