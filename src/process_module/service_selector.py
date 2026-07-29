from typing import Dict, List

# =====================================================
# STEP 9.1
# Affected System Mapping
# =====================================================

AFFECTED_SYSTEM_MAP = {

    "Website / Application": [
        "frontend",
    ],

    "Products": [
        "productcatalogservice",
    ],

    "Search Products": [
        "productcatalogservice",
        "recommendationservice",
    ],

    "Shopping Cart": [
        "cartservice",
    ],

    "Order": [
        "checkoutservice",
    ],

    "Shipping & Delivery": [
        "shippingservice",
        "checkoutservice",
    ],

    "Payment": [
        "paymentservice",
    ],

    "Billing & Invoice": [
        "paymentservice",
        "checkoutservice",
    ],

    "Prices": [
        "currencyservice",
    ],

    "Email Notifications": [
        "emailservice",
    ],

    "Promotions": [
        "adservice",
    ],

    "Other": [],
}


# =====================================================
# STEP 9.2
# Keyword Mapping
# =====================================================

SERVICE_KEYWORD_MAP = {

    # -----------------------------------------
    # Website / Application
    # -----------------------------------------

    "website": ["frontend"],
    "web": ["frontend"],
    "application": ["frontend"],
    "app": ["frontend"],
    "page": ["frontend"],
    "screen": ["frontend"],
    "browser": ["frontend"],
    "ui": ["frontend"],

    # -----------------------------------------
    # Products
    # -----------------------------------------

    "product": ["productcatalogservice"],
    "products": ["productcatalogservice"],
    "catalog": ["productcatalogservice"],
    "inventory": ["productcatalogservice"],
    "stock": ["productcatalogservice"],

    # -----------------------------------------
    # Search Products
    # -----------------------------------------

    "search": [
        "productcatalogservice",
        "recommendationservice",
    ],

    "find": [
        "productcatalogservice",
        "recommendationservice",
    ],

    "recommend": [
        "recommendationservice",
    ],

    "recommendation": [
        "recommendationservice",
    ],

    # -----------------------------------------
    # Shopping Cart
    # -----------------------------------------

    "cart": ["cartservice"],
    "basket": ["cartservice"],
    "shopping": ["cartservice"],

    # -----------------------------------------
    # Order
    # -----------------------------------------

    "order": ["checkoutservice"],
    "checkout": ["checkoutservice"],
    "purchase": ["checkoutservice"],
    "buy": ["checkoutservice"],
    "place": ["checkoutservice"],

    # -----------------------------------------
    # Shipping
    # -----------------------------------------

    "shipping": ["shippingservice"],
    "ship": ["shippingservice"],
    "delivery": ["shippingservice"],
    "tracking": ["shippingservice"],
    "address": ["shippingservice"],

    # -----------------------------------------
    # Payment / Billing
    # -----------------------------------------

    "payment": ["paymentservice"],
    "pay": ["paymentservice"],
    "billing": ["paymentservice"],
    "invoice": ["paymentservice"],
    "transaction": ["paymentservice"],
    "refund": ["paymentservice"],
    "credit": ["paymentservice"],
    "card": ["paymentservice"],

    # -----------------------------------------
    # Prices
    # -----------------------------------------

    "price": ["currencyservice"],
    "prices": ["currencyservice"],
    "pricing": ["currencyservice"],
    "currency": ["currencyservice"],
    "exchange": ["currencyservice"],
    "discount": ["currencyservice"],

    # -----------------------------------------
    # Email
    # -----------------------------------------

    "email": ["emailservice"],
    "mail": ["emailservice"],
    "notification": ["emailservice"],
    "confirmation": ["emailservice"],

    # -----------------------------------------
    # Promotions
    # -----------------------------------------

    "promotion": ["adservice"],
    "promotions": ["adservice"],
    "advertisement": ["adservice"],
    "advertising": ["adservice"],
    "ads": ["adservice"],
    "banner": ["adservice"],

    # -----------------------------------------
    # Redis
    # -----------------------------------------

    "redis": ["redis-cart"],
    "cache": ["redis-cart"],
}


# =====================================================
# STEP 9.3
# Select Related Services
# =====================================================

def select_services(
    parsed_query,
    contexts,
):
    """
    Select services based on:
        1. Affected System
        2. Keywords

    Returns
    -------
    Dict[str, InvestigationContext]
    """

    selected = set()

    # -----------------------------------------
    # Affected System
    # -----------------------------------------

    affected_system = parsed_query.affected_system

    if affected_system in AFFECTED_SYSTEM_MAP:

        selected.update(
            AFFECTED_SYSTEM_MAP[affected_system]
        )

    # -----------------------------------------
    # Keywords
    # -----------------------------------------

    for keyword in parsed_query.keywords:

        keyword = keyword.lower()

        if keyword in SERVICE_KEYWORD_MAP:

            selected.update(
                SERVICE_KEYWORD_MAP[keyword]
            )

    # -----------------------------------------
    # Build Selected Context
    # -----------------------------------------

    selected_contexts = {}

    for service in selected:

        if service in contexts:

            selected_contexts[service] = contexts[service]

    return selected_contexts