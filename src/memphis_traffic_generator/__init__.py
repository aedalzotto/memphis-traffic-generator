from argparse import ArgumentParser
from os import getenv
from .generator import Generator

ENV_MEMPHIS_V_PATH = "MEMPHIS_V_PATH"

def memphis_tg():
    parser = ArgumentParser(description="Memphis Traffic Generator")
    subparsers = parser.add_subparsers(dest="option")

    gen_parser = subparsers.add_parser("generate", help="Generate testcase and scenarios")
    gen_parser.add_argument("APPLICATION", help="Application name to generate")
    gen_parser.add_argument("OUTPUT_PATH", help="Path to base folder output")
    gen_parser.add_argument("MAL_MSG_SIZE", help="Size of the malicious message")
    
    # build
    # simulate
    # extract

    args = parser.parse_args()
    if args.option == "generate":
        MEMPHIS_V_PATH = getenv(ENV_MEMPHIS_V_PATH)
        if MEMPHIS_V_PATH is None:
            raise ValueError("Environment variable {} not set".format(ENV_MEMPHIS_V_PATH))
        generator = Generator(MEMPHIS_V_PATH, args.APPLICATION, args.MAL_MSG_SIZE)
        generator.write(args.OUTPUT_PATH)
