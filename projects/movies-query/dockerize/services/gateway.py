import copy
import services.shared as shared

gateway = {
    "container_name": "gateway_{ID}",
    "image": "gateway:latest",
    "environment": {
        "ID": 0,
        "CREDITS_DOMAIN":"credits_unwinder",
        "CREDITS_AMOUNT": 0,
        "MOVIES_DOMAIN": "moviesselector",
        "MOVIES_AMOUNT": 0,
        "RATINGS_DOMAIN": "ratingselector",
        "RATINGS_AMOUNT": 0,
        "RESULTS_AMOUNT": 5,
    },
}


def create(
    gateway_amount,
    credits_unwinder_amount,
    movies_selector_amount,
    ratings_selector_amount,
):
    services = {}
    for i in range(gateway_amount):
        item = copy.deepcopy(shared.base)
        gate = copy.deepcopy(gateway)
        item.update(gate)
        item["container_name"] = item["container_name"].format(ID=i)
        item["environment"]["INBOX_DOMAIN"] = "gateway"
        item["environment"]["ID"] = i
        item["environment"]["CREDITS_AMOUNT"] = credits_unwinder_amount
        item["environment"]["MOVIES_AMOUNT"] = movies_selector_amount
        item["environment"]["RATINGS_AMOUNT"] = ratings_selector_amount
        services[item["container_name"]] = item
    return services
