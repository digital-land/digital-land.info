import logging

logger = logging.getLogger(__name__)

# Local wrapper for AWS synthetics_logger
# Delegates interactions to local logger
synthetics_logger = logging.getLogger(__name__)
