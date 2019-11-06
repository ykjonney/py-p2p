import logging

Logger = logging.getLogger()
handler = logging.FileHandler('log.txt')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(message)s')
handler.setFormatter(formatter)
Logger.addHandler(handler)

KAD_ALPHA = 3
BUCKET_SIZE = 16
KAD_ID_SIZE = 256
BUCKET_NUMBER = 17
BUCKET_MIN_DISTANCE=KAD_ID_SIZE-BUCKET_NUMBER
RE_VALIDATE_INTERVAL = 10
REFRESH_INTERVAL = 3
K_BOND_EXPIRATION = 86400
K_EXPIRATION = 20
K_MAX_NEIGHBORS = 12
K_PUBKEY_SIZE=512
K_MAX_KEY_VALUE=2**K_PUBKEY_SIZE-1
