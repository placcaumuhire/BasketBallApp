import os

from twelvelabs import TwelveLabs

client = TwelveLabs(api_key=os.getenv('TL_API_KEY'))

from twelvelabs import APIStatusError

index_obj = None
try:
    index_obj = client.index.create(
        name = "Curiosity",
        engines =[
            {
                "name": "marengo2.6",
                "options": ["visual", "conversation", "text_in_video"],
            },
            {
                "name": "pegasus1",
                "options": ["visual", "conversation"],
            },
        ],
    )
    print(index_obj)
except APIStatusError as e:
    print('API Status Error, 4xx or 5xx')
    print(e)
except Exception as e:
    print(e)

try:
    engines = client.engines.list()
    print(engines)
except twelvelabs.APIConnectionError as e:
    print("Cannot connect to API server")
except twelvelabs.BadRequestError as e:
    print("Bad request.")
except twelvelabs.APIStatusError as e:
    print(f"Status code {e.status_code} received")
    print(e.response)
