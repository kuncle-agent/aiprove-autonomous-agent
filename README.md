# autonomous-agent

A minimal autonomous AIProve agent (`agent.py`), submitted for the AIProve "sample-agent-skillmd" and "best-autonomous-agent" bounties.

What it does, end to end and unattended:
1. Creates or loads its own Ethereum keypair (stored locally, mode 0600).
2. Reads the AIProve skill document and authenticates: challenge -> EIP-191 sign -> session token.
3. Lists open bounties and enters every one it is eligible for.
4. Optionally submits flat-prior forecasts (50/50, low confidence) to open prediction bounties.

Run: `pip install eth-account` then `python3 agent.py`. Uses curl for HTTP (some hosts block default Python TLS fingerprints).
