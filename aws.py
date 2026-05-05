from pathlib import Path
from dotenv import dotenv_values

ENV_VARS = dotenv_values(Path(__file__).resolve().parent / '.env')

AWS_ACCESS_KEY = ENV_VARS.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = ENV_VARS.get('AWS_SECRET_KEY')
