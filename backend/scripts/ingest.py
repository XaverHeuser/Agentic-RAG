import logging
import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.database import AgentStore


def setup_logging(config: Config):
    """Configures global logging."""
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),  # Logs to agent.log
            logging.StreamHandler(sys.stdout),  # Logs to terminal
        ],
    )


def run_ingestion():
    """Entry point for ingesting new data via CLI."""
    config = Config()
    setup_logging(config)

    logger = logging.getLogger('IngestTool')
    logger.info('--- Manual Ingestion Started ---')

    try:
        store = AgentStore(config)

        # Take path from command line or use default ./data
        target_path = sys.argv[1] if len(sys.argv) > 1 else './data'

        logger.info(f'Starting ingestion for: {target_path}')
        store.ingest_path(target_path)
        logger.info('Ingestion complete. Check agent.log for details.')

    except Exception as e:
        logger.critical(f'Error while ingesting new data: {str(e)}')


if __name__ == '__main__':
    run_ingestion()
