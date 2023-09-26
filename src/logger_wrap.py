from pathlib import Path
import logging
import logging.handlers


def logger(name=''):
  log_path = Path(__file__).parent
  log_path /= './log/index.log'
  # ログファイルがないときにディレクトリを生成
  if not log_path.parent.exists():
    log_path.parent.mkdir()
  logger = logging.getLogger(name)
  logger.setLevel(logging.DEBUG)
  rotation_handler = logging.handlers.RotatingFileHandler(
      log_path,
      encoding='utf-8',
      maxBytes=256*1000,
      backupCount=10,
    )
  rotation_handler.setLevel(logging.DEBUG)
  formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(name)s - %(funcName)s \n%(message)s\n')
  rotation_handler.setFormatter(formatter)
  logger.addHandler(rotation_handler)
  return logger
