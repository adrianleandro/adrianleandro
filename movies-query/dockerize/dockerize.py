import argparse
import pprint

import yaml
from services import (
    client,
    credits_unwinder,
    gateway,
    mom,
    onlyoneprodcountry,
    result,
    sharder,
    shared,
    rentability,
    sentiment,
    sentimentanalyzer,
    health
)

import services.counter.average_ratio as average_ratio
import services.counter.top_ranking as top_ranking
import services.filters.year.filter_by_year_after_2000 as filter_by_year_after_2000
import services.filters.year.filter_by_year_before_2010 as filter_by_year_before_2010
import services.selector.moviesselector as moviesselector
import services.selector.yearselector as yearselector
import services.selector.ratingselector as ratingselector
import services.filters.prodcountry.containscountry_ar as containscountry_ar
import services.filters.prodcountry.containscountry_es as containscountry_es
import services.usersplitter.ratingsplitter as ratingsplitter
import services.usersplitter.creditsplitter as creditsplitter
import services.userdispatcher.creditdispatcher as creditdispatcher
import services.userdispatcher.ratingdispatcher as ratingdispatcher
import services.joiner.movieratingjoiner as movieratingjoiner
import services.joiner.moviecreditjoiner as moviecreditjoiner
import services.counter.top_rating as top_rating
import services.counter.top_appearances as top_appearances
import services.health.health as health

PROJECT_NAME = "tp"


def save(path, data):
    with open(path, "w") as file:
        yaml.dump(data, file, default_flow_style=False)


def load_config(path):
    with open(path, "r") as file:
        config = yaml.safe_load(file)
    return config


def parse_args():
    parser = argparse.ArgumentParser(description="Dockerize the project.")
    parser.add_argument(
        "--config",
        type=str,
        default="./config.yml",
        help="Path to the configuration file.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./compose.yml",
        help="Path to the output docker-compose file.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(args.config)

    servs = {
        "mom": mom.mom,
    }

    template = {"name": PROJECT_NAME, "services": servs}

    network = {
        "networks": {
            "tp_net": {
                "ipam": {
                    "config": [{"subnet": "172.25.125.0/24"}],
                    "driver": "default",
                }
            }
        }
    }
    template.update(network)

    gate = gateway.create(
        config["gateway"],
        config["credits_unwinder"],
        config["movies_selector"],
        config["ratings_selector"],
    )
    servs.update(gate)

    clients = client.create(config["client"], config["gateway"])
    servs.update(clients)

    country_ar = containscountry_ar.create(
        config["contains_country_ar"],
        config["filter_by_year_after_2000"],
    )
    servs.update(country_ar)

    country_es = containscountry_es.create(
        config["contains_country_es"],
        config["resultq1"],
    )
    servs.update(country_es)

    _onlyoneprodcountry = shared.create(
        onlyoneprodcountry.data,
        config["onlyoneprodcountry"],
        config["top_ranking"],
    )
    servs.update(_onlyoneprodcountry)

    _credits_unwinder = shared.create(
        credits_unwinder.data,
        config["credits_unwinder"],
        config["creditsplitter"],
    )
    servs.update(_credits_unwinder)

    _moviesselector = moviesselector.create(
        config["movies_selector"],
        config["yearselector"],
        config["top_ranking"],
        config["average_ratio"],
    )
    servs.update(_moviesselector)

    _yearselector = yearselector.create(
        config["ratings_selector"],
        config["filter_by_year_after_2000"],
        config["movieratingsharder"],
        config["moviecreditsharder"],
    )
    servs.update(_yearselector)

    for i in range(5):
        res = result.create(i + 1, config[f"resultq{i+1}"])
        servs.update(res)

    movieratingsharders = sharder.create(
        prefix="movierating",
        index=0,
        inbox_amount=config["movieratingsharder"],
        outbox_amount=config["movieratingjoiner"],
        outbox_domain="movieratingjoiner",
    )
    servs.update(movieratingsharders)

    moviecreditsharders = sharder.create(
        prefix="moviecredit",
        index=0,
        inbox_amount=config["moviecreditsharder"],
        outbox_amount=config["moviecreditjoiner"],
        outbox_domain="moviecreditjoiner",
    )
    servs.update(moviecreditsharders)

    _rentability = shared.create(
        rentability.data,
        config["rentability"],
        config["sentiment"],
    )
    servs.update(_rentability)

    _sentiment = sentiment.create(
        config["sentiment"],
        config["average_ratio"],
    )
    servs.update(_sentiment)

    _average_ratio = average_ratio.create(
        config["average_ratio"],
        config["resultq5"],
    )
    servs.update(_average_ratio)

    _top_ranking = top_ranking.create(config["top_ranking"], config["resultq2"])
    servs.update(_top_ranking)

    _filter_by_year_after_2000 = filter_by_year_after_2000.create(
        config["filter_by_year_after_2000"],
        config["yearselector"],
    )
    servs.update(_filter_by_year_after_2000)

    _filter_by_year_before_2010 = filter_by_year_before_2010.create(
        config["filter_by_year_before_2010"],
        config["contains_country_es"],
    )
    servs.update(_filter_by_year_before_2010)

    _ratingselector = ratingselector.create(
        config["ratings_selector"],
        config["ratingsplitter"],
    )
    servs.update(_ratingselector)

    _ratingsplitter = ratingsplitter.create(
        config["ratingsplitter"],
    )
    servs.update(_ratingsplitter)

    _creditsplitter = creditsplitter.create(
        config["creditsplitter"],
    )
    servs.update(_creditsplitter)

    _creditdispatcher = creditdispatcher.create(
        config["creditdispatcher"],
        config["moviecreditsharder"],
    )
    servs.update(_creditdispatcher)

    _ratingdispatcher = ratingdispatcher.create(
        config["ratingdispatcher"],
        config["movieratingsharder"],
    )
    servs.update(_ratingdispatcher)

    _moviecreditjoiner = moviecreditjoiner.create(
        config["moviecreditjoiner"],
        config["top_appearances"],
        config["creditdispatcher"],
    )
    servs.update(_moviecreditjoiner)

    _movieratingjoiner = movieratingjoiner.create(
        config["movieratingjoiner"],
        config["top_rating"],
        config["ratingdispatcher"],
    )
    servs.update(_movieratingjoiner)

    _top_rating = top_rating.create(
        config["top_rating"],
        config["resultq3"],
    )
    servs.update(_top_rating)

    _top_appearances = top_appearances.create(
        config["top_appearances"],
        config["resultq4"],
    )
    servs.update(_top_appearances)

    _health = health.create(
        config["health"],
    )
    servs.update(_health)

    servs.update(sentimentanalyzer.create())


    save(args.output, template)


if __name__ == "__main__":
    main()
