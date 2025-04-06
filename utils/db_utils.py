"""DB utility functions for querying and paginating SQLAlchemy models."""

from typing import Any, Dict

from sqlalchemy import text

from app.extensions import db


def paginate_query(
    model, page: int = 1, page_size: int = 10, **filters
) -> Dict[str, Any]:
    """
    Execute a paginated query with filters.

    Args:
        model: The SQLAlchemy model to query
        page: Page number (1-indexed)
        page_size: Number of items per page
        **filters: Filter conditions to apply to the query
            Special filters:
            - sort: Field to sort by (can be a SQLAlchemy order_by expression)

    Returns:
        Dictionary containing:
        - data: List of items (as dictionaries if to_dict method exists)
        - page: Current page number
        - next_page: Next page number if more results exist, otherwise None
        - total_pages: Total number of pages
        - total_items: Total number of items matching the query
    """
    sort = filters.pop("sort", None)

    # Default to exclude deleted items
    filters.setdefault("deleted_at", None)

    query = model.query.filter_by(**filters)

    # Apply sorting if specified
    if sort:
        if isinstance(sort, str):
            query = query.order_by(text(sort))
        else:
            query = query.order_by(sort)

    pagination = query.paginate(page=page, per_page=page_size)

    items = [
        item.to_dict() if hasattr(item, "to_dict") else item
        for item in pagination.items
    ]

    total_items = pagination.total
    total_pages = (
        (total_items + page_size - 1) // page_size if total_items > 0 else 0
    )
    next_page = page + 1 if page < total_pages else None

    return dict(
        data=items,
        page=page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total_items,
    )


def search_by_multilang_field(
    model, field_name: str, search_term: str
) -> Dict[str, Any]:
    """
    Search for items where a multilingual field contains the search term.

    Args:
        model: The SQLAlchemy model to query
        field_name: Name of the JSONB field to search in
        search_term: The search term to look for

    Returns:
        Dictionary containing search results and pagination metadata
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

    # Prepare pagination metadata
    pagination_info = {
        "total_pages": 1,
        "page": 1,
        "next_page": None,
        "total_items": len(res),
    }

    result = {"data": res}
    result.update(pagination_info)

    return result
