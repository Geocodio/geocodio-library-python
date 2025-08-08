#!/usr/bin/env python3

import os
import time
import logging
from geocodio import Geocodio
from geocodio.models import ListProcessingState
from dotenv import load_dotenv

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("smoke_lists")


def print_headers_and_body(label, headers, body):
    logger.info(f"{label} headers: {headers}")
    # Only print body if not raw bytes
    if isinstance(body, (bytes, bytearray)):
        try:
            decoded = body.decode("utf-8")
            logger.info(f"{label} body (decoded):\n{decoded}")
        except Exception:
            logger.info(f"{label} body: <binary data>")
    else:
        logger.info(f"{label} body:\n{body}")


def wait_for_list_processed(client, list_id, timeout=120):
    logger.info(f"Waiting for list {list_id} to be processed...")
    start = time.time()
    while time.time() - start < timeout:
        list_response = client.get_list(list_id)
        list_processing_state = list_response.status.get('state')
        logger.debug(f"List status: {list_processing_state}")
        if list_processing_state == ListProcessingState.COMPLETED:
            logger.info(f"List processed. {list_processing_state}")
            return list_response
        elif list_processing_state == ListProcessingState.FAILED:
            print()  # Finish the dots line
            raise RuntimeError(f"List {list_id} failed to process.")
        elif list_processing_state == ListProcessingState.PROCESSING:
            print("=>", end="", flush=True)
        time.sleep(2)
    raise TimeoutError(f"List {list_id} did not process in {timeout} seconds.")


def main():
    load_dotenv()
    api_key = os.getenv("GEOCODIO_API_KEY")
    if not api_key:
        logger.error("GEOCODIO_API_KEY not set in environment.")
        exit(1)

    client = Geocodio(api_key)

    # Step 1: Create a list
    logger.info("Creating a new list...")
    file_content = "Zip\n20003\n20001"
    # --- Capture request details ---
    logger.info("REQUEST: POST /v1.9/lists")
    logger.info(f"Request params: {{'api_key': '***', 'direction': 'forward', 'format': '{{A}}'}}")
    logger.info(f"Request files: {{'file': ('smoke_test_list.csv', {repr(file_content)})}}")
    new_list_response = client.create_list(
        file=file_content,
        filename="smoke_test_list.csv",
        format_="{{A}}"
    )
    # --- Capture response details ---
    logger.info("RESPONSE: POST /v1.9/lists")
    print_headers_and_body("Response", {
        "id": new_list_response.id,
        "file": new_list_response.file,
        "status": new_list_response.status,
        "download_url": new_list_response.download_url,
        "expires_at": new_list_response.expires_at,
    }, new_list_response.http_response.content)

    logger.info(f"Created list: {new_list_response.id}, status: {new_list_response.status}")

    # Step 2: Wait for processing
    wait_for_list_processed(client, new_list_response.id)

    # Step 3: Download the list as bytes
    logger.info(f"Downloading list as bytes for list ID: {new_list_response.id}")
    file_bytes = client.download(list_id=new_list_response.id)
    # dump some info about the bytes to the log
    logger.info(f"Downloaded {len(file_bytes)} bytes from list ID: {new_list_response.id}")

    # Step 4: Download the list to a file
    out_path = os.path.abspath("/tmp/smoke_test_download.csv")
    logger.info(f"Downloading list to file: {out_path}")
    file_path = client.download(list_id=new_list_response.id, filename=out_path)
    # log the file size in bytes
    file_size = os.path.getsize(file_path)
    logger.info(f"File of size {file_size}b saved to: {file_path}")

    # Step 5: Show file content
    with open(file_path, "r") as f:
        logger.info("Downloaded file content:")
        print(f.read())


if __name__ == "__main__":
    main()
