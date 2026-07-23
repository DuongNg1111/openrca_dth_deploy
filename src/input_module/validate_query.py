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

    # Validate Environment
    valid_environments = {
        "Cloud A",
        "Cloud B",
    }

    if query.environment not in valid_environments:
        errors.append("Invalid environment.")

    return ValidationResult(

            is_valid=(len(errors) == 0),

            errors=errors,
        )
