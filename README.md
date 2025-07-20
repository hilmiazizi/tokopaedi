
# Tokopaedi - Python Library for Tokopedia E-Commerce Data Extraction
![PyPI](https://img.shields.io/pypi/v/tokopaedi) [![PyPI Downloads](https://static.pepy.tech/badge/tokopaedi)](https://pepy.tech/projects/tokopaedi) ![GitHub Repo stars](https://img.shields.io/github/stars/hilmiazizi/tokopaedi?style=social) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/hilmiazizi/tokopaedi/blob/main/LICENSE) ![GitHub forks](https://img.shields.io/github/forks/hilmiazizi/tokopaedi?style=social)

**Extract product data, reviews, and search results from Tokopedia with ease.**

Tokopaedi is a powerful Python library designed for scraping e-commerce data from Tokopedia, including product searches, detailed product information, and customer reviews. Ideal for developers, data analysts, and businesses looking to analyze Tokopedia's marketplace.


![Tokopaedi Runtime](image/runtime.png)

## Features
- **Product Search**: Search Tokopedia products by keyword with customizable filters (price, rating, condition, etc.).
- **Detailed Product Data**: Retrieve rich product details, including variants, pricing, stock, and media.
- **Customer Reviews**: Scrape product reviews with ratings, timestamps, and more.
- **Serializable Results**: Dataclass-based results with `.json()` for easy export to JSON or pandas DataFrames.
- **SearchResults Container**: Iterable and JSON-serializable container that supports enrich_details() and enrich_reviews() to automatically fetch product metadata and reviews for each item.


## Installation
Tokopaedi is available on PyPi: [https://pypi.org/project/tokopaedi/](https://pypi.org/project/tokopaedi/)

Install Tokopaedi via pip:

```bash
pip install tokopaedi
```

##  Quick Start
```python
from tokopaedi import search, SearchFilters, get_product, get_reviews
import json

filters = SearchFilters(
            bebas_ongkir_extra = True,
            pmin = 15000000,
            pmax = 25000000,
            rt = 4.5
        )

results = search("Asus Zenbook S14 32GB", max_result=10, debug=True, filters=filters)
results.enrich_details(debug=True)
results.enrich_reviews(max_result=50, debug=True)

with open('log.json','w') as f:
    f.write(json.dumps(results.json(), indent=4))
print(results.json())
```

## 📘 API Overview

### 🔍 `search(keyword: str, max_result: int = 100, filters: Optional[SearchFilters] = None, debug: bool = False) -> SearchResults`

Search for products from Tokopedia.

**Parameters:**

-   `keyword`: string keyword (e.g., `"logitech mouse"`).
    
-   `max_result`: Expected number of results to return.
    
-   `filters`: Optional `SearchFilters` instance to narrow search results.
    
-   `debug`: Show debug message if True
    

**Returns:**

-   A `SearchResults` instance (list-like object of `ProductSearchResult`), supporting `.json()` for easy export.
    

----------

### 📦 `get_product(product_id: Optional[Union[int, str]] = None, url: Optional[str] = None, debug: bool = False) -> ProductData`

Fetch detailed information for a given Tokopedia product.

**Parameters:**

- `product_id`: (Optional) The product ID returned from `search()`. If provided, this will take precedence over `url`.
- `url`: (Optional) The full product URL. Used only if `product_id` is not provided.
- `debug`: If `True`, prints debug output for troubleshooting.

> ⚠️ Either `product_id` or `url` must be provided. If both are given, `product_id` is used and `url` is ignored.

**Returns:**

- A `ProductData` instance containing detailed information such as product name, pricing, variants, media, stock, rating, etc.
- Supports `.json()` for easy serialization (e.g., to use with `pandas` or export as `.json`).

----------

### 🗣️ `get_reviews(product_id: Optional[Union[int, str]] = None, url: Optional[str] = None, max_count: int = 20, debug: bool = False) -> List[ProductReview]`

Scrape customer reviews for a given product.

**Parameters:**

- `product_id`: (Optional) The product ID to fetch reviews for. Takes precedence over `url` if both are provided.
- `url`: (Optional) Full product URL. Used only if `product_id` is not provided.
- `max_count`: Maximum number of reviews to fetch (default: 20).
- `debug`: Show debug messages if `True`.

> ⚠️ Either `product_id` or `url` must be provided.

**Returns:**

- A list of `ProductReview` objects.
- Each object supports `.json()` for serialization (e.g., for use with `pandas` or JSON export).

**Returns:**

-   A new `SearchResults` object with `.product_detail` and `.product_reviews` fields filled in (if data was provided).
    
----------
###  `SearchFilters` – Optional Search Filters

Use `SearchFilters` to refine your search results. All fields are optional. Pass it into the `search()` function via the `filters` argument.

#### Example:
```python
from tokopaedi import SearchFilters, search

filters = SearchFilters(
    pmin=100000,
    pmax=1000000,
    condition=1,              # 1 = New
    is_discount=True,
    bebas_ongkir_extra=True,
    rt=4.5,                   # Minimum rating 4.5
    latest_product=30         # Products listed in the last 30 days
)

results = search("logitech mouse", filters=filters)
```

#### Available Fields:

| Field                 | Type     | Description                                       | Accepted Values                  |
|----------------------|----------|---------------------------------------------------|----------------------------------|
| `pmin`               | `int`    | Minimum price (in IDR)                            | e.g., `100000`                   |
| `pmax`               | `int`    | Maximum price (in IDR)                            | e.g., `1000000`                  |
| `condition`          | `int`    | Product condition                                 | `1` = New, `2` = Used            |
| `shop_tier`          | `int`    | Type of shop                                      | `2` = Mall, `3` = Power Shop     |
| `rt`                 | `float`  | Minimum rating                                    | e.g., `4.5`                      |
| `latest_product`     | `int`    | Product recency filter                            | `7`, `30`, `90`               |
| `bebas_ongkir_extra` | `bool`   | Filter for extra free shipping                   | `True` / `False`                 |
| `is_discount`        | `bool`   | Only show discounted products                    | `True` / `False`                 |
| `is_fulfillment`     | `bool`   | Only Fulfilled by Tokopedia                      | `True` / `False`                 |
| `is_plus`            | `bool`   | Only Tokopedia PLUS sellers                      | `True` / `False`                 |
| `cod`                | `bool`   | Cash on delivery available                        | `True` / `False`                 |


## Product Details & Reviews Enrichment

Tokopaedi supports data enrichment to attach detailed product information and customer reviews directly to search results. This is useful when you want to go beyond basic search metadata and analyze full product details or customer feedback.
#### Example:
```python
# Enrich search results
results = search("Asus Zenbook S14 32GB", max_result=10, debug=True, filters=filters)
results.enrich_details(debug=True)
results.enrich_reviews(max_result=50, debug=True)

# Enrich product detail with reviews
product = get_product(url="https://www.tokopedia.com/asusrogindonesia/asus-tuf-a15-fa506ncr-ryzen-7-7435hs-rtx3050-4gb-8gb-512gb-w11-ohs-o365-15-6fhd-144hz-ips-rgb-blk-r735b1t-om-laptop-8gb-512gb-4970d?extParam=whid%3D17186756&aff_unique_id=&channel=others&chain_key=")
product.enrich_reviews(max_result=50, debug=True)
```

Enrichment methods are available on both the `SearchResults` container and individual `ProductData` objects:

### On `SearchResults`

- `enrich_details(debug: bool = False) -> None`  
  Enriches all items in the result with detailed product info.  
  - `debug`: If `True`, logs each enrichment step.

- `enrich_reviews(max_result: int = 10, debug: bool = False) -> None`  
  Enriches all items with customer reviews (up to `max_result` per product).  
  - `max_result`: Number of reviews to fetch for each product.  
  - `debug`: If `True`, logs the review enrichment process.

### On `ProductData`

- `enrich_details(debug: bool = False) -> None`  
  Enriches this specific product with detailed information.

- `enrich_reviews(max_result: int = 10, debug: bool = False) -> None`  
  Enriches this product with customer reviews.

This design allows for flexibility: enrich a full result set at once, or enrich individual items selectively as needed.


## Example: Scrape directly from Jupyter Notebook

Tokopaedi is fully compatible with Jupyter Notebook, making it easy to explore and manipulate data interactively. You can perform searches, enrich product details and reviews, and convert results to pandas DataFrames for analysis all from a notebook environment.

```python
from tokopaedi import search, SearchFilters, get_product, get_reviews
import json
import pandas as pd
from pandas import json_normalize

filters = SearchFilters(
            bebas_ongkir_extra = True,
            pmin = 15000000,
            pmax = 25000000,
            rt = 4.5
        )

results = search("Asus Zenbook S14 32GB", max_result=10, debug=False, filters=filters)

# Enrich each result with product details and reviews
results.enrich_details(debug=False)
results.enrich_reviews(max_result=50, debug=False)

# Convert to DataFrame and preview important fields
df = json_normalize(results.json())
df[["product_id", "product_name", "price", "price_original","discount_percentage","rating","shop.name"]].head()

# Reviews
df.iloc[0].reviews

# Retrieve single product by url
product = get_product(url="https://www.tokopedia.com/asusrogindonesia/asus-tuf-a15-fa506ncr-ryzen-7-7435hs-rtx3050-4gb-8gb-512gb-w11-ohs-o365-15-6fhd-144hz-ips-rgb-blk-r735b1t-om-laptop-8gb-512gb-4970d?extParam=whid%3D17186756&aff_unique_id=&channel=others&chain_key=")
product.enrich_reviews(max_result=50, debug=True)
df = json_normalize(product.json())
df[["product_id", "product_name", "price", "price_original","discount_percentage","rating","shop.name"]].head()
```
![Tokopaedi Runtime](image/notebook.png)

## 📋 Changelog

### 0.2.0
- Improve price accuracy with user spoofing (mobile pricing)
- Shop type conistency
- Minor extractor fix
- Replaced `ProductSearchResult` with `ProductData` for a unified model
- Removed `combine_data` and replace it with enrichment functions
- Added `.enrich_details(debug=False)` to `ProductData` and `SearchResults`
- Added `.enrich_reviews(max_result=10, debug=False)` to `ProductData` and `SearchResults`

### 0.1.3
- Added `url` parameter to `get_reviews()` and `get_product()` for direct product URL support

### 0.1.1
- Improved documentation and metadata

### 0.1.0
- Initial release with:
  - `search()` function with filters
  - `get_product()` for detailed product info
  - `get_reviews()` for customer reviews

## Author

Created by [**Hilmi Azizi**](https://hilmiazizi.com). For inquiries, feedback, or collaboration, contact me at [root@hilmiazizi.com](mailto:root@hilmiazizi.com). You can also reach out via [GitHub Issues](https://github.com/hilmiazizi/tokopaedi/issues) for bug reports or feature suggestions.

## 📄 License

This project is licensed under the MIT License.

You are free to use, modify, and distribute this project with attribution. See the [LICENSE](https://github.com/hilmiazizi/tokopaedi/blob/main/LICENSE) file for more details.
