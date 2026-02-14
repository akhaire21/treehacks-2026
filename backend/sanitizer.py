"""
Privacy sanitizer to remove PII from queries before sending to marketplace.
Implements the two-layer architecture: public (sent) vs private (local).
"""

import re
from typing import Dict, Any, Tuple


class PrivacySanitizer:
    """Filters PII and buckets sensitive data for marketplace queries."""

    # Patterns to detect and remove PII
    PII_PATTERNS = {
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'address': r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b',
    }

    # Income brackets for bucketing
    INCOME_BRACKETS = [
        (0, 30000, "0-30k"),
        (30000, 50000, "30k-50k"),
        (50000, 80000, "50k-80k"),
        (80000, 100000, "80k-100k"),
        (100000, 150000, "100k-150k"),
        (150000, 250000, "150k-250k"),
        (250000, float('inf'), "250k+")
    ]

    def sanitize_query(self, raw_query: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Split query into public (sanitized) and private (stays local) layers.

        Args:
            raw_query: Full query with potentially sensitive data

        Returns:
            Tuple of (public_query, private_data)
        """
        public_query = {}
        private_data = {}

        for key, value in raw_query.items():
            if self._is_sensitive_field(key):
                private_data[key] = value
                # Apply bucketing/anonymization for public query
                public_value = self._anonymize_value(key, value)
                if public_value is not None:
                    public_query[key] = public_value
            else:
                # Safe to include in public query
                public_query[key] = value

        return public_query, private_data

    def _is_sensitive_field(self, field_name: str) -> bool:
        """Check if a field contains sensitive information."""
        sensitive_keywords = [
            'name', 'ssn', 'social_security', 'email', 'phone', 'address',
            'exact_income', 'salary', 'account', 'password', 'dob',
            'birth_date', 'credit_card', 'bank'
        ]
        field_lower = field_name.lower()
        return any(keyword in field_lower for keyword in sensitive_keywords)

    def _anonymize_value(self, field_name: str, value: Any) -> Any:
        """Anonymize sensitive values (bucket income, remove exact identifiers)."""
        field_lower = field_name.lower()

        # Income bucketing
        if 'income' in field_lower or 'salary' in field_lower:
            if isinstance(value, (int, float)):
                return self._bucket_income(value)

        # For names, addresses, etc., don't include in public query at all
        return None

    def _bucket_income(self, income: float) -> str:
        """Convert exact income to bracket."""
        for min_val, max_val, bracket in self.INCOME_BRACKETS:
            if min_val <= income < max_val:
                return bracket
        return "250k+"

    def remove_pii_from_text(self, text: str) -> str:
        """Remove PII patterns from free-form text."""
        sanitized = text
        for pii_type, pattern in self.PII_PATTERNS.items():
            sanitized = re.sub(pattern, f'[REDACTED_{pii_type.upper()}]', sanitized, flags=re.IGNORECASE)
        return sanitized

    def get_sanitization_summary(self, raw_query: Dict[str, Any], public_query: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary showing what was sanitized (for UI display)."""
        return {
            'fields_removed': [k for k in raw_query.keys() if k not in public_query],
            'fields_anonymized': [k for k in public_query.keys() if k in raw_query and raw_query[k] != public_query[k]],
            'pii_protected': True
        }


# Example usage for testing
if __name__ == "__main__":
    sanitizer = PrivacySanitizer()

    # Example query with sensitive data
    raw_query = {
        "task_type": "tax_filing",
        "state": "ohio",
        "year": 2024,
        "name": "John Smith",
        "ssn": "123-45-6789",
        "exact_income": 87432.18,
        "deduction_type": "itemized",
        "email": "john.smith@example.com"
    }

    public, private = sanitizer.sanitize_query(raw_query)
    summary = sanitizer.get_sanitization_summary(raw_query, public)

    print("Public query (sent to marketplace):")
    print(public)
    print("\nPrivate data (stays local):")
    print(private)
    print("\nSanitization summary:")
    print(summary)
