"""
Example script demonstrating the List API functionality.

This script shows how to use the List API to manage lists of addresses
and geocode them in batch.
"""

from geocodio import GeocodioClient
from dotenv import load_dotenv
import os
import json
from dataclasses import asdict

# Load environment variables from .env file
load_dotenv()

# Initialize the client with your API key
client = GeocodioClient(os.getenv("GEOCODIO_API_KEY"))

# Create a new list
print("\nCreating a new list...")
new_list = client.create_list(format_="{{A}}")
print(f"Created list with ID: {new_list.list.id}")
print(f"List name: {new_list.list.name}")
print(f"List description: {new_list.list.description}")
print(f"Number of items: {new_list.list.item_count}")

# Get all lists
print("\nRetrieving all lists...")
lists = client.get_lists()
print(f"Found {len(lists.lists)} lists:")
for list_obj in lists.lists:
    print(f"  - {list_obj.name} (ID: {list_obj.id}, Items: {list_obj.item_count})")

# Get a specific list
list_id = new_list.list.id
print(f"\nRetrieving list with ID: {list_id}...")
list_details = client.get_list(list_id)
print(f"List name: {list_details.list.name}")
print(f"List description: {list_details.list.description}")
print(f"Number of items: {list_details.list.item_count}")
print("Items:")
for item in list_details.list.items:
    print(f"  - {item.query} (ID: {item.id})")

# Update the list
print("\nUpdating the list...")
updated_list = client.update_list(
    list_id=list_id,
    name="Updated Example Addresses",
    description="An updated list of example addresses"
)
print(f"Updated list name: {updated_list.list.name}")
print(f"Updated list description: {updated_list.list.description}")

# Add more items to the list
print("\nAdding more items to the list...")
added_items = client.add_items_to_list(
    list_id=list_id,
    items=[
        "123 Main St, Chicago, IL",
        "456 Oak St, Los Angeles, CA"
    ]
)
print(f"Added {len(added_items.items)} items:")
for item in added_items.items:
    print(f"  - {item.query} (ID: {item.id})")

# Geocode all items in the list
print("\nGeocoding all items in the list...")
geocoded_list = client.geocode_list(
    list_id=list_id,
    fields=["timezone", "cd"]
)
print(f"Geocoded {len(geocoded_list.list.items)} items:")
for item in geocoded_list.list.items:
    if item.result:
        print(f"  - {item.query} => {item.result.formatted_address}")
        print(f"    Location: {item.result.location.lat}, {item.result.location.lng}")
        if item.result.fields and item.result.fields.timezone:
            print(f"    Timezone: {item.result.fields.timezone.name}")
        if item.result.fields and item.result.fields.congressional_districts:
            districts = item.result.fields.congressional_districts
            for district in districts:
                print(f"    Congressional District: {district.name}")
    else:
        print(f"  - {item.query} => Not geocoded")

# Remove some items from the list
print("\nRemoving items from the list...")
item_ids = [added_items.items[0].id]  # Remove the first added item
client.remove_items_from_list(
    list_id=list_id,
    item_ids=item_ids
)
print(f"Removed {len(item_ids)} items")

# Get the updated list
print("\nRetrieving the updated list...")
updated_list = client.get_list(list_id)
print(f"Number of items: {updated_list.list.item_count}")
print("Items:")
for item in updated_list.list.items:
    print(f"  - {item.query} (ID: {item.id})")

# Clean up by deleting the list
print("\nDeleting the list...")
client.delete_list(list_id)
print(f"Deleted list with ID: {list_id}")

# Verify the list was deleted
print("\nVerifying the list was deleted...")
lists = client.get_lists()
list_exists = any(list_obj.id == list_id for list_obj in lists.lists)
print(f"List still exists: {list_exists}")

print("\nList API example completed successfully!")