"""Main module to start application."""
import argparse
import json
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import TextIO

from aiohttp import web

from config_model import MainConfig
from web_app import Application

os.environ['no_proxy'] = '*'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

BASE_DIR = Path(__file__).parent.absolute()


def set_logger(file_path: str, log_level: str = 'DEBUG') -> None:
    """
    Set up logger according settings.

    Args:
        log_level (str): Logger level.
        file_path (str): File path to save log.

    Raises:
        Exception: if error in logger setting up.

    """
    try:
        logger_handler = TimedRotatingFileHandler(
            os.path.join(
                file_path,
                'webapp.log',
            ),
            when='W6',
        )
    except Exception:
        logger.exception('Logger has error while setting up handler.')
        raise
    try:
        logger_handler.setLevel(log_level.upper())
    except Exception:
        logger.exception('Logger has error while setting up level.')
    formatter = logging.Formatter(
        '{asctime} :: {name:22s} :: {levelname:8s} :: {message}',
        style='{',
    )
    logger_handler.setFormatter(formatter)
    logger.addHandler(logger_handler)
    logger.info('Logger has been successfully set up.')


def load_config(config_file: TextIO) -> MainConfig:
    """
    Load configuration from json-file and structuring into a class-notation.

    Args:
        config_file (TextIO): file with config

    Raises:
        Exception: if error while getting configuration.

    Returns:
        loaded_config (MainConfig): Config for Zabbix, Redis, Psql, logger.

    """
    try:
        loaded_config = MainConfig(
            **json.loads(
                config_file.read(),
            ),
        )
    except Exception:
        logger.exception('Error getting configuration')
        raise
    return loaded_config


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-C',
        '--config',
        help='Required. Path to file with configurations',
        required=True,
        type=argparse.FileType('r'),
        dest='config_file',
    )
    parsed_args = parser.parse_args()
    config = load_config(config_file=parsed_args.config_file)

    set_logger(
        file_path=config.logger.path,
        log_level=config.logger.level,
    )

    try:
        web.run_app(
            app=Application(config),
            host=config.app.host,
            port=config.app.port,
        )
    except Exception as exception:
        logger.exception('Starting app was failed. {0}'.format(exception))
