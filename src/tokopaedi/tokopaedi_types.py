from dataclasses import dataclass, field, asdict
from typing import List, Optional, Iterator

def shop_resolver(shop_tier):
    ''' Find shop tier by id and badge image '''
    try:
        shop_tier = int(shop_tier)
    except:
        if 'PM%20Pro%20Small.png' in shop_tier:
            shop_tier = 3
        elif 'official_store_badge' in shop_tier:
            shop_tier = 2
        else:
            shop_tier = 1

    if shop_tier == 1:
        return 'Normal'
    elif shop_tier == 2:
        return 'Mall'
    elif shop_tier == 3:
        return 'Power Shop'
    else:
        return None

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
    shop_type: str

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
    product_sku: str
    product_name: str
    url: str
    main_image: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    price_text: Optional[str] = None
    price_original: Optional[str] = None
    discount_percentage: Optional[str] = None
    weight: Optional[int] = None
    weight_unit: Optional[str] = None
    product_media: List[ProductMedia] = field(default_factory=list)
    sold_count: Optional[int] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    discussion_count: Optional[int] = None
    total_stock: Optional[int] = None
    etalase: Optional[str] = None
    etalase_url: Optional[str] = None
    category: str = None
    sub_category: Optional[List[str]] = None
    product_option: Optional[List[ProductOption]] = None
    variants: Optional[List[ProductVariant]] = None
    shop: TokopaediShop = None
    reviews: Optional[List[ProductReview]] = None
    has_detail: bool = False
    has_reviews: bool = False

    def json(self):
        return asdict(self)

    def enrich_details(self, debug: bool = False):
        if not self.has_detail:
            from .get_product import get_product
            enriched_details = get_product(product_id=self.product_id, debug=debug)

            if enriched_details:
                for field_name in self.__dataclass_fields__:
                    setattr(self, field_name, getattr(enriched_details, field_name))
            self.has_detail = True

    def enrich_reviews(self, max_result=None, debug: bool = False):
        if not self.has_reviews:
            from .get_reviews import get_reviews
            self.reviews = get_reviews(product_id=self.product_id, debug=debug)
            self.has_reviews = True

class SearchResults:
    def __init__(self, items: List[ProductData] = None):
        self.items = items or []

    def enrich_details(self, debug=False):
        for product in self.items:
            product.enrich_details(debug)

    def enrich_reviews(self, max_result=None, debug=False):
        for product in self.items:
            product.enrich_reviews(max_result, debug)

    def __init__(self, items: List[ProductData] = None):
        self.items = items or []

    def append(self, item: ProductData) -> None:
        self.items.append(item)

    def extend(self, more: List[ProductData]) -> None:
        self.items.extend(more)

    def __getitem__(self, index) -> ProductData:
        return self.items[index]

    def __iter__(self) -> Iterator[ProductData]:
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
