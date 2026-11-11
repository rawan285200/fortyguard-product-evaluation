import argparse
import json
import time

import requests

from  fortygraud_client import FortyGuardClient


def main():

    parser = argparse.ArgumentParser(
        description="FortyGuard API Product Evaluation"
    )

    parser.add_argument(
        "--submit",
        action="store_true",
        help="Submit a real Heatmap request"
    )

    args = parser.parse_args()

    if not args.submit:
        print(
            "No API request was sent.\n"
            "Use --submit to start a real Heatmap task."
        )
        return

    client = FortyGuardClient()

    payload = client.build_heatmap_payload()

    print("\n========== REQUEST DETAILS ==========")

    print(
        json.dumps(
            payload,
            indent=4
        )
    )

    print("\n=====================================")

    confirmation = input(
        "\nThis request may consume API credits."
        "\nDo you want to continue? (yes/no): "
    )

    if confirmation.strip().lower() != "yes":
        print("Request cancelled.")
        return

    try:

        activity_id = client.submit_heatmap(
            payload
        )

        result = client.poll_status(
            activity_id
        )

        print("\n========== FINAL RESULT ==========")

        print(
            json.dumps(
                result,
                indent=4,
                ensure_ascii=False
            )
        )

        print("\nEvaluation completed.")

    except requests.HTTPError as error:

        status_code = (
            error.response.status_code
            if error.response is not None
            else "Unknown"
        )

        print(f"\nHTTP Error: {status_code}")
        print(error)

    except requests.RequestException as error:

        print("\nNetwork error:")
        print(error)

    except (ValueError, RuntimeError, TimeoutError) as error:

        print(f"\nEvaluation error: {error}")


if __name__ == "__main__":
    main()