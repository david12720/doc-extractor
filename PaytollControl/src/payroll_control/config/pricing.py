MODEL_PRICING_USD_PER_1M = {
    "gemini-2.5-flash": {"input": 0.30, "output": 2.50},
    "gemini-2.5-pro": {
        "input_le": 1.25, "output_le": 10.00,
        "input_gt": 2.50, "output_gt": 15.00,
    },
    "gemini-3.1-pro-preview": {
        "input_le": 2.00, "output_le": 12.00,
        "input_gt": 4.00, "output_gt": 18.00,
    },
}

PAGE_PRICING_USD_PER_1K = {
    "cloud-vision-ocr": 1.50,
}
