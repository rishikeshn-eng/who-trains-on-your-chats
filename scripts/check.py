"""Re-read every provider's policy page and check that each quoted sentence is still there, word for word.
Writes docs/data/status.json. A quote that has gone missing means the policy wording changed and the entry needs a human look."""
import json, re, hashlib, datetime as dt, concurrent.futures as cf
from pathlib import Path
import requests, trafilatura
ROOT = Path(__file__).resolve().parent.parent
H = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36", "Accept-Language": "en-US,en;q=0.9"}

def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip().lower()

def page(item):
    key, url = item
    for _ in range(3):
        try:
            r = requests.get(url, headers=H, timeout=30)
            if r.status_code == 200:
                r.encoding = r.apparent_encoding or r.encoding
                text = trafilatura.extract(r.text, include_comments=False) or ""
                if len(text) > 300: return key, text
        except Exception:
            pass
    return key, None

def main():
    cfg = json.loads((ROOT / "providers.json").read_text())
    today = dt.datetime.now(dt.timezone.utc)
    out_path = ROOT / "docs" / "data" / "status.json"
    old = json.loads(out_path.read_text()) if out_path.exists() else {"pages": {}, "log": []}
    with cf.ThreadPoolExecutor(6) as ex:
        texts = dict(ex.map(page, cfg["sources"].items()))
    pages, log = {}, old.get("log", [])
    for key, url in cfg["sources"].items():
        t = texts[key]; prev = old["pages"].get(key, {})
        h = hashlib.sha256(norm(t).encode()).hexdigest()[:16] if t else None
        changed = prev.get("changed")
        if t and prev.get("hash") and prev["hash"] != h:
            changed = today.strftime("%Y-%m-%d"); log.insert(0, {"day": changed, "page": key, "url": url, "what": "The text of this page changed."})
        pages[key] = {"url": url, "read": bool(t), "hash": h or prev.get("hash"), "changed": changed, "words": len(t.split()) if t else 0}
    bad = 0
    for p in cfg["providers"]:
        for field in ("trains", "switch", "kept", "private", "catch"):
            c = p.get(field)
            if not c: continue
            t = texts.get(c["src"])
            c["found"] = None if t is None else norm(c["quote"]) in norm(t)
            c["url"] = cfg["sources"][c["src"]]
            if c["found"] is False:
                bad += 1
                entry = {"day": today.strftime("%Y-%m-%d"), "page": c["src"], "url": c["url"], "what": f"{p['app']}: a quoted sentence is no longer on the page ({field})."}
                if entry["what"] not in [x["what"] for x in log if x["day"] == entry["day"]]: log.insert(0, entry)
    out = {"checked": today.isoformat(), "providers": cfg["providers"], "unread": cfg["unread"], "pages": pages, "log": log[:200]}
    out_path.parent.mkdir(parents=True, exist_ok=True); out_path.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    unread = [k for k, v in pages.items() if not v["read"]]
    total = sum(1 for p in cfg["providers"] for f in ("trains", "switch", "kept", "private", "catch") if p.get(f))
    print(f"{total} quotes checked, {bad} missing; pages that could not be read: {unread or 'none'}")
    for p in cfg["providers"]:
        for f in ("trains", "switch", "kept", "private", "catch"):
            if p.get(f) and p[f]["found"] is not True: print("  NOT FOUND:", p["app"], f, "|", p[f]["quote"][:70])

if __name__ == "__main__":
    main()
