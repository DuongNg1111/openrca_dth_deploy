from src.schemas import RawQuery, ValidationResult


def validate_query(query: RawQuery) -> ValidationResult:

    errors = []

    description = query.incident_description or ""

    text = description.strip().lower()

    # -------------------------
    # Empty description
    # -------------------------

    if not text:

        errors.append("Incident description is required.")

    # -------------------------
    # Too short
    # -------------------------

    elif len(text) < 10:

        errors.append("Incident description is too short.")

    # -------------------------
    # Meaningless description
    # -------------------------

    elif text in {"test", "abc", "hello", "123"}:

        errors.append("Incident description is not meaningful.")

    return ValidationResult(

            is_valid=(len(errors) == 0),

            errors=errors,
        )
