from curl_cffi import requests
import json
import traceback
from urllib.parse import quote, parse_qs, urlencode
import logging
import logging
from dataclasses import dataclass
from typing import Optional

from .tokopaedi_types import SearchResults, ProductData, TokopaediShop, shop_resolver
from .custom_logging import setup_custom_logging
from .get_fingerprint import randomize_fp

logger = setup_custom_logging()


def search_extractor(result):
    if result['products']:
        product_result = []
        for product in result['products']:
            price_data = product.get('price',{})
            shop_info = product.get('shop')

            product_id = product.get('id')
            product_sku = product.get('stock', {}).get('ttsSKUID') 
            name = product.get('name')
            category = product.get('category',{}).get('name')
            url = product.get('url')
            sold_count = product.get('stock',{}).get('sold')
            price_original = price_data.get('original')
            price = price_data.get('number')
            price_text = price_data.get('text')
            rating = float(product.get('rating')) if product.get('rating') else None
            main_image = product.get('mediaURL',{}).get('image700')

            shop_id = shop_info.get('id')
            shop_name = shop_info.get('name')
            city = shop_info.get('city')
            shop_url = shop_info.get('url')
            shop_type = str(product.get('badge',{}).get('url'))

            product_result.append(ProductData(
                    product_id=product_id,
                    product_sku=product_sku,
                    product_name=name,
                    category=category,
                    url=url,
                    sold_count=sold_count,
                    price_original=price_original,
                    price=price,
                    price_text=price_text,
                    rating=rating,
                    main_image=main_image,
                    shop=TokopaediShop(
                            shop_id=shop_id,
                            name=shop_name,
                            city=city,
                            url=shop_url,
                            shop_type=shop_resolver(shop_type)
                        )
                ))
        return product_result
    else:
        return []

def dedupe(items):
    if not items:
        return SearchResults()
    return SearchResults(list({item.product_id: item for item in items}.values()))

def filters_to_query(filters) -> str:
    filter_dict = {k: v for k, v in vars(filters).items() if v is not None}
    return "&".join(f"{k}={quote(str(v), safe=',')}" for k, v in filter_dict.items())

def merge_params(original, additional=None):
    original_dict = {k: v[0] for k, v in parse_qs(original).items()}
    if additional:
        additional_dict = {k: v[0] for k, v in parse_qs(additional).items()}
    else:
        additional_dict = {}

    merged = {**original_dict, **additional_dict}

    return "&".join(f"{k}={quote(str(v), safe=',')}" for k, v in merged.items())

def search(keyword="zenbook 14 32gb", max_result=100, result_count=0, base_param=None, next_param=None, filters=None, debug=False):
    user_id, fingerprint = randomize_fp()
    headers = {
        'Host': 'gql.tokopedia.com',
        'Os_type': '2',
        'Fingerprint-Data': fingerprint,
        'X-Tkpd-Userid': user_id,
        'X-Tkpd-Path': '/graphql/SearchResult/getProductResult',
        'X-Method': 'POST',
        'X-Device': 'ios-2.318.0',
        'Request-Method': 'POST',
        'Accept-Language': 'id;q=1.0, en;q=0.9',
        'Content-Type': 'application/json; encoding=utf-8',
        'User-Agent': 'Tokopedia/2.318.0 (com.tokopedia.Tokopedia; build:202505022018; iOS 18.5.0) Alamofire/2.318.0',
        'Date': 'Sun, 29 Jun 2025 14:44:51 +0700',
        'X-App-Version': '2.318.0',
        'Accept': 'application/json',
        'X-Dark-Mode': 'false',
        'X-Theme': 'default',
        'Tt-Request-Time': '1751183091059',
        'X-Price-Center': 'true',
        'Device-Type': 'iphone',
        'Bd-Device-Id': '7132999401249080838',
    }

    if not base_param:
        base_param = f'user_warehouseId=0&user_shopId=0&user_postCode=10110&srp_initial_state=false&breadcrumb=true&ep=product&user_cityId=0&q={quote(keyword)}&related=true&source=search&srp_enter_method=normal_search&enter_method=normal_search&l_name=sre&user_districtId=0&srp_feature_id=&catalog_rows=0&page=1&srp_component_id=02.01.00.00&ob=0&srp_sug_type=&src=search&with_template=true&show_adult=false&srp_direct_middle_page=false&channel=product%20search&rf=false&navsource=home&use_page=true&dep_id=&device=ios'

    if filters:
        base_param = merge_params(base_param, filters_to_query(filters))

    json_data = {
        'query': 'query Search_SearchProduct($params: String!, $query: String!) {\n global_search_navigation(keyword: $query, size: 5, device: \"ios\", params: $params){\n data {\n source\n keyword\n title\n nav_template\n background\n see_all_applink\n show_topads\n info\n list {\n category_name\n name\n info\n image_url\n subtitle\n strikethrough\n background_url\n logo_url\n applink\n component_id\n }\n component_id\n tracking_option\n }\n }\n searchInspirationCarouselV2(params: $params){\n process_time\n data {\n title\n type\n position\n layout\n tracking_option\n color\n options {\n title\n subtitle\n icon_subtitle\n applink\n banner_image_url\n banner_applink_url\n identifier\n meta\n component_id\n card_button {\n  title\n  applink\n }\n bundle {\n  shop {\n  name\n  url\n  }\n  count_sold\n  price\n  original_price\n  discount\n  discount_percentage\n }\n  product {\n id\n ttsProductID\n name\n price\n price_str\n image_url\n rating\n count_review\n applink\n description\n original_price\n discount\n discount_percentage\n rating_average\n badges {\n title\n image_url\n show\n }\n shop {\n id\n name\n city\n ttsSellerID\n }\n label_groups {\n position\n title\n type\n url\n styles {\n key\n value\n }\n }\n freeOngkir {\n isActive\n image_url\n }\n ads {\n id\n productClickUrl\n productWishlistUrl\n productViewUrl\n }\n wishlist\n component_id\n customvideo_url\n label\n bundle_id\n parent_id\n min_order\n category_id\n stockbar {\n percentage_value\n value\n color\n ttsSkuID\n }\n warehouse_id_default\n sold\n }\n }\n }\n }\n searchInspirationWidget(params: $params){\n data {\n title\n header_title\n header_subtitle\n type\n position\n layout\n options {\n text\n img\n color\n applink\n multi_filters{\n  key\n  name\n  value\n  val_min\n  val_max\n }\n component_id\n }\n tracking_option\n input_type\n }\n }\n productAds: displayAdsV3(displayParams: $params) {\n status {\n error_code\n message\n }\n header {\n process_time\n total_data\n }\n data{\n id\n ad_ref_key\n redirect\n sticker_id\n sticker_image\n product_click_url\n product_wishlist_url\n shop_click_url\n tag\n creative_id\n log_extra\n product{\n id\n tts_product_id\n tts_sku_id\n parent_id\n name\n wishlist\n image{\n  m_url\n  s_url\n  xs_url\n  m_ecs\n  s_ecs\n  xs_ecs\n }\n uri\n relative_uri\n price_format\n price_range\n campaign {\n  discount_percentage\n  original_price\n }\n wholesale_price {\n  price_format\n  quantity_max_format\n  quantity_min_format\n }\n count_talk_format\n count_review_format\n category {\n  id\n }\n category_breadcrumb\n product_preorder\n product_wholesale\n product_item_sold_payment_verified\n free_return\n product_cashback\n product_new_label\n product_cashback_rate\n product_rating\n product_rating_format\n labels {\n  color\n  title\n }\n free_ongkir {\n  is_active\n  img_url\n }\n label_group {\n  position\n  type\n  title\n  url\n  style {\n  key\n  value\n  }\n }\n top_label\n bottom_label\n product_minimum_order\n customvideo_url\n }\n shop{\n id\n tts_seller_id\n name\n domain\n location\n city\n gold_shop\n gold_shop_badge\n lucky_shop\n uri\n shop_rating_avg\n owner_id\n is_owner\n badges{\n  title\n  image_url\n  show\n }\n }\n applinks\n }\n template {\n is_ad\n }\n }\n searchProductV5(params: $params) {\n header {\n totalData\n responseCode\n keywordProcess\n keywordIntention\n componentID\n meta {\n productListType\n hasPostProcessing\n hasButtonATC\n dynamicFields\n }\n isQuerySafe\n additionalParams\n autocompleteApplink\n backendFilters\n backendFiltersToggle\n }\n data {\n totalDataText\n banner {\n position\n text\n applink\n imageURL\n componentID\n trackingOption\n }\n redirection {\n applink\n }\n related {\n relatedKeyword\n position\n trackingOption\n otherRelated {\n  keyword\n  applink\n  componentID\n  products {\n  id\n  name\n  applink\n  mediaURL {\n  image\n  }\n  shop {\n  name\n  city\n  }\n  badge {\n  title\n  url\n  }\n  price {\n  text\n  number\n  }\n  freeShipping {\n  url\n  }\n  labelGroups {\n  id\n  position\n  title\n  type\n  url\n  styles {\n  key\n  value\n  }\n  }\n  rating\n  wishlist\n  ads {\n  id\n  productClickURL\n  productViewURL\n  productWishlistURL\n  }\n  meta {\n  parentID\n  warehouseID\n  componentID\n  isImageBlurred\n  }\n  }\n }\n }\n suggestion {\n currentKeyword\n suggestion\n query\n text\n componentID\n trackingOption\n }\n ticker {\n id\n text\n query\n applink\n componentID\n trackingOption\n }\n violation {\n headerText\n descriptionText\n imageURL\n ctaApplink\n buttonText\n buttonType\n }\n products {\n id\n ttsProductID\n name\n url\n applink\n mediaURL {\n  image\n  image300\n  image500\n  image700\n  videoCustom\n }\n shop {\n  id\n  name\n  url\n  city\n  ttsSellerID\n }\n badge {\n  title\n  url\n }\n price {\n  text\n  number\n  range\n  original\n  discountPercentage\n }\n freeShipping {\n  url\n }\n labelGroups {\n  id\n  position\n  title\n  type\n  url\n  styles {\n  key\n  value\n  }\n }\n labelGroupsVariant {\n  title\n  type\n  typeVariant\n  hexColor\n }\n category {\n  id\n  name\n  breadcrumb\n  gaKey\n }\n rating\n wishlist\n ads {\n  id\n  productClickURL\n  productViewURL\n  productWishlistURL\n  tag\n  creativeID\n  logExtra\n }\n meta {\n  parentID\n  warehouseID\n  isPortrait\n  isImageBlurred\n  dynamicFields\n }\n stock {\n  sold\n  ttsSKUID\n }\n }\n shopWidget {\n headline {\n  badge {\n  url\n  }\n  shop {\n  id\n  imageShop {\n  sURL\n  }\n  City\n  name\n  ratingScore\n  ttsSellerID\n  products {\n  id\n  ttsProductID\n  name\n  applink\n  mediaURL {\n  image300\n  }\n  price {\n  text\n  original\n  discountPercentage\n  }\n  freeShipping {\n  url\n  }\n  labelGroups {\n  position\n  title\n  type\n  styles {\n   key\n   value\n  }\n  url\n  }\n  rating\n  meta {\n  parentID\n  dynamicFields\n  }\n  shop {\n  ttsSellerID\n  }\n  stock {\n  ttsSKUID\n  }\n  }\n  }\n }\n meta {\n  applinks\n }\n }\n filters {\n title\n template_name: templateName\n isNew\n subTitle: subtitle\n search: searchInfo {\n  searchable\n  placeholder\n }\n options {\n  name\n  key\n  value\n  icon\n  isPopular\n  isNew\n  hexColor\n  inputType\n  valMin\n  valMax\n  Description: description\n  child {\n  name\n  key\n  value\n  isPopular\n  child {\n  name\n  key\n  value\n  }\n  }\n }\n }\n quickFilters {\n title\n chip_name: chipName\n options {\n  name\n  key\n  value\n  icon\n  is_popular: isPopular\n  is_new: isNew\n  hex_color: hexColor\n  input_type: inputType\n  image_url_active: imageURLActive\n  image_url_inactive: imageURLInactive\n }\n }\n sorts {\n name\n key\n value\n }\n }\n }\n fetchLastFilter(param: $params) {\n data {\n title\n description\n category_id_l2\n applink\n tracking_option\n filters {\n title\n key\n name\n value\n }\n component_id\n }\n }\n }',
        'variables': {
            'params': base_param,
            'query': keyword,
        },
    }

    if next_param:
        params = merge_params(base_param, next_param)
        json_data['variables']['params'] = params

    try:
        response = requests.post(
            'https://gql.tokopedia.com/graphql/SearchResult/getProductResult',
            headers=headers,
            json=json_data,
            verify=False,
        )

        if 'searchProductV5' in response.text:
            result = response.json()['data']['searchProductV5']['data']
            result = SearchResults(search_extractor(result))
            if result:
                result_count += len(result)
                if debug:
                    for line in result:
                        logger.search(f'{line.product_id} - {line.product_name[0:40]}...')
                if result_count >= max_result:
                    return dedupe(result)

                next_param = response.json()['data']['searchProductV5']['header']['additionalParams']
                next_result = search(
                    keyword=keyword,
                    max_result=max_result,
                    result_count=result_count,
                    base_param=base_param,
                    next_param = next_param,
                    debug = debug
                )
                return dedupe(result+next_result)

        return dedupe(result)
    except:
        print(traceback.format_exc())
        return None