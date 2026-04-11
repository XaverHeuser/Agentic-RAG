import logging
import sys

from src.agent import Agent
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


def main():
    """Main entry point to initialize the system and start the interaction loop."""
    config = Config()
    setup_logging(config)

    logger = logging.getLogger('Main')
    logger.info('System Startup - Agent v1.0')

    try:
        # Initialize Components
        store = AgentStore(config)
        agent = Agent(config, search_func=store.search)

        print('Agent ready. Type "exit" to quit')

        while True:
            user_input = input('\nYour Question: ').strip()
            if user_input.lower() in ['exit', 'quit']:
                logger.info('Session terminated by user')
                break

            if not user_input:
                continue

            # Get answer from agent
            answer = agent.ask(user_input)
            print(f'\nAgent: {answer}')

    except KeyboardInterrupt:
        logger.warning('System interrupted by user')
    except Exception as e:
        logger.critical(f'Unexpected system error: {str(e)}', exc_info=True)


if __name__ == '__main__':
    main()
