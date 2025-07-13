__version__ = '0.1.0'
from dataclasses import dataclass
from typing import Optional
from .search import search
from .get_product import get_product
from .get_reviews import get_reviews
from .tokopaedi_types import ProductSearchResult, ProductData, ProductReview

def combine_data(
    search_result: ProductSearchResult,
    product: Optional[ProductData] = None,
    reviews: Optional[list[ProductReview]] = None,
) -> ProductSearchResult:
    search_result.product_detail = product
    search_result.product_reviews = reviews
    return search_result

@dataclass
class SearchFilters:
    # Free shipping benefit (bebas ongkir ekstra)
    # true = only show products with free shipping
    bebas_ongkir_extra: Optional[bool] = None

    # Discounted products
    # true = only show products with active discounts
    is_discount: Optional[bool] = None

    # Product condition
    # 1 = New
    # 2 = Used
    condition: Optional[int] = None

    # Shop tier
    # 2 = Mall
    # 3 = Power Shop
    shop_tier: Optional[int] = None

    # Minimum price (in IDR)
    pmin: Optional[int] = None

    # Maximum price (in IDR)
    pmax: Optional[int] = None

    # Fulfilled by Tokopedia
    # true = only show products fulfilled by Tokopedia
    is_fulfillment: Optional[bool] = None

    # Tokopedia Plus membership products
    # true = only show products available under Tokopedia Plus
    is_plus: Optional[bool] = None

    # Cash on Delivery (COD)
    # true = only show products eligible for COD
    cod: Optional[bool] = None

    # Minimum average rating (0.0 to 5.0)
    rt: Optional[float] = None

    # Product age in days
    # 7  = added in the last 7 days
    # 30 = added in the last 30 days
    # 90 = added in the last 90 days
    latest_product: Optional[int] = None
