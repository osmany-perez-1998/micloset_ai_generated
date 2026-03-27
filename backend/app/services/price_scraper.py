"""
Price scraper — four-layer strategy per URL:

  Layer 1 — JSON-LD structured data  (works for most modern stores)
  Layer 2 — Open Graph / meta price tags
  Layer 3 — Store-specific CSS selectors
  Layer 4 — OpenAI extraction from raw HTML (last resort)

Returns a PriceResult with the found price, currency, and which layer
succeeded (or a failed result so the rep can enter manually).
"""

import re
import json
import httpx
from dataclasses import dataclass
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from app.core.config import settings


# ─── Result type ─────────────────────────────────────────────────────────────

@dataclass
class PriceResult:
    url: str
    price: float | None
    currency: str | None          # e.g. "USD"
    store: str | None
    method: str | None            # which layer succeeded
    raw_text: str | None          # original string before parsing (for debug)
    needs_manual: bool            # True if all layers failed


# ─── HTTP client ─────────────────────────────────────────────────────────────

# Realistic browser headers — reduces bot detection
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
}

_TIMEOUT = 15.0


async def _fetch_html(url: str) -> str | None:
    async with httpx.AsyncClient(headers=_HEADERS, timeout=_TIMEOUT, follow_redirects=True) as client:
        try:
            res = await client.get(url)
            if res.status_code == 200:
                return res.text
        except Exception:
            pass
    return None


# ─── Price string parser ──────────────────────────────────────────────────────

def _parse_price(raw: str) -> float | None:
    """Extract numeric price from strings like '$29.99', '29,99', '1,299.00'."""
    raw = raw.strip()
    # Remove currency symbols and letters
    cleaned = re.sub(r"[^\d.,]", "", raw)
    if not cleaned:
        return None
    # Handle European comma-decimal: '29,99' → '29.99'
    if re.match(r"^\d{1,3}(?:\.\d{3})*,\d{2}$", cleaned):
        cleaned = cleaned.replace(".", "").replace(",", ".")
    else:
        cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


# ─── Layer 1: JSON-LD ─────────────────────────────────────────────────────────

def _extract_jsonld(soup: BeautifulSoup) -> tuple[float, str] | None:
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (json.JSONDecodeError, TypeError):
            continue

        # Handle list of schemas
        if isinstance(data, list):
            for item in data:
                result = _parse_offer(item)
                if result:
                    return result
        else:
            result = _parse_offer(data)
            if result:
                return result
    return None


def _parse_offer(data: dict) -> tuple[float, str] | None:
    if not isinstance(data, dict):
        return None

    # Direct Product schema
    offers = data.get("offers") or data.get("Offers")
    if offers:
        if isinstance(offers, list):
            offers = offers[0]
        price = offers.get("price") or offers.get("lowPrice")
        currency = offers.get("priceCurrency", "USD")
        if price is not None:
            parsed = _parse_price(str(price))
            if parsed:
                return parsed, currency

    # Sometimes price is directly on the schema
    price = data.get("price")
    if price is not None:
        parsed = _parse_price(str(price))
        if parsed:
            return parsed, data.get("priceCurrency", "USD")

    return None


# ─── Layer 2: Meta / Open Graph tags ─────────────────────────────────────────

def _extract_meta(soup: BeautifulSoup) -> tuple[float, str] | None:
    selectors = [
        {"property": "product:price:amount"},
        {"name": "twitter:data1"},       # some stores put price here
        {"property": "og:price:amount"},
        {"itemprop": "price"},
        {"name": "price"},
    ]
    currency_meta = (
        soup.find("meta", {"property": "product:price:currency"})
        or soup.find("meta", {"property": "og:price:currency"})
    )
    currency = currency_meta["content"] if currency_meta else "USD"

    for attrs in selectors:
        tag = soup.find("meta", attrs)
        if tag:
            content = tag.get("content") or tag.get("data-content")
            if content:
                parsed = _parse_price(str(content))
                if parsed:
                    return parsed, currency

    # <span itemprop="price" content="29.99">
    span = soup.find(attrs={"itemprop": "price"})
    if span:
        content = span.get("content") or span.get_text()
        if content:
            parsed = _parse_price(str(content))
            if parsed:
                return parsed, "USD"

    return None


# ─── Layer 3: Store-specific CSS selectors ────────────────────────────────────

_STORE_SELECTORS: dict[str, list[str]] = {
    "amazon.com": [
        "span.a-price[data-a-size='xl'] span.a-price-whole",
        "#corePrice_feature_div span.a-price-whole",
        "#price_inside_buybox",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "span.a-price.a-text-price.a-size-medium span.a-offscreen",
        ".a-price .a-offscreen",
    ],
    "shein.com": [
        "div.product-intro__price-del",
        "div.product-intro__price .product-price__sale-price",
        ".original-price",
        ".price-content .price",
        "[class*='ProductPrice'] [class*='price']",
    ],
    "temu.com": [
        "div._3OGW_YL span",
        "[class*='Price'] [class*='current']",
        "[data-type='price']",
        "div.price-item",
    ],
    "walmart.com": [
        "[itemprop='price']",
        "span[class*='price-characteristic']",
        "[data-automation='buybox-price']",
        ".price-main .visuallyhidden",
        "[class*='PriceDisplay']",
    ],
    "target.com": [
        "[data-test='product-price']",
        "span[class*='styles__CurrentPriceStyle']",
    ],
    "adidas.com": [
        "div.gl-price-item--sale",
        "div.gl-price-item",
        "[class*='product-price']",
    ],
    "zara.com": [
        "span.money-amount__main",
        "[class*='price__amount']",
    ],
    "ebay.com": [
        "span#prcIsum",
        "div.x-price-primary span.ux-textspans",
        "span[itemprop='price']",
    ],
    "aliexpress.com": [
        "span.product-price-value",
        "[class*='uniform-banner-box-price']",
        ".product-price-current",
    ],
    "forever21.com": [
        "span[class*='product-price']",
    ],
    "macys.com": [
        "div.product-price span.medium",
        "[class*='regular-price']",
    ],
    "nordstrom.com": [
        "span[class*='CurrentPricestyle']",
        "[class*='Price'] span",
    ],
    "asos.com": [
        "span[class*='current-price']",
        "[data-testid='current-price']",
    ],
}


def _detect_store(url: str) -> str | None:
    host = urlparse(url).hostname or ""
    for store_key in _STORE_SELECTORS:
        if store_key in host:
            return store_key
    return None


def _extract_css(soup: BeautifulSoup, url: str) -> tuple[float, str] | None:
    store = _detect_store(url)
    if not store:
        return None
    for selector in _STORE_SELECTORS[store]:
        try:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(strip=True) or el.get("content", "")
                parsed = _parse_price(text)
                if parsed and parsed > 0:
                    return parsed, "USD"
        except Exception:
            continue
    return None


# ─── Layer 4: OpenAI extraction ──────────────────────────────────────────────

async def _extract_openai(html: str, url: str) -> tuple[float, str] | None:
    if not settings.OPENAI_API_KEY:
        return None
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Feed a condensed version — keep head + first 4000 chars of body
        soup = BeautifulSoup(html, "lxml")
        body_text = soup.get_text(separator=" ", strip=True)[:4000]

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You extract product prices from web page text. "
                        "Respond ONLY with a JSON object: "
                        '{"price": <number or null>, "currency": "<ISO 4217 code>"} '
                        "If no price is found respond with {\"price\": null, \"currency\": null}."
                    ),
                },
                {
                    "role": "user",
                    "content": f"URL: {url}\n\nPage text:\n{body_text}",
                },
            ],
            temperature=0,
            max_tokens=50,
            response_format={"type": "json_object"},
        )

        data = json.loads(response.choices[0].message.content)
        price = data.get("price")
        currency = data.get("currency") or "USD"
        if price is not None:
            return float(price), currency
    except Exception:
        pass
    return None


# ─── Public entry point ───────────────────────────────────────────────────────

async def fetch_price(url: str) -> PriceResult:
    store = _detect_store(url)
    html = await _fetch_html(url)

    if not html:
        return PriceResult(
            url=url, price=None, currency=None, store=store,
            method=None, raw_text=None, needs_manual=True,
        )

    soup = BeautifulSoup(html, "lxml")

    # Layer 1 — JSON-LD
    result = _extract_jsonld(soup)
    if result:
        return PriceResult(url=url, price=result[0], currency=result[1],
                           store=store, method="json-ld", raw_text=None, needs_manual=False)

    # Layer 2 — meta tags
    result = _extract_meta(soup)
    if result:
        return PriceResult(url=url, price=result[0], currency=result[1],
                           store=store, method="meta", raw_text=None, needs_manual=False)

    # Layer 3 — CSS selectors
    result = _extract_css(soup, url)
    if result:
        return PriceResult(url=url, price=result[0], currency=result[1],
                           store=store, method="css", raw_text=None, needs_manual=False)

    # Layer 4 — OpenAI
    result = await _extract_openai(html, url)
    if result:
        return PriceResult(url=url, price=result[0], currency=result[1],
                           store=store, method="openai", raw_text=None, needs_manual=False)

    return PriceResult(
        url=url, price=None, currency=None, store=store,
        method=None, raw_text=None, needs_manual=True,
    )
