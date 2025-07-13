

# Tokopaedi

Tokopaedi is a Python library for extracting e-commerce data from Tokopedia, including product search, detailed product information, and product reviews.

## Features

- `search()` – search products by keyword with support for filters
- `get_product()` – fetch rich product details including variants and media
- `get_reviews()` – retrieve product reviews with ratings and timestamps
- Dataclass-based results with `.json()` method for easy conversion
- `SearchResults` container for iterable and serializable product search results

## Installation

``pip install tokopaedi``

  ##  Quick Start

```python
from tokopaedi import search, SearchFilters, get_product, get_reviews, combine_data
from dataclasses import dataclass, asdict
import json

filters = SearchFilters(
            bebas_ongkir_extra = True,
            pmin = 15000000,
            pmax = 30000000,
            rt = 4.5
        )

results = search("Zenbook 14 32GB", max_result=100, debug=False)
for result in results:
    combine_data(
        result,
        get_product(product_id=result.product_id, debug=True),
        get_reviews(product_id=result.product_id, max_result=20, debug=True)
    )

with open('log.json','w') as f:
    f.write(json.dumps(results.json(), indent=4))
print(json.dumps(results.json(), indent=4))
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

### 📦 `get_product(product_id: Union[int, str], debug: bool = False) -> ProductData`

Fetch detailed information for a given product.

**Parameters:**

-   `product_id`: ID of a product returned from `search()`.
-   `debug`: Show debug message if True
    

**Returns:**

-   A `ProductData` instance containing detailed information (price, variants, media, etc.).
    
-   Supports `.json()` for serialization.
    

----------

### 🗣️ `get_reviews(product_id: Union[int, str], max_count: int = 20, debug: bool = False) -> List[ProductReview]`

Scrape customer reviews for a given product.

**Parameters:**

-   `product_id`: Product ID to fetch reviews for.
    
-   `max_count`: Max number of reviews to fetch (default: 20).
-   `debug`: Show debug message if True
    

**Returns:**

-   A list of `ProductReview` objects, each of which has a `.json()` method.
    

----------

### 🔗 `combine_data(search_results, products=None, reviews=None) -> SearchResults`

Attach product detail and/or reviews to the search results.

**Parameters:**

-   `search_results`: The `SearchResults` from `search()`.
    
-   `products`: List of `ProductData` from `get_product()` (optional).
    
-   `reviews`: List of `ProductReview` from `get_reviews()` (optional).
    

**Returns:**

-   A new `SearchResults` object with `.product_detail` and `.product_reviews` fields filled in (if data was provided).
    

----------
##  `SearchFilters` – Optional Search Filters

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


---

## Example: Enrich with product details & reviews, then convert to pandas DataFrame from Jupyter Notebook

```python
from tokopaedi import search, SearchFilters, get_product, get_reviews, combine_data
import json
import pandas as pd
from pandas import json_normalize

filters = SearchFilters(
    bebas_ongkir_extra=True,
    pmax=100000,
    rt=4.5
)

# Fetch search results
results = search("logitech g304", max_result=10, debug=False)

# Enrich each result with product details and reviews
for result in results:
    combine_data(
        result,
        get_product(product_id=result.product_id, debug=False),
        get_reviews(product_id=result.product_id, max_result=1, debug=False)
    )

# Convert to DataFrame and preview important fields
df = json_normalize(results.json())
print(df[[
    "product_id",
    "category",
    "real_price",
    "original_price",
    "product_detail.product_name",
    "rating",
    "shop.name"
]].head())
```

## 📄 License

This project is licensed under the MIT License.

You are free to use, modify, and distribute this project with attribution. See the `LICENSE` file for more details.
