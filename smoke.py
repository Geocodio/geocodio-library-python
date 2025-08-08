#!/usr/bin/env python3

from geocodio import Geocodio
from dotenv import load_dotenv
import os
import json
from dataclasses import asdict

# Load environment variables from .env file
load_dotenv()

# Initialize the client with your API key
client = Geocodio(os.getenv("GEOCODIO_API_KEY"))

# Single forward geocode
print("\nSingle forward geocode:")
response = client.geocode("3730 N Clark St, Chicago, IL")
print(json.dumps(asdict(response), indent=2))

# Batch forward geocode
print("\nBatch forward geocode:")
addresses = [
    "3730 N Clark St, Chicago, IL",
    "638 E 13th Ave, Denver, CO"
]
batch_response = client.geocode(addresses)
print(json.dumps(asdict(batch_response), indent=2))

# Single reverse geocode
print("\nSingle reverse geocode:")
rev = client.reverse("38.9002898,-76.9990361")
print(json.dumps(asdict(rev), indent=2))

# Append additional fields
print("\nGeocode with additional fields:")
data = client.geocode(
    "3730 N Clark St, Chicago, IL",
    fields=["cd", "timezone"]
)
print(json.dumps(asdict(data), indent=2))