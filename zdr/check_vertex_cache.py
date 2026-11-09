#!/usr/bin/env python3
"""
Verify Vertex AI context caching settings (In-Memory vs. Durable).
Usage:
    python check_vertex_cache.py --project-id <PROJECT_ID> --region <REGION>
"""

import argparse
import sys
import google.auth
from google.auth.transport.requests import AuthorizedSession


def get_cache_config(project_id: str, region: str) -> dict:
    """Fetch current CacheConfig from the regional Vertex AI v1 endpoint."""
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    authed_session = AuthorizedSession(credentials)

    endpoint = f"https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/cacheConfig"
    
    response = authed_session.get(endpoint)
    
    if response.status_code == 404:
        # Not found / never modified means GCP default applies
        return {}
    
    if not response.ok:
        sys.exit(f"Error fetching cacheConfig ({response.status_code}): {response.text}")

    return response.json()


def evaluate_cache_status(config: dict):
    """
    Parses CacheConfig payload:
      - disableCache: bool (default: False)
      - retentionConfig.retentionType: "DURABLE" | "EPHEMERAL" (default: "DURABLE")
    """
    disable_cache = config.get("disableCache", False)
    retention_type = config.get("retentionConfig", {}).get("retentionType", "DURABLE")

    print("\n" + "=" * 55)
    print(" VERTEX AI CONTEXT CACHING VERIFICATION")
    print("=" * 55)

    if disable_cache:
        in_memory_status = "DISABLED"
        durable_status = "DISABLED"
        summary = "All implicit caching is completely disabled."
    else:
        in_memory_status = "ENABLED"
        if retention_type == "EPHEMERAL":
            durable_status = "DISABLED (Ephemeral Only - Compliant with ZDR)"
            summary = "In-memory caching is active. Evicted context will NOT be stored on durable disk."
        else:
            durable_status = "ENABLED (Up to 24h at rest)"
            summary = "Both in-memory and durable storage at rest are active (GCP Default)."

    print(f" Raw Response Payload : {config if config else 'Default (Unset)'}")
    print("-" * 55)
    print(f" In-Memory Caching    : {in_memory_status}")
    print(f" Durable Caching      : {durable_status}")
    print(f" Retention Type       : {retention_type if not disable_cache else 'N/A'}")
    print("-" * 55)
    print(f" Status Summary       : {summary}")
    print("=" * 55 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Verify Vertex AI in-memory and durable cache configuration."
    )
    parser.add_argument(
        "--project-id", "-p", required=True, help="Google Cloud Project ID"
    )
    parser.add_argument(
        "--region", "-r", required=True, help="Vertex AI region (e.g., europe-west2, us-central1)"
    )

    args = parser.parse_args()
    config = get_cache_config(args.project_id, args.region)
    evaluate_cache_status(config)


if __name__ == "__main__":
    main()
