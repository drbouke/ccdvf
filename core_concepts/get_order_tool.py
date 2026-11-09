"""Acme support assistant: the get_order tool, as Claude receives it."""
GET_ORDER = {
    "name": "get_order",  # what Claude writes to ask for it
    "description": ("Full record of one order: items, payments (every "
                    "capture), shipment, courier tracking events and "
                    "refunds."),  # Claude decides from this text
    "input_schema": {  # a JSON Schema for the input
        "type": "object",
        "properties": {
            "order_id": {"type": "string",
                         "description": "For example ord_20931"},
        },
        "required": ["order_id"],
    },
}
