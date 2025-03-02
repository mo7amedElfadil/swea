"""Utils module for parsing form data."""

from typing import Any, Dict, List, Optional


def parse_nested_field(form_data: Dict[str, Any], field_prefix: str) -> Dict[str, str]:
    """
    Parse nested fields like field[en], field[ar] from form data.

    Args:
        form_data: The form data dictionary
        field_prefix: The prefix of the field to parse

    Returns:
        Dict with language codes as keys and field values as values
    """
    return {
        "en": (
            form_data.get(f"{field_prefix}[en]").strip()
            if form_data.get(f"{field_prefix}[en]")
            else ""
        ),
        "ar": (
            form_data.get(f"{field_prefix}[ar]").strip()
            if form_data.get(f"{field_prefix}[ar]")
            else ""
        ),
    }


def parse_key_value_items(
    items_str: Optional[str], separator: str = ",", kv_separator: str = ":"
) -> Dict[str, Any]:
    """
    Parse comma-separated key-value pairs into a dictionary.

    Args:
        items_str: String of comma-separated key-value pairs
        separator: Character separating different items (default: ',')
        kv_separator: Character separating keys from values (default: ':')

    Returns:
        Dictionary of parsed key-value pairs
    """
    if not items_str:
        return {}

    result = {}
    for item in items_str.split(separator):
        parts = item.strip().split(kv_separator, 1)
        if len(parts) == 2:
            key, value = parts
            result[key.strip()] = value.strip()
        elif len(parts) == 1:
            key = parts[0].strip()
            result[key] = ""

    return result


def parse_tags(tags_str: Optional[str]) -> Dict[str, List[str]]:
    """
    Parse tags string into a dictionary of language-tag pairs.

    Args:
        tags_str: String containing tags in format "lang:tag1;tag2,lang2:tag3;tag4"

    Returns:
        Dictionary with language codes as keys and lists of tags as values
    """
    if not tags_str:
        return {}

    tags = {}
    for item in tags_str.split(","):
        parts = item.strip().split(":", 1)
        if len(parts) == 2:
            language, tag_list = parts
            tags[language.strip()] = [tag.strip() for tag in tag_list.split(";")]
        elif len(parts) == 1:
            language = parts[0].strip()
            tags[language] = []

    return tags
