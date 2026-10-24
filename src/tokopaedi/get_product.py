from curl_cffi import requests
import traceback
import json
from .tokopaedi_types import ProductData, ProductMedia, ProductOption, ProductVariant, TokopaediShop, shop_resolver
from .custom_logging import setup_custom_logging
from .get_fingerprint import randomize_fp
import random

logger = setup_custom_logging()

def product_details_extractor(json_data):
    data = json_data.get("data", {}) or {}
    pdp = data.get("pdpMainInfo") or data.get("pdpGetLayout") or {}
    components = pdp.get("components") or []
    inner = pdp.get("data") or {}

    def find_component(name):
        for c in components:
            if c.get("name") == name:
                return c.get("data", [])
        return []

    product_content = find_component("product_content")
    product_content = product_content[0] if product_content else {}
    product_media_raw = find_component("product_media")
    product_media_raw = product_media_raw[0].get("media", []) if product_media_raw else []
    basic_info = inner.get("basicInfo") or pdp.get("basicInfo") or {}
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

    description = None
    description_element = find_component('product_detail')
    if description_element is not None and isinstance(description_element, list) and len(description_element) > 0:
        detail = description_element[0] or {}
        product_detail_description = detail.get('productDetailDescription') or {}
        if isinstance(product_detail_description, dict):
            description = product_detail_description.get('content')
        if not description:
            content = detail.get('content')
            if content is not None and isinstance(content, list):
                for line in content:
                    if isinstance(line, dict) and line.get('key') == 'deskripsi':
                        description = line.get('subtitle', '')
                        break

    pdpdSession = pdp.get('pdpSession')
    shop_type = json.loads(pdpdSession).get('stier', {}) if pdpdSession else None
    if shop_type is None:
        if product_content.get('isOS'):
            shop_type = 2
        elif product_content.get('isPowerMerchant'):
            shop_type = 3
        else:
            shop_type = 1

    return ProductData(
        product_id=basic_info.get('productID'),
        product_sku = basic_info.get("ttsSKUID"),
        product_name=product_content.get("name", ""),
        url=product_url,
        main_image=basic_info.get("defaultMediaURL"),
        status=basic_info.get("status", ""),
        description=description,
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
        'Accept': 'application/json',
        'Os_version': '26.2.1',
        'X-Method': 'POST',
        'Bd-Device-Id': str(random.randint(10**18, 10**19 - 1)),
        'X-Tkpd-Akamai': 'pdpMainInfoP1',
        'X-Tkpd-Userid': user_id,
        'X-Price-Center': 'true',
        'Content-Type': 'application/json; encoding=utf-8',
        'Accept-Language': 'id;q=1.0, en;q=0.9',
        'User-Agent': 'Tokopedia/2.318.0 (com.tokopedia.Tokopedia; build:202505022018; iOS 18.5.0) Alamofire/2.318.0',
        'Fingerprint-Data': fingerprint,
        'X-App-Version': '2.371.0',
        'X-Tkpd-Path': '/graphql/ProductDetails/getPDPMainInfoP1',
        'X-Device': 'ios-2.371.0',
        'Request-Method': 'POST',
        'X-Theme': 'default',
        'X-Dark-Mode': 'false',
    }

    json_data = {
        'variables': {
            'productID': product_id if product_id else '',
            'layoutID': '',
            'queryParam': '',
            'productKey': product_key if product_key  else '',
            'shopDomain': shop_id if shop_id else '',
            'source': 'P1',
            'userLocation': {
                'addressID': '',
                'addressName': '',
                'latlon': '',
                'postalCode': '',
                'cityID': '',
                'receiverName': '',
                'districtID': '',
            },
        },
        'query': 'query pdpMainInfo($productID: String, $shopDomain: String, $productKey: String, $layoutID: String, $queryParam: String, $source: String, $userLocation: pdpUserLocation) {\n  pdpMainInfo(productID: $productID, shopDomain: $shopDomain, productKey: $productKey, layoutID: $layoutID, queryParam: $queryParam, source: $source, userLocation: $userLocation) {\n    requestID\n    extraPayload\n    data {\n      layoutName\n      basicInfo {\n        ttsPID\n        ttsSKUID\n        ttsShopID\n        shopMultilocation {\n          cityName\n        }\n        isGiftable\n        isTokoNow\n        shopName\n        productID\n        shopID\n        minOrder\n        maxOrder\n        weight\n        weightUnit\n        status\n        url\n        sku\n        needPrescription\n        catalogID\n        isLeasing\n        isBlacklisted\n        totalStockFmt\n        defaultMediaURL\n        menu {\n          id\n          name\n          url\n        }\n        category {\n          id\n          ttsID\n          name\n          title\n          breadcrumbURL\n          isAdult\n          isKyc\n          lastUpdateCategory\n          detail {\n            id\n            name\n            breadcrumbURL\n            isAdult\n          }\n          ttsDetail {\n            id\n            name\n            breadcrumbURL\n            isAdult\n          }\n        }\n        blacklistMessage {\n          title\n          description\n          button\n          buttonArea\n          buttonName\n          url\n          imageURL\n          supportingImage {\n            url\n            width\n            height\n          }\n        }\n        txStats {\n          transactionSuccess\n          transactionReject\n          countSold\n          paymentVerified\n          itemSoldFmt\n        }\n        stats {\n          countReview\n          countTalk\n          rating\n        }\n        weightWording\n      }\n      fomoSocialProofs {\n        name\n        icons\n        text\n        position\n        typeIcon\n        backgroundColor\n      }\n    }\n    components {\n      name\n      type\n      data {\n        ... on pdpDataProductMedia {\n            media {\n              type\n              URLOriginal\n              URLThumbnail\n              description\n              videoURLIOS\n              isAutoplay\n              index\n              variantOptionID\n              URLMaxRes\n            }\n            recommendation {\n              lightIcon\n              darkIcon\n              iconText\n              bottomsheetTitle\n              recommendation\n            }\n            videos {\n              source\n              url\n            }\n            containerType\n            liveIndicator {\n              isLive\n              channelID\n              mediaURL\n              applink\n            }\n            showJumpToVideo\n        }\n        ... on pdpDataOnGoingCampaign {\n          campaign {\n            campaignID\n            campaignType\n            campaignTypeName\n            campaignLogo\n            percentageAmount\n            originalPrice\n            discountedPrice\n            stock\n            stockSoldPercentage\n            threshold\n            startDate\n            endDate\n            endDateUnix\n            appLinks\n            isAppsOnly\n            isActive\n            hideGimmick\n            isCheckImei\n            isUsingOvo\n            background\n            campaignIdentifier\n            paymentInfoWording\n            showStockBar\n          }\n          thematicCampaign {\n            campaignName\n            icon\n            background\n            additionalInfo\n            productID\n            campaignLogo\n            applink\n            superGraphicURL\n          }\n        }\n        ... on pdpDataProductContent {\n            name\n            price {\n              value\n              currency\n              lastUpdateUnix\n              priceFmt\n              slashPriceFmt\n              discPercentage\n              currencyFmt\n              valueFmt\n            }\n            campaign {\n              campaignID\n              campaignType\n              campaignTypeName\n              percentageAmount\n              originalPrice\n              discountedPrice\n              originalStock\n              stock\n              stockSoldPercentage\n              endDateUnix\n              isActive\n              hideGimmick\n              isUsingOvo\n              campaignIdentifier\n              background\n              paymentInfoWording\n              productID\n              campaignLogo\n              showStockBar\n            }\n            thematicCampaign {\n              productID\n              campaignName\n              background\n              icon\n              campaignLogo\n              superGraphicURL\n            }\n            stock {\n              useStock\n              value\n              stockWording\n            }\n            variant {\n              isVariant\n            }\n            isFreeOngkir {\n              isActive\n              imageURL\n            }\n            preorder {\n              duration\n              isActive\n              preorderInDays\n            }\n            isOS\n            isPowerMerchant\n            isWishlist\n            isCOD\n            parentName\n            labelIcons {\n              iconURL\n              label\n            }\n        }\n        ... on pdpDataProductDetail {\n          title\n          content {\n            status\n            key\n            type\n            title\n            subtitle\n            applink\n            showAtFront\n            isAnnotation\n            showAtBottomsheet\n          }\n          productDetailDescription {\n            title\n            content\n          }\n          bottomsheet {\n            actionTitle\n            bottomSheetTitle\n            param\n          }\n        }\n        ... on pdpDataSocialProof {\n          row\n          content {\n            icon\n            title\n            subtitle\n            applink\n          }\n        }\n        ... on pdpDataProductVariant {\n          errorCode\n          parentID\n          defaultChild\n          sizeChart\n          maxFinalPrice\n          landingSubText\n          variants {\n            productVariantID\n            variantID\n            name\n            identifier\n            option {\n              productVariantOptionID\n              variantUnitValueID\n              value\n              hex\n              picture {\n                url\n                url100\n                url200\n              }\n            }\n          }\n          showQtyEditor\n          children {\n            productID\n            price\n            priceFmt\n            slashPriceFmt\n            discPercentage\n            sku\n            optionID\n            productName\n            productURL\n            picture {\n              url\n              url100\n              url200\n            }\n            stock {\n              stock\n              isBuyable\n              stockWording\n              stockWordingHTML\n              minimumOrder\n              maximumOrder\n              stockFmt\n              stockCopy\n              trackerFmt\n            }\n            isCOD\n            isWishlist\n            campaignInfo {\n              campaignID\n              campaignType\n              campaignTypeName\n              discountPercentage\n              originalPrice\n              discountPrice\n              stock\n              stockSoldPercentage\n              endDateUnix\n              appLinks\n              isActive\n              hideGimmick\n              isUsingOvo\n              minOrder\n              campaignIdentifier\n              background\n              paymentInfoWording\n              campaignLogo\n              showStockBar\n            }\n            thematicCampaign {\n              campaignName\n              icon\n              background\n              productID\n              campaignLogo\n              superGraphicURL\n            }\n            subText\n            qtyLabel\n            promo {\n              value\n              iconURL\n              productID\n              promoPriceFmt\n              subtitle\n              applink\n              color\n              background\n              promoType\n              superGraphicURL\n              priceAdditionalFmt\n              separatorColor\n              bottomsheetParam\n              vbsProductVouchers {\n                identifier\n                type\n                text\n                backgroundColor\n                icon\n                borderColor\n                trailingIcon\n              }\n              promoPriceColor\n              promoPriceIcon\n              promoCodes {\n                promoID\n                promoCode\n                promoCodeType\n              }\n              claimContext\n              benefitParam{\n                benefitBreakdowns{\n                  type\n                  amount\n                }\n                promoMetadata\n                promoLabel\n              }\n              identifier\n              slashPriceColor\n              discPercentageColor\n              discPercentageBgColor\n              discPercentageBorderColor\n              discPercentageTransparency\n              backgroundGradientDirection\n              rightSections {\n                contents {\n                  type\n                  value\n                  color\n                  format\n                  gradientDirection\n                  fontType\n                  margin\n                  imageHeight\n                  colorTransparency\n                }\n              }\n              hideCampaignBanner\n              bigSaleName\n            }\n            currencyFmt\n            valuePriceFmt\n            componentPriceType\n            isTopSold\n            labelIcons {\n              iconURL\n              label\n            }\n            ttsPID\n            ttsSKUID\n            qtyLabel\n          }\n          componentType\n          borderColor\n          isGrouped\n          socialProof {\n            bgColor\n            bgGradient\n            contents {\n              name\n              content\n              iconURL\n            }\n          }\n        }\n        ... on pdpDataOneLiner {\n          productID\n          oneLinerContent\n          linkText\n          color\n          applink\n          separator\n          icon\n          isVisible\n          eduLink {\n            appLink\n          }\n        }\n        ... on pdpDataDynamicOneLiner {\n          name\n          text\n          title\n          applink\n          separator\n          icon\n          status\n          chevronPos\n          bgColor\n          chevronColor\n          bgGradient\n          borderColor\n          padding {\n            t\n            b\n          }\n          imageSize {\n            w\n            h\n          }\n        }\n        ... on pdpDataComponentDynamicOneLinerVariant {\n          name\n          text\n          title\n          applink\n          separator\n          icon\n          status\n          chevronPos\n          chevronColor\n          bgGradient\n          borderColor\n          padding {\n            t\n            b\n          }\n          imageSize {\n            w\n            h\n          }\n          bgColor\n        }\n        ... on pdpDataProductDetailMediaComponent {\n          title\n          description\n          contentMedia {\n            url\n            ratio\n          }\n          show\n          ctaText\n        }\n        ... on pdpDataProductListComponent {\n          queryParam\n          thematicID\n        }\n        ... on pdpDataComponentPromoPrice {\n          price {\n            value\n            currency\n            lastUpdateUnix\n            priceFmt\n            slashPriceFmt\n            discPercentage\n            currencyFmt\n            valueFmt\n          }\n          promo {\n            value\n            iconURL\n            productID\n            promoPriceFmt\n            subtitle\n            applink\n            color\n            background\n            promoType\n            superGraphicURL\n            priceAdditionalFmt\n            separatorColor\n            bottomsheetParam\n            promoPriceColor\n            promoPriceIcon\n            promoCodes {\n              promoID\n              promoCode\n              promoCodeType\n            }\n            claimContext\n            benefitParam{\n              benefitBreakdowns{\n                type\n                amount\n              }\n              promoMetadata\n              promoLabel\n            }\n            identifier\n            slashPriceColor\n            discPercentageColor\n            discPercentageBgColor\n            discPercentageBorderColor\n            discPercentageTransparency\n            backgroundGradientDirection\n            rightSections {\n              contents {\n                type\n                value\n                color\n                format\n                gradientDirection\n                fontType\n                margin\n                imageHeight\n                colorTransparency\n              }\n            }\n            hideCampaignBanner\n            bigSaleName\n          }\n          componentPriceType\n        }\n        ... on pdpDataComponentSocialProofV2 {\n          socialProofContent {\n            socialProofType\n            socialProofID\n            title\n            titleEn\n            subtitle\n            icon\n            hasSeparator\n            applink {\n              appLink\n            }\n            bgColor\n            showChevron\n            chevronColor\n            btmDCode\n          }\n        }\n        ... on pdpDataComponentShipmentV4 {\n          data {\n            productID\n            warehouse_info {\n              warehouse_id\n              is_fulfillment\n              district_id\n              postal_code\n              geolocation\n              city_name\n              ttsWarehouseID\n            }\n            useBOVoucher\n            isCOD\n            metadata\n          }\n        }\n        ... on pdpDataComponentSDUIDivKit {\n          template\n        }\n      }\n    }\n  }\n}',
    }
    try:
        response = requests.post(
            'https://gql.tokopedia.com/graphql/ProductDetails/getPDPMainInfoP1',
            headers=headers,
            json=json_data,
            timeout=20,
            impersonate='chrome',
        )
        result_json = response.json()
        product_data = product_details_extractor(result_json)
        if debug:
            logger.detail(f"{product_data.product_id} - {product_data.product_name[0:40]}...")
        return product_data
    except Exception:
        print(traceback.format_exc())
        return None