import logging.config
import uvicorn
import yaml

from application.factory import create_app

with open("log_config.yml") as f:
    config = yaml.safe_load(f)
    logging.config.dictConfig(config)

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
