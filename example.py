from tokopaedi import search, SearchFilters, get_product, get_reviews, combine_data
import json

filters = SearchFilters(
            bebas_ongkir_extra = True,
            pmin = 15000000,
            pmax = 30000000,
            rt = 4.5
        )

results = search("Zenbook 14 32GB", max_result=100, debug=True)
for result in results:
    combine_data(
        result,
        get_product(product_id=result.product_id, debug=True),
        get_reviews(product_id=result.product_id, max_result=20, debug=True)
    )

with open('log.json','w') as f:
    f.write(json.dumps(results.json(), indent=4))