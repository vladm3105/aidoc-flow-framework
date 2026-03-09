"""Validator registry."""

from typing import Type
from ucx.models.enums import DocType
from ucx.validators.base import BaseValidator

# Registry of validators
_VALIDATORS: dict[DocType, Type[BaseValidator]] = {}


def register_validator(doc_type: DocType):
    """
    Decorator to register a validator for a document type.

    Example:
        @register_validator(DocType.BRD)
        class BRDValidator(BaseValidator):
            ...
    """
    def decorator(cls: Type[BaseValidator]) -> Type[BaseValidator]:
        _VALIDATORS[doc_type] = cls
        return cls
    return decorator


def get_validator(doc_type: DocType) -> BaseValidator:
    """
    Get validator instance for document type.

    Falls back to GenericValidator if no specific validator exists.

    Args:
        doc_type: Document type

    Returns:
        Validator instance
    """
    # Import validators to trigger registration
    from ucx.validators import (  # noqa: F401
        brd,
        prd,
        ears,
        bdd,
        adr,
        sys,
        req,
        ctr,
        spec,
        tspec,
        generic,
    )

    if doc_type in _VALIDATORS:
        return _VALIDATORS[doc_type]()

    # Fall back to generic
    from ucx.validators.generic import GenericValidator
    return GenericValidator(doc_type)
