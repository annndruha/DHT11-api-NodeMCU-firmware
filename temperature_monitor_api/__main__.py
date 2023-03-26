import uvicorn

from temperature_monitor_api.routes.route_base import app


if __name__ == '__main__':
    uvicorn.run(app)
