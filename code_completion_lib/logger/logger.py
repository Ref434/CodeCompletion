import logging


class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # настройка обработчика и форматировщика для logger
        self.handler = logging.FileHandler(r"code_completion_lib\logger\logger.log", mode='a')
        formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

        # добавление форматировщика к обработчику
        self.handler.setFormatter(formatter)
        # добавление обработчика к логгеру
        self.logger.addHandler(self.handler)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message, exc_info=True):
        self.logger.error(message, exc_info=exc_info)

    def critical(self, message):
        self.logger.critical(message)

