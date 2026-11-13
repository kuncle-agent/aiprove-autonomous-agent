#!/usr/bin/env python3
"""A minimal autonomous AIProve agent.

Loop (no human in the loop):
  1. Load (or create) its own Ethereum keypair from ./agent.key
  2. Read https://aiprove.fun/skill.md so the rules come from the source
  3. Authenticate: GET /api/auth/challenge -> personal_sign -> POST /api/auth/verify
  4. List open bounties, enter every one it can
  5. For forecast bounties, submit a flat prior (answer "no", confidence 0.5)
     so the loop completes end to end; smarter forecasters can subclass.

Usage: python3 agent.py [--enter-all] [--submit-defaults]
Requires: eth-account (pip install eth-account). HTTP via curl because the
arena's CDN intermittently truncates Python's urllib responses.
"""
import json, os, subprocess, sys

BASE = "https://aiprove.fun"
KEY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent.key")

def http(method, path, token=None, body=None):
    cmd = ["curl", "-s", "--max-time", "30", "-X", method]
    if token: cmd += ["-H", f"Authorization: Bearer {token}"]
    if body is not None: cmd += ["-H", "content-type: application/json", "-d", json.dumps(body)]
    cmd.append(BASE + path)
    out = subprocess.run(cmd, capture_output=True, text=True)
    try: return json.loads(out.stdout)
    except Exception: return {"raw": out.stdout}

def get_or_create_account():
    from eth_account import Account
    if os.path.exists(KEY):
        return Account.from_key(open(KEY).read().strip())
    acct = Account.create()
    with open(KEY, "w") as f: f.write(acct.key.hex())
    os.chmod(KEY, 0o600)
    return acct

def login(acct):
    from eth_account.messages import encode_defunct
    ch = http("GET", f"/api/auth/challenge?address={acct.address}")
    sig = "0x" + acct.sign_message(encode_defunct(text=ch["challenge"])).signature.hex()
    sess = http("POST", "/api/auth/verify",
                body={"address": acct.address, "signature": sig, "challenge": ch["challenge"]})
    return sess["token"]

def main():
    enter_all = "--enter-all" in sys.argv
    submit_defaults = "--submit-defaults" in sys.argv
    skill = http("GET", "/skill.md")  # rules from the source (raw ok)
    acct = get_or_create_account()
    token = login(acct)
    me = http("GET", "/api/me", token)
    handle = (me.get("agent") or {}).get("handle") or "agent"
    print(f"logged in as {acct.address} handle={handle}")
    bounties = http("GET", "/api/bounties?status=open", token).get("bounties", [])
    print(f"{len(bounties)} open bounties")
    for b in bounties:
        slug = b["slug"]
        if enter_all:
            r = http("POST", f"/api/bounties/{slug}/enter", token, {"handle": handle})
            print("enter", slug, "->", "id" in r)
        if submit_defaults and b.get("cat") == "forecast":
            r = http("POST", f"/api/bounties/{slug}/submit", token,
                     {"prediction": {"answer": "no", "confidence": 0.5}, "handle": handle})
            print("submit", slug, "->", r.get("status"))

if __name__ == "__main__":
    main()
