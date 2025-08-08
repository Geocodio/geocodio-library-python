"""
Test configuration and fixtures
"""

import os
import logging
from dotenv import load_dotenv
import pytest
from geocodio import Geocodio

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def client(request):
    """Create a Geocodio instance with test configuration"""
    # Use TEST_KEY for all tests except e2e tests
    if "e2e" in request.node.fspath.strpath:
        logger.debug("Running e2e tests - using API key from environment")
        api_key = os.getenv("GEOCODIO_API_KEY")
        if not api_key:
            logger.warning("GEOCODIO_API_KEY not set - skipping e2e test")
            pytest.skip("GEOCODIO_API_KEY environment variable not set")
        return Geocodio(api_key=api_key)
    else:
        logger.debug("Running unit tests - using TEST_KEY with api.test hostname")
        return Geocodio(api_key="TEST_KEY", hostname="api.test")