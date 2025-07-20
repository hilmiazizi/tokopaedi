from curl_cffi import requests
import logging
import traceback
import json
from .tokopaedi_types import ProductData, ProductMedia, ProductOption, ProductVariant, TokopaediShop, shop_resolver
from .custom_logging import setup_custom_logging
from .get_fingerprint import randomize_fp

logger = setup_custom_logging()

def product_details_extractor(json_data):
    pdp = json_data.get("data", {}).get("pdpGetLayout", {})
    components = pdp.get("components", [])

    def find_component(name):
        for c in components:
            if c.get("name") == name:
                return c.get("data", [])
        return []

    product_content = find_component("product_content")
    product_content = product_content[0] if product_content else {}
    product_media_raw = find_component("product_media")
    product_media_raw = product_media_raw[0].get("media", []) if product_media_raw else []
    basic_info = pdp.get("basicInfo", {})
    product_url = basic_info.get("url", "")
    product_media = [
        ProductMedia(
            original=media.get("URLOriginal", ""),
            thumbnail=media.get("URLThumbnail", ""),
            max_res=media.get("URLMaxRes", ""),
        )
        for media in product_media_raw
    ]

    product_option = []
    variants = []
    mini_variant = find_component("mini_variant_options")
    if mini_variant:
        mini_variant = mini_variant[0] if mini_variant else {}
        for option in mini_variant.get('variants', []):
            option_id = int(option.get('productVariantID', 0) or 0)
            option_name = option.get('name', '')
            option_child = [x.get('value', '') for x in option.get('option', [])]
            product_option.append(ProductOption(
                option_id=option_id,
                option_name=option_name,
                option_child=option_child
            ))

        for child in mini_variant.get("children", []):
            variants.append(
                ProductVariant(
                    option_ids=child.get("optionID", []),
                    option_name=child.get('productName', ""),
                    option_url=child.get('productURL', ""),
                    price=child.get("price", 0),
                    price_string=child.get("priceFmt", ""),
                    discount=child.get('discPercentage', ""),
                    image_url=child.get("picture", {}).get("url", ""),
                    stock=child.get("stock", {}).get('stock', None),
                )
            )

    pdpdSession = pdp.get('pdpSession')
    shop_type = json.loads(pdpdSession).get('stier', {}) if pdpdSession else None

    return ProductData(
        product_id=basic_info.get('productID'),
        product_sku = basic_info.get("ttsSKUID"),
        product_name=product_content.get("name", ""),
        url=product_url,
        main_image=basic_info.get("defaultMediaURL"),
        status=basic_info.get("status", ""),
        price=product_content.get("price", {}).get("value", 0),
        price_text=product_content.get("price", {}).get("priceFmt", ""),
        price_original=product_content.get("price", {}).get("slashPriceFmt", ""),
        discount_percentage=product_content.get("price", {}).get("discPercentage", ""),
        weight=int(basic_info.get("weight", 0) or 0),
        weight_unit=basic_info.get("weightUnit", ""),
        product_media=product_media,
        sold_count=int(basic_info.get("txStats", {}).get("countSold", 0) or 0),
        rating=float(basic_info.get("stats", {}).get("rating", 0) or 0),
        review_count=int(basic_info.get("stats", {}).get("countReview", 0) or 0),
        discussion_count=int(basic_info.get("stats", {}).get("countTalk", 0) or 0),
        total_stock=int(basic_info.get("totalStockFmt", "0").replace(".", "") or 0),
        etalase=basic_info.get("menu", {}).get("name", ""),
        etalase_url=basic_info.get("menu", {}).get("url", ""),
        category=basic_info.get("category", {}).get("name", ""),
        sub_category=[d.get("name", "") for d in basic_info.get("category", {}).get("detail", [])],
        product_option=product_option,
        variants=variants,
        shop=TokopaediShop(
            shop_id=int(basic_info.get("shopID", 0) or 0),
            name=basic_info.get("shopName", ""),
            city=basic_info.get('shopMultilocation', {}).get('cityName', ""),
            url='/'.join(product_url.split('/')[:-1]),
            shop_type=shop_resolver(shop_type)
        )
    )

def parse_tokped_url(url):
    temp = url.split('?')[0]
    temp = url.split('tokopedia.com/')[1].split('/')
    shop_id = temp[0] if len(temp) > 0 else ""
    product_key = temp[1] if len(temp) > 1 else ""
    return shop_id, product_key

def get_product(product_id=None, url=None, debug=False):
    assert url or product_id
    user_id, fingerprint = randomize_fp()
    if url:
        shop_id, product_key = parse_tokped_url(url)
        if not product_id:
            assert shop_id or product_key, "Failed to resolve product from URL"
    if product_id:
        product_id = str(product_id)
        shop_id, product_key = None, None

    headers = {
        'Host': 'gql.tokopedia.com',
        'Fingerprint-Data': fingerprint,
        'X-Tkpd-Userid': user_id,
        'X-Tkpd-Path': '/graphql/ProductDetails/getPDPLayout',
        'X-Method': 'POST',
        'Request-Method': 'POST',
        'X-Tkpd-Akamai': 'pdpGetLayout',
        'X-Device': 'ios-2.318.0',
        'Accept-Language': 'id;q=1.0, en;q=0.9',
        'User-Agent': 'Tokopedia/2.318.0 (com.tokopedia.Tokopedia; build:202505022018; iOS 18.5.0) Alamofire/2.318.0',
        'Content-Type': 'application/json; encoding=utf-8',
        'X-App-Version': '2.318.0',
        'Accept': 'application/json',
        'X-Theme': 'default',
        'X-Dark-Mode': 'false',
        'X-Price-Center': 'true',
    }

    json_data = {
        'variables': {
            'apiVersion': 1,
            'userLocation': {
                'addressID': '',
                'addressName': '',
                'receiverName': '',
                'postalCode': '',
                'districtID': '',
                'cityID': '',
                'latlon': '',
            },
            'tokonow': {
                'shopID': '0',
                'warehouses': [],
                'whID': '0',
                'serviceType': 'ooc',
            },
            'extParam': '',
            'productId': product_id if product_id else "",
            'shopDomain': shop_id if url else "",
            'productKey': product_key if url else "",
            'whID': '',
            'layoutID': '',
        },
        'query': 'query PDP_getPDPLayout($productId: String, $shopDomain: String, $productKey: String, $apiVersion: Float, $whID: String, $layoutID: String, $userLocation: pdpUserLocation, $extParam: String, $tokonow: pdpTokoNow) {\npdpGetLayout(productID: $productId, shopDomain: $shopDomain, productKey: $productKey, apiVersion: $apiVersion, whID: $whID, layoutID: $layoutID, userLocation: $userLocation, extParam: $extParam, tokonow: $tokonow) {\nrequestID\nname\npdpSession\nbasicInfo {\nproductID\ninitialVariantOptionID\ncategory {\nid\nname\ntitle\nbreadcrumbURL\nisAdult\nisKyc\ndetail {\nid\nname\nbreadcrumbURL\n}\nttsID\nttsDetail {\nid\nname\nbreadcrumbURL\n}\n}\nmenu {\nid\nname\nurl\n}\nshopID\nshopName\nalias\nminOrder\nmaxOrder\nurl\ncatalogID\nneedPrescription\nweight\nweightUnit\nstatus\ntxStats {\ntransactionReject\ntransactionSuccess\ncountSold\nitemSoldFmt\n}\nstats {\nrating\ncountTalk\ncountView\ncountReview\n}\ndefaultOngkirEstimation\nisTokoNow\ntotalStockFmt\nisGiftable\ndefaultMediaURL\nshopMultilocation {\ncityName\n}\nisBlacklisted\nblacklistMessage {\ntitle\ndescription\nbutton\n}\nweightWording\nttsPID\nttsSKUID\nttsShopID\n}\nadditionalData {\nfomoSocialProofs {\nname\ntext\nicons\ntypeIcon\nbackgroundColor\nposition\n}\n}\ncomponents {\nname\ntype\nkind\ndata {\n... on pdpDataComponentSocialProofV2 {\nsocialProofContent {\nsocialProofType\nsocialProofID\ntitle\nsubtitle\nicon\napplink {\nappLink\n}\nbgColor\nchevronColor\nshowChevron\nhasSeparator\n}\n}\n... on pdpDataProductMedia {\nmedia {\ntype\nURLOriginal\nURLThumbnail\ndescription\nvideoURLIOS\nisAutoplay\nindex\nvariantOptionID\nURLMaxRes\n}\nrecommendation{\nlightIcon\ndarkIcon\niconText\nbottomsheetTitle\nrecommendation\n}\nvideos {\nsource\nurl\n}\ncontainerType\nliveIndicator {\nisLive\nchannelID\nmediaURL\napplink\n}\nshowJumpToVideo\n}\n... on pdpDataProductContent {\nname\nprice {\nvalue\ncurrency\nlastUpdateUnix\npriceFmt\nslashPriceFmt\ndiscPercentage\ncurrencyFmt\nvalueFmt\n}\ncampaign {\ncampaignID\ncampaignType\ncampaignTypeName\npercentageAmount\noriginalPrice\ndiscountedPrice\noriginalStock\nstock\nstockSoldPercentage\nendDateUnix\nisActive\nhideGimmick\nisUsingOvo\ncampaignIdentifier\nbackground\npaymentInfoWording\nproductID\ncampaignLogo\nshowStockBar\n}\nthematicCampaign {\nproductID\ncampaignName\nbackground\nicon\ncampaignLogo\nsuperGraphicURL\n}\nstock {\nuseStock\nvalue\nstockWording\n}\nvariant {\nisVariant\n}\nwholesale {\nminQty\nprice {\nvalue\ncurrency\nlastUpdateUnix\n}\n}\nisFreeOngkir {\nisActive\nimageURL\n}\npreorder {\nduration\ntimeUnit\nisActive\npreorderInDays\n}\nisCashback {\npercentage\n}\nisTradeIn\nisOS\nisPowerMerchant\nisWishlist\nisCOD\nparentName\nisShowPrice\nlabelIcons {\niconURL\nlabel\n}\n}\n... on pdpDataProductInfo {\nrow\ncontent {\ntitle\nsubtitle\napplink\n}\n}\n... on pdpDataInfo {\ntitle\napplink\nisApplink\nicon\nlightIcon\ndarkIcon\ncontent {\nicon\ntext\n}\nseparator\n}\n... on pdpDataProductVariant {\nparentID\ndefaultChild\nsizeChart\nmaxFinalPrice\ncomponentType\nlandingSubText\nsocialProof {\nbgColor\ncontents {\nname\ncontent\niconURL\n}\n}\nvariants {\nproductVariantID\nvariantID\nname\nidentifier\noption {\nproductVariantOptionID\nvariantUnitValueID\nvalue\nhex\npicture {\nurl\nurl100\n}\n}\n}\nchildren {\nproductID\nprice\npriceFmt\nslashPriceFmt\ndiscPercentage\nsku\noptionID\nproductName\nproductURL\npicture {\nurl\nurl100\n}\nstock {\nstock\nisBuyable\nstockWording\nstockWordingHTML\nminimumOrder\nmaximumOrder\nstockFmt\nstockCopy\n}\nisCOD\nisWishlist\ncampaignInfo {\ncampaignID\ncampaignType\ncampaignTypeName\ndiscountPercentage\noriginalPrice\ndiscountPrice\nstock\nstockSoldPercentage\nendDateUnix\nappLinks\nisActive\nhideGimmick\nisUsingOvo\nminOrder\ncampaignIdentifier\nbackground\npaymentInfoWording\ncampaignLogo\nshowStockBar\n}\nthematicCampaign {\ncampaignName\nicon\nbackground\nproductID\ncampaignLogo\nsuperGraphicURL\n}\nsubText\npromo {\nvalue\niconURL\nproductID\npromoPriceFmt\nsubtitle\napplink\ncolor\nbackground\npromoType\nsuperGraphicURL\npriceAdditionalFmt\nseparatorColor\nbottomsheetParam\npromoCodes {\npromoID\npromoCode\npromoCodeType\n}\n}\ncurrencyFmt\nvaluePriceFmt\ncomponentPriceType\nisTopSold\nlabelIcons {\niconURL\nlabel\n}\nttsPID\nttsSKUID\n}\n}\n... on pdpDataCustomInfo {\nicon\ntitle\nisApplink\napplink\nseparator\ndescription\nlabel {\nvalue\ncolor\n}\nlightIcon\ndarkIcon\n}\n... on pdpDataComponentReviewV2 {\nmostHelpfulReviewParam {\nlimit\n}\n}\n... on pdpDataProductDetail {\ntitle\ncontent {\ntype\nkey\nextParam\naction\ntitle\nsubtitle\napplink\nshowAtFront\nshowAtBottomsheet\ninfoLink\nicon\n}\ncatalogBottomsheet {\nactionTitle\nbottomSheetTitle\nparam\n}\nbottomsheet {\nactionTitle\nbottomSheetTitle\nparam\n}\n}\n... on pdpDataOneLiner {\nproductID\noneLinerContent\nlinkText\napplink\nseparator\nisVisible\ncolor\nicon\neduLink {\nappLink\n}\n}\n... on pdpDataCategoryCarousel {\nlinkText\ntitleCarousel\napplink\nlist {\ncategoryID\nicon\ntitle\nisApplink\napplink\n}\n}\n... on pdpDataBundleComponentInfo {\ntitle\nwidgetType\nproductID\nwhID\n}\n... on pdpDataDynamicOneLiner {\nname\napplink\nseparator\nicon\nstatus\nchevronPos\ntext\nbgColor\nchevronColor\npadding {\nt\nb\n}\nimageSize {\nw\nh\n}\n}\n... on pdpDataComponentDynamicOneLinerVariant {\nname\napplink\nseparator\nicon\nstatus\nchevronPos\ntext\nbgColor\nchevronColor\npadding {\nt\nb\n}\nimageSize {\nw\nh\n}\n}\n... on pdpDataCustomInfoTitle {\ntitle\nstatus\ncomponentName\n}\n... on pdpDataProductDetailMediaComponent {\ntitle\ndescription\ncontentMedia {\nurl\nratio\ntype\n}\nshow\nctaText\n}\n... on pdpDataOnGoingCampaign {\ncampaign {\ncampaignID\ncampaignType\ncampaignTypeName\npercentageAmount\noriginalPrice\ndiscountedPrice\noriginalStock\nstock\nstockSoldPercentage\nendDateUnix\nisActive\nhideGimmick\nisUsingOvo\ncampaignIdentifier\nbackground\npaymentInfoWording\nproductID\ncampaignLogo\nshowStockBar\n}\nthematicCampaign {\nproductID\ncampaignName\nbackground\nicon\ncampaignLogo\nsuperGraphicURL\n}\n}\n... on pdpDataProductListComponent {\nthematicID\nqueryParam\n}\n... on pdpDataComponentPromoPrice {\nprice {\nvalue\ncurrency\nlastUpdateUnix\npriceFmt\nslashPriceFmt\ndiscPercentage\ncurrencyFmt\nvalueFmt\n}\npromo {\nvalue\niconURL\nproductID\npromoPriceFmt\nsubtitle\napplink\ncolor\nbackground\npromoType\nsuperGraphicURL\npriceAdditionalFmt\nseparatorColor\nbottomsheetParam\npromoCodes {\npromoID\npromoCode\npromoCodeType\n}\n}\ncomponentPriceType\n}\n... on pdpDataComponentSDUIDivKit {\ntemplate\n}\n... on pdpDataComponentShipmentV4 {\ndata {\nproductID\nwarehouse_info {\nwarehouse_id\nis_fulfillment\ndistrict_id\npostal_code\ngeolocation\ncity_name\nttsWarehouseID\n}\nuseBOVoucher\nisCOD\nmetadata\n}\n}\n... on pdpDataComponentShipmentV5 {\ndata {\nproductID\nwarehouse_info {\nwarehouse_id\nis_fulfillment\ndistrict_id\npostal_code\ngeolocation\ncity_name\nttsWarehouseID\n}\nuseBOVoucher\nisCOD\nmetadata\n}\n}\n...on pdpDataAffordabilityGroupLabel {\naffordabilityData{\nproductID\nproductVouchers {\nidentifier\ntype\ntext\nbackgroundColor\n}\nshowChevron\nchevronColor\nappliedVoucherTypeIDs\n}\n}\n}\n}\n}\n}',
    }

    try:
        response = requests.post(
            'https://gql.tokopedia.com/graphql/ProductDetails/getPDPLayout',
            headers=headers,
            json=json_data,
            verify=False,
        )
        result_json = response.json()
        product_data = product_details_extractor(result_json)
        if debug:
            logger.detail(f"{product_data.product_id} - {product_data.product_name[0:40]}...")
        return product_data
    except Exception as e:
        print(traceback.format_exc())
        exit()