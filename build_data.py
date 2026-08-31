#!/usr/bin/env python3
import urllib.request, urllib.error, gzip, json, hashlib, re, xml.etree.ElementTree as ET
from datetime import datetime, timezone

CURATED = [
  {"title":"GitHub Student Developer Pack","provider":"GitHub","category":"Developer","duration":"2 tahun","price":"$0","eligibility":"Student verified","url":"https://education.github.com/pack","desc":"Copilot Pro + 100+ tools (JetBrains, Canva, Namecheap) gratis untuk student terverifikasi.","tags":["student","developer","copilot"]},
  {"title":"JetBrains All Products Pack","provider":"JetBrains","category":"Developer","duration":"1 tahun (renew)","price":"$0","eligibility":"Student","url":"https://www.jetbrains.com/community/education/#students","desc":"IntelliJ, PyCharm Pro, WebStorm dll gratis untuk student.","tags":["student","ide"]},
  {"title":"Perplexity Pro","provider":"Perplexity","category":"AI","duration":"12 bulan","price":"$0","eligibility":"Student (.edu)","url":"https://www.perplexity.ai/student","desc":"Pro search + GPT-4o + Claude gratis 1 tahun untuk student (promo US, cek eligibility).","tags":["ai","student"]},
  {"title":"Google Gemini Advanced (Google One AI Premium)","provider":"Google","category":"AI","duration":"12 bulan","price":"$0","eligibility":"Student US 18+","url":"https://gemini.google/students/","desc":"Gemini Advanced + 2TB Drive gratis 1 tahun untuk student US. Butuh .edu verification.","tags":["ai","student","google"]},
  {"title":"Cursor Pro","provider":"Cursor","category":"AI","duration":"12 bulan","price":"$0","eligibility":"Student","url":"https://cursor.sh/students","desc":"AI code editor Pro gratis 1 tahun untuk student verified.","tags":["ai","developer","student"]},
  {"title":"Notion Plus + AI","provider":"Notion","category":"Productivity","duration":"Gratis selama student","price":"$0","eligibility":"Student (.edu)","url":"https://www.notion.com/product/notion-for-education","desc":"Notion Plus + Notion AI gratis untuk student & educator.","tags":["student","productivity"]},
  {"title":"Figma Education","provider":"Figma","category":"Design","duration":"Gratis selama student","price":"$0","eligibility":"Student","url":"https://www.figma.com/education/","desc":"Figma Professional + FigJam gratis untuk student.","tags":["student","design"]},
  {"title":"Canva Pro for Education","provider":"Canva","category":"Design","duration":"Gratis selama student","price":"$0","eligibility":"Student/Educator","url":"https://www.canva.com/education/","desc":"Canva Pro gratis untuk student & guru (K-12 & univ tertentu).","tags":["student","design"]},
  {"title":"Adobe Creative Cloud","provider":"Adobe","category":"Editing","duration":"7 hari trial + diskon 60%","price":"~Rp 120rb/bln","eligibility":"Student trial umum","url":"https://www.adobe.com/creativecloud/buy/students.html","desc":"Photoshop, Premiere, After Effects. Trial 7 hari, lalu harga student ~60% off.","tags":["editing","student","adobe"]},
  {"title":"CapCut Pro","provider":"CapCut","category":"Editing","duration":"7 hari trial","price":"$0 trial","eligibility":"Umum","url":"https://www.capcut.com/","desc":"Video editor Pro trial 7 hari. Banyak fitur tetap free.","tags":["editing","video"]},
  {"title":"DaVinci Resolve Studio","provider":"Blackmagic","category":"Editing","duration":"Gratis (free version)","price":"$0","eligibility":"Umum","url":"https://www.blackmagicdesign.com/products/davinciresolve","desc":"Versi free sudah super lengkap untuk editing & color grading.","tags":["editing","video"]},
  {"title":"Microsoft 365 Education","provider":"Microsoft","category":"Productivity","duration":"Gratis selama student","price":"$0","eligibility":"Student","url":"https://education.microsoft.com/","desc":"Word, Excel, PowerPoint, Teams + 1TB OneDrive gratis.","tags":["student","office"]},
  {"title":"Autodesk Education","provider":"Autodesk","category":"Design","duration":"1 tahun","price":"$0","eligibility":"Student","url":"https://www.autodesk.com/education/edu-software/overview","desc":"AutoCAD, Maya, Revit gratis 1 tahun untuk student.","tags":["student","design","3d"]},
  {"title":"Apple Music Student","provider":"Apple","category":"Music","duration":"1 bulan trial + 50% off","price":"Rp 35rb/bln","eligibility":"Student","url":"https://www.apple.com/apple-music/","desc":"Apple Music + Apple TV+ gratis untuk student.","tags":["music","student"]},
  {"title":"Spotify Premium Student","provider":"Spotify","category":"Music","duration":"1 bulan trial + 50% off","price":"~Rp 27rb/bln","eligibility":"Student","url":"https://www.spotify.com/student/","desc":"Premium + Hulu (US) / diskon 50% di ID.","tags":["music","student"]},
  {"title":"YouTube Premium Student","provider":"Google","category":"Music","duration":"1 bulan trial + diskon","price":"~Rp 35rb/bln","eligibility":"Student","url":"https://www.youtube.com/premium/student","desc":"YouTube Premium diskon student + trial 1 bulan.","tags":["music","student"]},
  {"title":"GitHub Copilot Free Trial","provider":"GitHub","category":"Developer","duration":"30 hari","price":"$0 trial","eligibility":"Umum","url":"https://github.com/features/copilot","desc":"Copilot trial 30 hari, gratis selamanya jika student via pack.","tags":["ai","developer"]},
  {"title":"ChatGPT Plus Trial","provider":"OpenAI","category":"AI","duration":"— (promo musiman)","price":"$20/bln normal","eligibility":"Umum","url":"https://openai.com/chatgpt/pricing","desc":"Tidak ada trial permanen, tapi sering ada promo bundle. Free tier tetap ada.","tags":["ai"]},
  {"title":"Claude Pro Trial","provider":"Anthropic","category":"AI","duration":"7 hari (via app)","price":"$20/bln","eligibility":"Umum","url":"https://claude.ai/","desc":"Claude Pro kadang kasih trial 7 hari via mobile subscription.","tags":["ai"]},
  {"title":"Vercel Pro Trial","provider":"Vercel","category":"Developer","duration":"14 hari","price":"$0 trial","eligibility":"Umum","url":"https://vercel.com/pricing","desc":"Hobby free selamanya, Pro trial 14 hari.","tags":["developer"]},
  {"title":"Framer Pro Trial","provider":"Framer","category":"Design","duration":"14 hari","price":"$0 trial","eligibility":"Umum","url":"https://www.framer.com/pricing","desc":"Website builder trial 14 hari.","tags":["design"]},
  {"title":"Notion AI Trial","provider":"Notion","category":"AI","duration":"Gratis terbatas","price":"$0","eligibility":"Umum","url":"https://www.notion.com/pricing","desc":"AI trial dengan limit, gratis penuh jika student.","tags":["ai","productivity"]},
  {"title":"Office 365 Family Trial","provider":"Microsoft","category":"Productivity","duration":"1 bulan","price":"$0 trial","eligibility":"Umum","url":"https://www.microsoft.com/microsoft-365/buy/compare-all-microsoft-365-products","desc":"Family/Personal 1 bulan trial.","tags":["office"]},
  {"title":"Grammarly Premium","provider":"Grammarly","category":"Productivity","duration":"7 hari trial","price":"$0 trial","eligibility":"Umum","url":"https://www.grammarly.com/","desc":"Writing assistant premium trial 7 hari.","tags":["productivity","ai"]},
  {"title":"Coursera Plus Trial","provider":"Coursera","category":"Education","duration":"7 hari","price":"$0 trial","eligibility":"Umum","url":"https://www.coursera.org/courseraplus","desc":"7 hari trial akses 7000+ course.","tags":["education"]},
]

FEEDS = [
  "https://dev.to/feed/tag/free",
  "https://dev.to/feed/tag/student",
  "https://blog.google/technology/developers/rss/",
  "https://www.theverge.com/rss/index.xml",
  "https://feeds.feedburner.com/TechCrunch/",
]

KEYWORDS = ["free","trial","student","discount","promo","gratis","pro free","education","giveaway","deal","offer","coupon"]

def fetch_feed(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 FreeTrialTracker/1.0","Accept":"*/*"})
        resp = urllib.request.urlopen(req, timeout=20)
        data = resp.read()
        if resp.headers.get('Content-Encoding')=='gzip':
            data = gzip.decompress(data)
        return data
    except Exception as e:
        print("feed fail "+url+" : "+str(e))
        return None

def parse_feed(data):
    items=[]
    try:
        root = ET.fromstring(data)
    except: return items
    # detect RSS vs Atom
    # RSS: channel/item
    for item in root.findall(".//item"):
        t = item.findtext("title") or ""
        link = item.findtext("link") or ""
        desc = item.findtext("description") or ""
        if not t or not link: continue
        items.append((t.strip(), link.strip(), re.sub(r'<[^>]+>','',desc)[:200]))
    # Atom
    ns="{http://www.w3.org/2005/Atom}"
    for e in root.findall(".//"+ns+"entry"):
        t = e.findtext(ns+"title") or ""
        link_el = e.find(ns+"link")
        link = link_el.get("href") if link_el is not None else ""
        summ = e.findtext(ns+"summary") or e.findtext(ns+"content") or ""
        if not t or not link: continue
        items.append((t.strip(), link.strip(), re.sub(r'<[^>]+>','',summ)[:200]))
    return items

def is_relevant(title):
    tl = title.lower()
    if len(tl) < 12: return False
    return any(k in tl for k in KEYWORDS)

def stable_id(url):
    return hashlib.md5(url.encode()).hexdigest()[:12]

def build():
    curated_list=[]
    seen=set()
    for c in CURATED:
        cid = stable_id(c["url"])
        curated_list.append({
            "id": cid,
            "title": c["title"],
            "provider": c["provider"],
            "category": c["category"],
            "duration": c["duration"],
            "price": c["price"],
            "eligibility": c["eligibility"],
            "url": c["url"],
            "desc": c["desc"],
            "tags": c["tags"],
            "source":"curated"
        })
        seen.add(c["url"])

    from_feeds=[]
    for feed_url in FEEDS:
        data = fetch_feed(feed_url)
        if not data: continue
        for t, link, desc in parse_feed(data):
            if not is_relevant(t): continue
            if link in seen: continue
            if len(from_feeds) >= 40: break
            seen.add(link)
            from_feeds.append({
                "id": stable_id(link),
                "title": t,
                "provider": link.split("/")[2] if "://" in link else "News",
                "category": "News/Deal",
                "duration": "—",
                "price": "—",
                "eligibility": "Umum",
                "url": link,
                "desc": desc,
                "tags": ["news"],
                "source":"feed"
            })

    all_items = curated_list + from_feeds
    out = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(all_items),
        "curated": len(curated_list),
        "from_feeds": len(from_feeds),
        "offers": all_items
    }
    # compat alias
    out["courses"] = all_items
    with open("data.json","w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("Wrote data.json total="+str(len(all_items))+" curated="+str(len(curated_list))+" feeds="+str(len(from_feeds)))
    assert out["total"] >= len(CURATED), "curated missing"
    assert all("id" in x and "url" in x for x in all_items), "schema broken"
    assert len(set(x["id"] for x in all_items))==len(all_items), "duplicate id"

if __name__=="__main__":
    build()
