import sys
import pendulum

from dns_system.config.settings import settings


def set_datetime(record):
    record["extra"]["datetime"] = pendulum.now(settings.TZ).format("Y:M:D HH:mm:ss")


fmt = "{extra[datetime]} | {level} | {name}:{function}:{line} -> {message}"


conf = {
    "handlers": [
        {"sink": sys.stdout, "format": fmt},
    ],

}
