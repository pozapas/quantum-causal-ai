"""Discovery helper for the media unit (candidates only; nothing here is trusted).

Usage:
  python scripts/discover_media.py yt  OUT.json "query 1" "query 2" ...
  python scripts/discover_media.py pod OUT.json "query 1" ...
YouTube: fetches the public results page and parses videoId/title/channel from ytInitialData.
Podcasts: iTunes Search API (entity=podcastEpisode).
Output is a candidate list that must still pass scripts/verify_media.py.
"""
import json, re, sys, time, urllib.parse
import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}


def _walk(o, out):
    if isinstance(o, dict):
        if "videoRenderer" in o:
            v = o["videoRenderer"]
            def txt(x):
                if not x: return ""
                if "simpleText" in x: return x["simpleText"]
                return "".join(r.get("text", "") for r in x.get("runs", []))
            out.append({"id": v.get("videoId"), "title": txt(v.get("title")),
                        "channel": txt(v.get("ownerText") or v.get("longBylineText")),
                        "length": txt(v.get("lengthText")), "published": txt(v.get("publishedTimeText")),
                        "views": txt(v.get("viewCountText"))})
        for val in o.values():
            _walk(val, out)
    elif isinstance(o, list):
        for val in o:
            _walk(val, out)


def yt(query, n=12):
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
    r = requests.get(url, headers=UA, timeout=30)
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", r.text, re.S)
    out = []
    if m:
        _walk(json.loads(m.group(1)), out)
    return {"query": query, "status": r.status_code, "results": out[:n]}


def pod(query, n=25):
    url = "https://itunes.apple.com/search"
    r = requests.get(url, params={"term": query, "media": "podcast", "entity": "podcastEpisode", "limit": n},
                     headers=UA, timeout=30)
    res = []
    if r.status_code == 200:
        for it in r.json().get("results", []):
            res.append({k: it.get(k) for k in ("trackId", "trackName", "collectionName", "collectionId", "releaseDate",
                                               "trackViewUrl", "episodeUrl", "trackTimeMillis", "feedUrl")})
    return {"query": query, "status": r.status_code, "results": res}


if __name__ == "__main__":
    mode, outp, *qs = sys.argv[1:]
    fn = yt if mode == "yt" else pod
    allr = []
    for q in qs:
        allr.append(fn(q))
        time.sleep(1.5)
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(allr, f, indent=1, ensure_ascii=False)
    for blk in allr:
        print("##", blk["query"], blk["status"])
        for x in blk["results"]:
            if mode == "yt":
                print(f"  {x['id']} | {x['title'][:90]} | {x['channel']} | {x['length']} | {x['published']}")
            else:
                print(f"  {x['trackId']} | {x['trackName'][:90]} | {x['collectionName']} | {(x['releaseDate'] or '')[:10]}")
