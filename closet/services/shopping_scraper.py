import re
import requests
from bs4 import BeautifulSoup
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}
TIMEOUT = 8
SITES = [
    {"name": "Outfitters", "kind": "shopify", "domain": "outfitters.com.pk"},
    {"name": "Sapphire", "kind": "shopify", "domain": "www.sapphireonline.pk"},
    {"name": "Chinyere", "kind": "shopify", "domain": "www.chinyere.pk"},
    {"name": "Breakout", "kind": "shopify", "domain": "www.breakout.com.pk"},
    {"name": "Lama", "kind": "shopify", "domain": "pk.lamaretail.com"},
    {"name": "Nishat Linen", "kind": "shopify", "domain": "nishatlinen.com"},
    {"name": "Diners", "kind": "shopify", "domain": "diners.com.pk"},
    {"name": "Uniworth", "kind": "shopify", "domain": "uniworthshop.com"},
    {"name": "Bata", "kind": "shopify", "domain": "www.bata.com.pk"},
    {"name": "Servis", "kind": "shopify", "domain": "servis.pk"},
    {"name": "Ndure", "kind": "shopify", "domain": "www.ndure.com"},
    {"name": "Hush Puppies", "kind": "shopify", "domain": "www.hushpuppies.com.pk"},
    {
        "name": "Daraz.pk",
        "kind": "html",
        "search_url": "https://www.daraz.pk/catalog/?q={query}",
        "item_attrs": {"data-qa-locator": "product-item"},
    },
]
def _build_query(sub_type, color):
    parts = [p for p in [color, sub_type] if p]
    return " ".join(parts).strip()

def _shopify_search(domain, query, limit=6):
    url = f"https://{domain}/search/suggest.json"
    params = {
        "q": query,
        "resources[type]": "product",
        "resources[limit]": limit,
        "resources[options][unavailable_products]": "last",
    }
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        products = data.get("resources", {}).get("results", {}).get("products", [])
        results = []
        for p in products:
            results.append({
                "title": p.get("title", "Untitled item"),
                "price": p.get("price", ""),
                "url": p.get("url", "/"),
                "image": (p.get("image") or "").replace("{width}", "400"),
            })
        return results
    except Exception:
        return []

def _daraz_scrape(query, limit=6):
    url = f"https://www.daraz.pk/catalog/?q={requests.utils.quote(query)}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.find_all("div", attrs={"data-qa-locator": "product-item"})
        results = []
        for item in items[:limit]:
            title_tag = item.find(["div", "span"], class_=re.compile("title", re.I))
            price_tag = item.find(["span", "div"], class_=re.compile("price", re.I))
            link_tag = item.find("a", href=True)
            img_tag = item.find("img")
            if not link_tag:
                continue
            href = link_tag["href"]
            if href.startswith("//"):
                href = "https:" + href
            results.append({
                "title": title_tag.get_text(strip=True) if title_tag else "Daraz item",
                "price": price_tag.get_text(strip=True) if price_tag else "",
                "url": href,
                "image": img_tag.get("src") or img_tag.get("data-src", "") if img_tag else "",
            })
        return results
    except Exception:
        return []

def search_products(sub_type, color, category=None, limit_per_site=4):
    query = _build_query(sub_type, color)
    output = []
    for site in SITES:
        if site["kind"] == "shopify":
            products = _shopify_search(site["domain"], query, limit=limit_per_site)
            search_url = f"https://{site['domain']}/search?q={requests.utils.quote(query)}"
            # Shopify returns relative URLs/images sometimes - normalize them.
            for p in products:
                if p["url"].startswith("/"):
                    p["url"] = f"https://{site['domain']}{p['url']}"
                if p["image"].startswith("//"):
                    p["image"] = "https:" + p["image"]
        else:  # html
            products = _daraz_scrape(query, limit=limit_per_site)
            search_url = site["search_url"].format(query=requests.utils.quote(query))
        output.append({
            "site": site["name"],
            "products": products,
            "search_url": search_url,
        })
    return output

COMMON_COMBOS = [
    ("shoes", "formal shoes", "black"),
    ("shoes", "formal shoes", "brown"),
    ("shoes", "sneakers", "white"),
    ("accessory", "belt", "black"),
    ("accessory", "belt", "brown"),
    ("accessory", "watch", "black"),
    ("pant", "formal trousers", "black"),
    ("pant", "jeans", "navy"),
    ("shirt", "formal shirt", "white"),
]

def find_wardrobe_gaps(all_items):
    owned = set()
    for item in all_items:
        color = (item.get("color_name") or "").lower()
        owned.add((item["category"], item["sub_type"].lower(), color))
    gaps = []
    for category, sub_type, color in COMMON_COMBOS:
        has_close_match = any(
            category == oc and sub_type == ost and color in oco
            for oc, ost, oco in owned
        )
        if not has_close_match:
            gaps.append({"category": category, "sub_type": sub_type, "color": color})
    return gaps