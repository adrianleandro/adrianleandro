import subprocess
import random
import yaml
import time


def docker_kill(container):
    return subprocess.run(
        ["docker", "compose", "kill", container],
        check=True,
        capture_output=True,
        text=True,
    )


def docker_run(container):
    return subprocess.run(
        ["docker", "compose", "up", container, "--detach"],
        check=True,
        capture_output=True,
        text=True,
    )


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(description="Kill a Docker container.")
    parser.add_argument(
        "--compose", help="Path to the docker-compose file", required=True
    )
    parser.add_argument(
        "--times",
        help="Number of times to kill a random container",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--seed",
        help="Random seed for reproducibility",
        type=int,
        default=123,
    )
    return parser.parse_args()


def load_compose(path):
    with open(path, "r") as file:
        return yaml.safe_load(file)


def main():
    args = parse_args()
    compose = load_compose(args.compose)
    services = compose.get("services", {}).keys()
    random.seed(args.seed)

    filtered_services = []
    for service in services:
        if service.startswith("client") or service.startswith("gateway") or service.startswith("mom") or service.startswith("sentimentanalyzer"):
            continue
        filtered_services.append(service)

    selected = random.sample(
        list(filtered_services), min(args.times, len(filtered_services))
    )
    print(f"Selected containers to kill: {selected}")

    events = []
    for selected_container in selected:
        events.append({"container": selected_container, "events": ["kill"]})

    while len(events) > 0:
        random_event = random.choice(events)
        if len(random_event["events"]) == 0:
            print(f"No more events for container: {random_event['container']}")
            events.remove(random_event)
            continue

        container = random_event["container"]
        current_event = random_event["events"].pop(0)
        if current_event == "kill":
            print(f"Killing container: {container}")
            print(docker_kill(container))
        elif current_event == "run":
            print(f"Running container: {container}")
            print(docker_run(container))

        sleeping_time = random.uniform(0.5, 2.0)
        print(f"Sleeping for {sleeping_time:.2f} seconds")
        time.sleep(sleeping_time)


if __name__ == "__main__":
    main()
