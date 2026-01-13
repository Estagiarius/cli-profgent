# Author: Victor Hugo Garcia de Oliveira
# Date: 2025-12-21
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
import keyring
import json
from app.core.config import CONFIG_DIR

# The service name under which the credentials will be stored.
# In a real application, this should be unique to your app.
APP_NAME = "academic-management-app"
SECRETS_FILE = CONFIG_DIR / "secrets.json"

def _save_to_file(service_name: str, api_key: str):
    """Fallback: Saves API key to a local JSON file."""
    try:
        data = {}
        if SECRETS_FILE.exists():
            with open(SECRETS_FILE, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    pass

        data[service_name] = api_key

        with open(SECRETS_FILE, "w") as f:
            json.dump(data, f, indent=4)
        print(f"API key for {service_name} saved to file (fallback).")
    except Exception as e:
        print(f"Error saving API key to file: {e}")

def _get_from_file(service_name: str) -> str | None:
    """Fallback: Retrieves API key from a local JSON file."""
    if not SECRETS_FILE.exists():
        return None
    try:
        with open(SECRETS_FILE, "r") as f:
            data = json.load(f)
            return data.get(service_name)
    except Exception as e:
        print(f"Error retrieving API key from file: {e}")
        return None

def save_api_key(service_name: str, api_key: str):
    """
    Saves an API key for a given service in the system's secure keychain.
    Falls back to a local file if keyring is unavailable.

    Args:
        service_name: The name of the service (e.g., 'OpenAI').
        api_key: The API key to store.
    """
    try:
        keyring.set_password(APP_NAME, service_name, api_key)
        print(f"API key for {service_name} saved successfully via keyring.")
    except Exception as e:
        # Handle potential errors with the keyring backend
        print(f"Keyring error ({e}). Using file fallback.")
        _save_to_file(service_name, api_key)

def get_api_key(service_name: str) -> str | None:
    """
    Retrieves an API key for a given service from the system's secure keychain.
    Falls back to a local file if keyring is unavailable.

    Args:
        service_name: The name of the service (e.g., 'OpenAI').

    Returns:
        The API key as a string, or None if it's not found or an error occurs.
    """
    try:
        val = keyring.get_password(APP_NAME, service_name)
        if val is not None:
            return val
        # If keyring returns None, it might just be empty, or not working.
        # Check file fallback just in case.
        return _get_from_file(service_name)
    except Exception as e:
        # Handle potential errors with the keyring backend
        print(f"Keyring error ({e}). Using file fallback.")
        return _get_from_file(service_name)
