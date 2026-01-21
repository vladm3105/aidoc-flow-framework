import sys
import json

def call_api(prompt, options, context):
    # This is where you would call your actual Agent (e.g. via HTTP or import)
    # For now, we mock it.
    
    ticker = context['vars'].get('ticker', 'UNKNOWN')
    
    # Mock Response
    return {
        "output": f"The current price of {ticker} is $150. The trend is bullish. This is professional advice."
    }
