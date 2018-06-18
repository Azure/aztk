import logging

# Azure storage is logging error in the console which make the CLI quite confusing
logging.getLogger("azure.storage").setLevel(logging.CRITICAL)

# msrestazure logs warning for keyring
logging.getLogger("msrestazure").setLevel(logging.CRITICAL)

# msrest
logging.getLogger("msrest").setLevel(logging.CRITICAL)
