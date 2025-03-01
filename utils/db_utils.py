"""DB utility functions for querying and paginating SQLAlchemy models."""

from typing import Any, Dict, List, Tuple

from app.extensions import db


def paginate_query(
    model, page: int = 1, page_size: int = 10, **filters
) -> Tuple[List, Dict[str, Any]]:
    """
    Execute a paginated query with filters.

    Args:
        model: The SQLAlchemy model to query
        page: Page number (1-indexed)
        page_size: Number of items per page
        **filters: Filter conditions to apply to the query

    Returns:
        Tuple containing (list of items, pagination metadata)
    """
    # Apply filters, default to exclude deleted items
    if "deleted_at" not in filters:
        filters["deleted_at"] = None

    # Execute query with pagination
    pagination = model.query.filter_by(**filters).paginate(
        page=page, per_page=page_size
    )

    # Convert to dictionaries if they have to_dict method
    items = []
    for item in pagination.items:
        if hasattr(item, "to_dict"):
            items.append(item.to_dict())
        else:
            items.append(item)

    # Prepare pagination metadata
    next_page = page + 1 if len(items) == page_size else None
    total_pages = (pagination.total + page_size - 1) // page_size  # Ceiling division

    pagination_info = {
        "total_pages": total_pages,
        "page": page,
        "next_page": next_page,
        "total_items": pagination.total,
    }

    return items, pagination_info


def search_by_multilang_field(model, field_name: str, search_term: str) -> List:
    """
    Search for items where a multilingual field contains the search term.

    Args:
        model: The SQLAlchemy model to query
        field_name: Name of the JSONB field to search in
        search_term: The search term to look for

    Returns:
        List of matching model instances
    """
    field = getattr(model, field_name)

    result = model.query.filter(
        model.deleted_at.is_(None),
        (
            db.cast(field["en"], db.String).ilike(f"%{search_term}%")
            | db.cast(field["ar"], db.String).ilike(f"%{search_term}%")
        ),
    ).all()

    res = [item.to_dict() for item in result if item]
    return res
