from dataclasses import dataclass, field, asdict
from typing import List, Optional, Iterator

@dataclass
class ProductMedia:
    original: str
    thumbnail: str
    max_res: str

@dataclass
class ProductOption:
    option_id: int
    option_name: str
    option_child: List[str]

@dataclass
class ProductVariant:
    option_ids: List[int]
    option_name: str
    option_url: str
    price: int
    price_string: str
    discount: str
    image_url: Optional[str] = None
    stock: Optional[int] = None

@dataclass
class ProductData:
    product_id: int
    product_name: str
    url: str
    product_status: str
    product_price: int
    product_price_text: str
    product_price_original: str
    product_discount_percentage: str
    weight: int
    weight_unit: str
    product_media: List[ProductMedia]
    sold_count: int
    rating: float
    review_count: int
    discussion_count: int
    total_stock: int
    etalase: str
    etalase_url: str
    category: str
    sub_category: List[str]
    product_option: List[ProductOption]
    variants: List[ProductVariant]
    shop_id: int
    shop_name: str
    shop_location: List[str]

    def json(self):
        return asdict(self)

@dataclass
class ProductReview:
    feedback_id: int
    variant_name: Optional[str]
    message: str
    rating: float
    review_age: str
    user_full_name: str
    user_url: str
    response_message: Optional[str]
    response_created_text: Optional[str]
    images: List[str] = field(default_factory=list)
    videos: List[str] = field(default_factory=list)
    likes: int = 0

    def json(self):
        return asdict(self)

@dataclass
class TokopaediShop:
    shop_id: int
    name: str
    city: Optional[str]
    url: str
    is_official: Optional[bool]

@dataclass
class ProductSearchResult:
    product_id: int
    product_sku:int
    name: str
    category: str
    url: str
    sold_count: Optional[int]
    original_price: str
    real_price: int
    real_price_text: str
    rating: Optional[float]
    image: Optional[str]
    shop: TokopaediShop
    product_detail: Optional[ProductData] = None
    product_reviews: Optional[List[ProductReview]] = None

    def json(self):
        return asdict(self)

class SearchResults:
    def __init__(self, items: List[ProductSearchResult] = None):
        self.items = items or []

    def append(self, item: ProductSearchResult) -> None:
        self.items.append(item)

    def extend(self, more: List[ProductSearchResult]) -> None:
        self.items.extend(more)

    def __getitem__(self, index) -> ProductSearchResult:
        return self.items[index]

    def __iter__(self) -> Iterator[ProductSearchResult]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def json(self) -> List[dict]:
        return [item.json() for item in self.items]

    def __repr__(self) -> str:
        return f"<SearchResults total={len(self.items)}>"

    def __add__(self, other: "SearchResults") -> "SearchResults":
        if not isinstance(other, SearchResults):
            return NotImplemented
        return SearchResults(self.items + other.items)

    def __iadd__(self, other: "SearchResults") -> "SearchResults":
        if not isinstance(other, SearchResults):
            return NotImplemented
        self.extend(other.items)
        return self
