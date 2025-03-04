import requests
import os

print(requests.get("http://localhost:" + os.environ["GRANIAN_PORT"] + "/live"))
