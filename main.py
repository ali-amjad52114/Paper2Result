import os

from dotenv import load_dotenv
from daytona import Daytona, DaytonaConfig

load_dotenv()

api_key = os.getenv("DAYTONA_API_KEY")
if not api_key:
    raise ValueError("DAYTONA_API_KEY is not set in .env")

config = DaytonaConfig(api_key=api_key)
daytona = Daytona(config)

sandbox = daytona.create()

response = sandbox.process.code_run('print("Hello World from code!")')
if response.exit_code != 0:
    print(f"Error: {response.exit_code} {response.result}")
else:
    print(response.result)
