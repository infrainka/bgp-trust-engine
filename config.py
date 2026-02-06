import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

GRPC_PORT = int(os.getenv("GRPC_PORT", 50051))
# There is no key needed for mock mode - this is for later RPKI API integration
RPKI_API_KEY = os.getenv("RPKI_API_KEY")

IS_MOCK_MODE = (RPKI_API_KEY is None)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Correctly point to the sim-clone-testing directory
DEFAULT_TOPOLOGY_PATH = os.path.normpath(
    os.path.join(BASE_DIR, "..", "sim-clone-testing", "topology.conf")
)

TOPOLOGY_FILE = os.getenv("TOPOLOGY_FILE", DEFAULT_TOPOLOGY_PATH)

if IS_MOCK_MODE:
    print(f"[Config] Mock Mode Active. Using topology: {TOPOLOGY_FILE}")
