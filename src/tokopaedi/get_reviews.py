from curl_cffi import requests
import logging
import traceback
from .tokopaedi_types import ProductReview
from .custom_logging import setup_custom_logging
from .get_fingerprint import randomize_fp

logger = setup_custom_logging()

def extract_reviews(json_data):
    reviews = []
    
    data = json_data.get("data", {})
    productrev_list = data.get("productrevGetProductReviewList", {})
    items = productrev_list.get("list", [])
    
    if not items:
        return reviews

    for item in items:
        images = item.get("imageAttachments", [])
        videos = item.get("videoAttachments", [])
        like_dislike = item.get("likeDislike", {})
        user = item.get("user", {})
        review_response = item.get("reviewResponse", {})

        review = ProductReview(
            feedback_id=int(item.get("feedbackID", 0)),
            variant_name=item.get("variantName", ""),
            message=item.get("message", ""),
            rating=float(item.get("productRating", 0)),
            review_age=item.get("reviewCreateTimestamp", ""),
            user_full_name=user.get("fullName", ""),
            user_url=user.get("url", ""),
            response_message=review_response.get("message", ""),
            response_created_text=review_response.get("createTime", ""),
            images=[img.get("imageUrl", "") for img in images],
            videos=[v for v in videos],
            likes=like_dislike.get("totalLike", 0),
        )
        reviews.append(review)

    return reviews

def get_reviews(product_id, max_result=10, page=1, result_count=0, debug=False):
    product_id = str(product_id)
    headers = {
        'Host': 'gql.tokopedia.com',
        'Fingerprint-Data': randomize_fp(),
        'X-Tkpd-Path': '/graphql/ProductReview/getProductReviewReadingList',
        'X-Device': 'ios-2.318.0',
        'Request-Method': 'POST',
        'X-Method': 'POST',
        'Accept-Language': 'id;q=1.0, en;q=0.9',
        'User-Agent': 'Tokopedia/2.318.0 (com.tokopedia.Tokopedia; build:202505022018; iOS 18.5.0) Alamofire/2.318.0',
        'Content-Type': 'application/json; encoding=utf-8',
        'X-App-Version': '2.318.0',
        'Accept': 'application/json',
        'X-Dark-Mode': 'true',
        'X-Theme': 'default',
        'X-Price-Center': 'true',
    }

    json_data = {
        'query': 'query productrevGetProductReviewList($productID: String!, $page: Int!, $limit: Int!, $sortBy: String,\n$filterBy: String, $opt: String) {\nproductrevGetProductReviewList(productID: $productID, page: $page, limit: $limit, sortBy: $sortBy,\nfilterBy: $filterBy, opt: $opt) {\nlist {\nfeedbackID\nvariantName\nmessage\nproductRating\nreviewCreateTime\nreviewCreateTimestamp\nisAnonymous\nisReportable\nreviewResponse {\nmessage\ncreateTime\n}\nuser {\nuserID\nfullName\nimage\nurl\nlabel\n}\nimageAttachments {\nattachmentID\nimageThumbnailUrl\nimageUrl\n}\nvideoAttachments {\nattachmentID\nvideoUrl\n}\nlikeDislike {\ntotalLike\nlikeStatus\n}\nstats {\nkey\nformatted\ncount\n}\nbadRatingReasonFmt\n}\nshop {\nshopID\nname\nurl\nimage\n}\nvariantFilter {\nisUnavailable\nticker\n}\nhasNext\n}\n}',
        'variables': {
            'productID': product_id,
            'page': page,
            'filterBy': '',
            'opt': '',
            'limit': 10,
            'sortBy': 'informative_score desc',
        },
    }

    try:
        response = requests.post(
            'https://gql.tokopedia.com/graphql/ProductReview/getProductReviewReadingList',
            headers=headers,
            json=json_data,
            verify=False,
        )
        result_json = response.json()
        has_next = result_json.get('data', {}).get('productrevGetProductReviewList', {}).get('hasNext', False)
        current_result =  extract_reviews(result_json)
        if current_result:
            result_count += len(current_result)
            if result_count >= max_result:
                return current_result

            if debug:
                for line in current_result:
                    review_message = line.message.replace('\n','')[0:40]
                    logger.reviews(f"{line.feedback_id} - {review_message}...")

            next_result = get_reviews(
                    product_id = product_id,
                    max_result = max_result,
                    page = page+1,
                    result_count = result_count,
                    debug = debug
                )
            return current_result+next_result
        return current_result
    except:
        print(traceback.format_exc())
        return None