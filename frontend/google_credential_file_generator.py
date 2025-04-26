import json
import os
import tempfile

from dotenv import load_dotenv

load_dotenv()


def get_google_credentials(env_var_name: str = "GOOGLE_CREDENTIALS_JSON") -> str:
    """
    Fetches JSON credentials from the given environment variable,
    writes them to a temporary file named 'google_credentials.json',
    and returns the file path.

    :param env_var_name: Name of the environment variable containing JSON credentials.
    :return: Path to the temporary JSON file.
    :raises EnvironmentError: If the env var is missing or empty.
    :raises ValueError: If the env var contents are not valid JSON.
    """
    # 1. Retrieve from environment
    credentials_json = os.getenv(env_var_name)
    if not credentials_json:
        raise EnvironmentError(
            f"Environment variable '{env_var_name}' is not set or is empty."
        )

    # 2. Validate JSON
    try:
        json.loads(credentials_json)
    except json.JSONDecodeError as ex:
        raise ValueError(f"Invalid JSON in environment variable '{env_var_name}': {ex}")

    # 3. Write to temp file
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, "google_credentials.json")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(credentials_json)

    # 4. Return the path for use elsewhere (e.g. GOOGLE_APPLICATION_CREDENTIALS)
    return file_path
