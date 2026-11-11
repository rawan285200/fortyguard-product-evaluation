import os
import time
import json
from pathlib import Path
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

API_KEY = os.getenv("FORTYGUARD_API_KEY")
BASE_URL = os.getenv(
    "BASE_URL",
    "https://api.fortyguard.com"
).rstrip("/")

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 5))
MAX_POLL_ATTEMPTS = int(
    os.getenv("MAX_POLL_ATTEMPTS", 120)
)

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)


class FortyGuardClient:

    def __init__(self):

        if not API_KEY:
            raise ValueError(
                "FORTYGUARD_API_KEY is missing. "
                "Check your .env file."
            )

        self.base_url = BASE_URL

        self.headers = {
            "api-key": API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    @staticmethod
    def build_heatmap_payload():

        start_date = os.getenv(
            "HEATMAP_START_DATE",
            "2024-07-15"
        )

        start_time = os.getenv(
            "HEATMAP_START_TIME",
            "14:00"
        )

        filter_type = int(
            os.getenv("HEATMAP_FILTER_TYPE", 1)
        )

        granularity = int(
            os.getenv("HEATMAP_GRANULARITY", 100)
        )

        coordinates = [
            [-74.0170, 40.7050],
            [-74.0030, 40.7050],
            [-74.0030, 40.7180],
            [-74.0170, 40.7180],
            [-74.0170, 40.7050]
        ]

        return {
            "polygon_aoi": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {},
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                coordinates
                            ]
                        }
                    }
                ]
            },
            "date_time": {
                "start_date": start_date,
                "start_time": start_time,
                "filter_type": filter_type
            },
            "granularity": granularity
        }

    def submit_heatmap(self, payload):

        url = f"{self.base_url}/v1/heatmap"

        print("\nSubmitting Heatmap request...")

        start_time = time.perf_counter()

        # Do not automatically retry POST requests:
        # a retry could create a duplicate paid activity.
        response = self.session.post(
            url,
            json=payload,
            timeout=60
        )

        elapsed = time.perf_counter() - start_time

        print(f"HTTP Status: {response.status_code}")
        print(f"Response Time: {elapsed:.3f} seconds")

        if not response.ok:
            print("\nAPI ERROR DETAILS:")
            print(response.text)
            response.raise_for_status()

        data = response.json()

        activity_id = (
            data.get("data", {}).get("activity_id")
            if isinstance(data.get("data"), dict)
            else data.get("activity_id")
        )

        if not activity_id:
            raise ValueError(
                "The response did not contain an activity_id."
            )

        print("Heatmap submitted successfully!")
        print(f"Activity ID: {activity_id}")

        self.save_result(
            "submission",
            {
                "activity_id": activity_id,
                "http_status": response.status_code,
                "response_time_seconds": round(elapsed, 3),
                "response": data
            }
        )

        return activity_id

    def get_status(self, activity_id):

        url = (
            f"{self.base_url}/v1/status/{activity_id}"
        )

        response = self.session.get(
            url,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    def poll_status(self, activity_id):

        print("\nMonitoring Heatmap activity...")

        for attempt in range(1, MAX_POLL_ATTEMPTS + 1):

            try:
                result = self.get_status(activity_id)

            except requests.HTTPError as error:

                # The official guide notes that 404 may
                # occur temporarily immediately after submission.
                if (
                    error.response is not None
                    and error.response.status_code == 404
                ):
                    print(
                        f"Attempt {attempt}: "
                        "Activity not available yet."
                    )
                    time.sleep(POLL_INTERVAL)
                    continue

                raise

            data = result.get("data", result)

            status = str(
                data.get("status", "unknown")
            ).lower()

            print(
                f"Attempt {attempt}: Status = {status}"
            )

            if status in ("completed", "succeeded"):

                print("\nHeatmap completed successfully!")

                self.save_result(
                    "completed",
                    {
                        "activity_id": activity_id,
                        "status": status,
                        "result": result
                    }
                )

                return result

            if status in ("failed", "error"):

                self.save_result(
                    "failed",
                    {
                        "activity_id": activity_id,
                        "status": status,
                        "result": result
                    }
                )

                raise RuntimeError(
                    f"Heatmap activity failed: {activity_id}"
                )

            time.sleep(POLL_INTERVAL)

        raise TimeoutError(
            "Maximum polling attempts reached."
        )

    @staticmethod
    def save_result(name, content):

        timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%d_%H%M%S")

        filename = (
            RESULTS_DIR /
            f"{name}_{timestamp}.json"
        )

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                content,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(f"Saved result: {filename}")