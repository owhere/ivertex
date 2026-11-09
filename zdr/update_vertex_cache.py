#!/usr/bin/env python3
"""
Verify and configure Vertex AI context caching settings.

Examples:
    # 1. Read / verify only
    python3 check_vertex_cache.py -p <PROJECT_ID> -r us-east1

    # 2. In-Memory: Enabled, Durable: Disabled (ZDR Ephemeral target)
    python3 check_vertex_cache.py -p <PROJECT_ID> -r us-east1 \
        --in-memory enabled --durable disabled

    # 3. Both Enabled (GCP default)
    python3 check_vertex_cache.py -p <PROJECT_ID> -r us-east1 \
        --in-memory enabled --durable enabled

    # 4. Turn off all caching
    python3 check_vertex_cache.py -p <PROJECT_ID> -r us-east1 \
        --in-memory disabled --durable disabled
"""

import argparse
import sys
import google.auth
from google.auth.transport.requests import AuthorizedSession


def get_session():
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    return AuthorizedSession(credentials)


def get_cache_config(session: AuthorizedSession, project_id: str, region: str) -> dict:
    endpoint = f"https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/cacheConfig"
    response = session.get(endpoint)
    if response.status_code == 404:
        return {}
    if not response.ok:
        sys.exit(f"Error fetching cacheConfig ({response.status_code}): {response.text}")
    return response.json()

def update_cache_config(session: AuthorizedSession, project_id: str, region: str, in_memory: str, durable: str) -> dict:
    in_mem_bool = in_memory.lower() == "enabled"
    durable_bool = durable.lower() == "enabled"

    if not in_mem_bool and durable_bool:
        sys.exit(
            "Invalid configuration: Durable caching cannot be 'enabled' while In-Memory caching is 'disabled'."
        )

    endpoint = f"https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/cacheConfig"

    if not in_mem_bool:
        payload = {
            "name": f"projects/{project_id}/cacheConfig",
            "disableCache": True
        }
        params = {"updateMask": "disable_cache"}
    else:
        payload = {
            "name": f"projects/{project_id}/cacheConfig",
            "disableCache": False,
            "retentionConfig": {
                "retentionType": "DURABLE" if durable_bool else "EPHEMERAL"
            }
        }
        params = {"updateMask": "disable_cache,retention_config"}

    # Include updateMask in query params so the API persists retentionConfig
    response = session.patch(endpoint, params=params, json=payload)
    if not response.ok:
        sys.exit(f"Error updating cacheConfig ({response.status_code}): {response.text}")

    print("\n>>> Configuration update successful.")
    
    # Always fetch the live state via GET to guarantee accurate verification
    return get_cache_config(session, project_id, region)


def evaluate_cache_status(config: dict):
    # Unpack LRO wrapper if present
    if "response" in config and isinstance(config["response"], dict):
        config = config["response"]

    disable_cache = config.get("disableCache", False)
    retention_type = config.get("retentionConfig", {}).get("retentionType", "DURABLE")

    print("\n" + "=" * 58)
    print(" VERTEX AI CONTEXT CACHING STATUS")
    print("=" * 58)

    if disable_cache:
        in_memory_status = "DISABLED"
        durable_status = "DISABLED"
        summary = "All implicit caching is completely disabled."
    else:
        in_memory_status = "ENABLED"
        if retention_type == "EPHEMERAL":
            durable_status = "DISABLED (Ephemeral Only - Compliant with ZDR)"
            summary = "In-memory caching is active. Evicted context is NOT saved to disk."
        else:
            durable_status = "ENABLED (Up to 24h at rest)"
            summary = "Both in-memory and durable storage at rest are active."

    print(f" Raw Response Payload : {config if config else 'Default (Unset)'}")
    print("-" * 58)
    print(f" In-Memory Caching    : {in_memory_status}")
    print(f" Durable Caching      : {durable_status}")
    print(f" Retention Type       : {retention_type if not disable_cache else 'N/A'}")
    print("-" * 58)
    print(f" Status Summary       : {summary}")
    print("=" * 58 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Verify or adjust Vertex AI in-memory and durable cache configuration."
    )
    parser.add_argument(
        "--project-id", "-p", required=True, help="Google Cloud Project ID"
    )
    parser.add_argument(
        "--region", "-r", required=True, help="Vertex AI region (e.g. us-east1, europe-west2)"
    )
    parser.add_argument(
        "--in-memory",
        choices=["enabled", "disabled"],
        help="Control in-memory caching tier",
    )
    parser.add_argument(
        "--durable",
        choices=["enabled", "disabled"],
        help="Control durable at-rest caching tier",
    )

    args = parser.parse_args()
    session = get_session()

    # If any update flag is provided, both must be specified to prevent ambiguous states
    if (args.in_memory is not None) ^ (args.durable is not None):
        sys.exit("Error: When updating, please specify both --in-memory and --durable flags.")

    if args.in_memory and args.durable:
        config = update_cache_config(
            session, args.project_id, args.region, args.in_memory, args.durable
        )
    else:
        config = get_cache_config(session, args.project_id, args.region)

    evaluate_cache_status(config)


if __name__ == "__main__":
    main()
