from typing import Any, Dict


def compose_i18n(form_data: Dict[str, Any], field_prefix: str) -> Dict[str, str]:
    """Compose a dictionary of i18n values from the form data.
    Args:
      form_data (Dict[str, Any]): The form data.
      field_prefix (str): The field prefix.
    Returns:
      Dict[str, str]: The composed i18n values.
    """
    return dict(
        en=(
            form_data.get(f"{field_prefix}[en]").strip()
            if form_data.get(f"{field_prefix}[en]")
            else ""
        ),
        ar=(
            form_data.get(f"{field_prefix}[ar]").strip()
            if form_data.get(f"{field_prefix}[ar]")
            else ""
        )
    ) 
