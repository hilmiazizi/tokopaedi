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
        'query': 'query Search_SearchProduct($params: String!, $query: String!) {\nglobal_search_navigation(keyword: $query, size: 5, device: "ios", params: $params){\ndata {\nsource\nkeyword\ntitle\nnav_template\nbackground\nsee_all_applink\nshow_topads\ninfo\nlist {\ncategory_name\nname\ninfo\nimage_url\nsubtitle\nstrikethrough\nbackground_url\nlogo_url\napplink\ncomponent_id\n}\ncomponent_id\ntracking_option\n}\n}\nsearchInspirationCarouselV2(params: $params){\nprocess_time\ndata {\ntitle\ntype\nposition\nlayout\ntracking_option\ncolor\noptions {\ntitle\nsubtitle\nicon_subtitle\napplink\nbanner_image_url\nbanner_applink_url\nidentifier\nmeta\ncomponent_id\ncard_button {\ntitle\napplink\n}\nbundle {\nshop {\nname\nurl\n}\ncount_sold\nprice\nprice_original\ndiscount\ndiscount_percentage\n}\nproduct {\nid\nttsProductID\nname\nprice\nprice_str\nimage_url\nrating\ncount_review\napplink\ndescription\nprice_original\ndiscount\ndiscount_percentage\nrating_average\nbadges {\ntitle\nimage_url\nshow\n}\nshop {\nid\nname\ncity\nttsSellerID\n}\nlabel_groups {\nposition\ntitle\ntype\nurl\nstyles {\nkey\nvalue\n}\n}\nfreeOngkir {\nisActive\nimage_url\n}\nads {\nid\nproductClickUrl\nproductWishlistUrl\nproductViewUrl\n}\nwishlist\ncomponent_id\ncustomvideo_url\nlabel\nbundle_id\nparent_id\nmin_order\ncategory_id\nstockbar {\npercentage_value\nvalue\ncolor\nttsSkuID\n}\nwarehouse_id_default\nsold\n}\n}\n}\n}\nsearchInspirationWidget(params: $params){\ndata {\ntitle\nheader_title\nheader_subtitle\ntype\nposition\nlayout\noptions {\ntext\nimg\ncolor\napplink\nmulti_filters{\nkey\nname\nvalue\nval_min\nval_max\n}\ncomponent_id\n}\ntracking_option\ninput_type\n}\n}\nproductAds: displayAdsV3(displayParams: $params) {\nstatus {\nerror_code\nmessage\n}\nheader {\nprocess_time\ntotal_data\n}\ndata{\nid\nad_ref_key\nredirect\nsticker_id\nsticker_image\nproduct_click_url\nproduct_wishlist_url\nshop_click_url\ntag\ncreative_id\nlog_extra\nproduct{\nid\ntts_product_id\ntts_sku_id\nparent_id\nname\nwishlist\nimage{\nm_url\ns_url\nxs_url\nm_ecs\ns_ecs\nxs_ecs\n}\nuri\nrelative_uri\nprice_format\nprice_range\ncampaign {\ndiscount_percentage\nprice_original\n}\nwholesale_price {\nprice_format\nquantity_max_format\nquantity_min_format\n}\ncount_talk_format\ncount_review_format\ncategory {\nid\n}\ncategory_breadcrumb\nproduct_preorder\nproduct_wholesale\nproduct_item_sold_payment_verified\nfree_return\nproduct_cashback\nproduct_new_label\nproduct_cashback_rate\nproduct_rating\nproduct_rating_format\nlabels {\ncolor\ntitle\n}\nfree_ongkir {\nis_active\nimg_url\n}\nlabel_group {\nposition\ntype\ntitle\nurl\nstyle {\nkey\nvalue\n}\n}\ntop_label\nbottom_label\nproduct_minimum_order\ncustomvideo_url\n}\nshop{\nid\ntts_seller_id\nname\ndomain\nlocation\ncity\ngold_shop\ngold_shop_badge\nlucky_shop\nuri\nshop_rating_avg\nowner_id\nis_owner\nbadges{\ntitle\nimage_url\nshow\n}\n}\napplinks\n}\ntemplate {\nis_ad\n}\n}\nsearchProductV5(params: $params) {\nheader {\ntotalData\nresponseCode\nkeywordProcess\nkeywordIntention\ncomponentID\nmeta {\nproductListType\nhasPostProcessing\nhasButtonATC\ndynamicFields\n}\nisQuerySafe\nadditionalParams\nautocompleteApplink\nbackendFilters\nbackendFiltersToggle\n}\ndata {\ntotalDataText\nbanner {\nposition\ntext\napplink\nimageURL\ncomponentID\ntrackingOption\n}\nredirection {\napplink\n}\nrelated {\nrelatedKeyword\nposition\ntrackingOption\notherRelated {\nkeyword\napplink\ncomponentID\nproducts {\nid\nname\napplink\nmediaURL {\nimage\n}\nshop {\nname\ncity\n}\nbadge {\ntitle\nurl\n}\nprice {\ntext\nnumber\n}\nfreeShipping {\nurl\n}\nlabelGroups {\nid\nposition\ntitle\ntype\nurl\nstyles {\nkey\nvalue\n}\n}\nrating\nwishlist\nads {\nid\nproductClickURL\nproductViewURL\nproductWishlistURL\n}\nmeta {\nparentID\nwarehouseID\ncomponentID\nisImageBlurred\n}\n}\n}\n}\nsuggestion {\ncurrentKeyword\nsuggestion\nquery\ntext\ncomponentID\ntrackingOption\n}\nticker {\nid\ntext\nquery\napplink\ncomponentID\ntrackingOption\n}\nviolation {\nheaderText\ndescriptionText\nimageURL\nctaApplink\nbuttonText\nbuttonType\n}\nproducts {\nid\nttsProductID\nname\nurl\napplink\nmediaURL {\nimage\nimage300\nimage500\nimage700\nvideoCustom\n}\nshop {\nid\nname\nurl\ncity\nttsSellerID\n}\nbadge {\ntitle\nurl\n}\nprice {\ntext\nnumber\nrange\noriginal\ndiscountPercentage\n}\nfreeShipping {\nurl\n}\nlabelGroups {\nid\nposition\ntitle\ntype\nurl\nstyles {\nkey\nvalue\n}\n}\nlabelGroupsVariant {\ntitle\ntype\ntypeVariant\nhexColor\n}\ncategory {\nid\nname\nbreadcrumb\ngaKey\n}\nrating\nwishlist\nads {\nid\nproductClickURL\nproductViewURL\nproductWishlistURL\ntag\ncreativeID\nlogExtra\n}\nmeta {\nparentID\nwarehouseID\nisPortrait\nisImageBlurred\ndynamicFields\n}\nstock {\nsold\nttsSKUID\n}\n}\nshopWidget {\nheadline {\nbadge {\nurl\n}\nshop {\nid\nimageShop {\nsURL\n}\nCity\nname\nratingScore\nttsSellerID\nproducts {\nid\nttsProductID\nname\napplink\nmediaURL {\nimage300\n}\nprice {\ntext\noriginal\ndiscountPercentage\n}\nfreeShipping {\nurl\n}\nlabelGroups {\nposition\ntitle\ntype\nstyles {\nkey\nvalue\n}\nurl\n}\nrating\nmeta {\nparentID\ndynamicFields\n}\nshop {\nttsSellerID\n}\nstock {\nttsSKUID\n}\n}\n}\n}\nmeta {\napplinks\n}\n}\nfilters {\ntitle\ntemplate_name: templateName\nisNew\nsubTitle: subtitle\nsearch: searchInfo {\nsearchable\nplaceholder\n}\noptions {\nname\nkey\nvalue\nicon\nisPopular\nisNew\nhexColor\ninputType\nvalMin\nvalMax\nDescription: description\nchild {\nname\nkey\nvalue\nisPopular\nchild {\nname\nkey\nvalue\n}\n}\n}\n}\nquickFilters {\ntitle\nchip_name: chipName\noptions {\nname\nkey\nvalue\nicon\nis_popular: isPopular\nis_new: isNew\nhex_color: hexColor\ninput_type: inputType\nimage_url_active: imageURLActive\nimage_url_inactive: imageURLInactive\n}\n}\nsorts {\nname\nkey\nvalue\n}\n}\n}\nfetchLastFilter(param: $params) {\ndata {\ntitle\ndescription\ncategory_id_l2\napplink\ntracking_option\nfilters {\ntitle\nkey\nname\nvalue\n}\ncomponent_id\n}\n}\n}',
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