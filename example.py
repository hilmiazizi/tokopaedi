from tokopaedi import search, SearchFilters, get_product, get_reviews
import json

filters = SearchFilters(
            bebas_ongkir_extra = True,
            pmin = 15000000,
            pmax = 25000000,
            rt = 4.5
        )

results = search("Asus Zenbook S14 32GB", max_result=10, debug=True, filters=filters)
results.enrich_details(debug=True)
results.enrich_reviews(max_result=50, debug=True)

with open('log.json','w') as f:
    f.write(json.dumps(results.json(), indent=4))
print(results.json())
exit()