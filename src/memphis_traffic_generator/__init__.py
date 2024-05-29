from argparse import ArgumentParser
from os import getenv
from .generator import Generator
from .builder import Builder
from .simulator import Simulator

ENV_MEMPHIS_V_PATH = "MEMPHIS_V_PATH"

def memphis_tg():
    parser = ArgumentParser(description="Memphis Traffic Generator")
    subparsers = parser.add_subparsers(dest="option")

    gen_parser = subparsers.add_parser("generate", help="Generate testcase and scenarios")
    gen_parser.add_argument("APPLICATION", help="Application name to generate")
    gen_parser.add_argument("OUTPUT_PATH", help="Path to base folder output")
    gen_parser.add_argument("MAL_MSG_SIZE", help="Size of the malicious message")
    
    build_parser = subparsers.add_parser("build", help="Generate testcase and scenarios")
    build_parser.add_argument("TESTCASE", help="Testcase file")
    build_parser.add_argument("APPLICATIONS", help="Applications file")
    build_parser.add_argument("SCENARIOS", help="Scenarios folder")

    sim_parser = subparsers.add_parser("simulate", help="Generate testcase and scenarios")
    sim_parser.add_argument("TESTCASE", help="Testcase path")
    sim_parser.add_argument("-l", "--lower", help="Lower bound", default=None)
    sim_parser.add_argument("-u", "--upper", help="Upper bound", default=None)

    # extract

    args = parser.parse_args()
    if args.option == "generate":
        MEMPHIS_V_PATH = getenv(ENV_MEMPHIS_V_PATH)
        if MEMPHIS_V_PATH is None:
            raise ValueError("Environment variable {} not set".format(ENV_MEMPHIS_V_PATH))
        generator = Generator(MEMPHIS_V_PATH, args.APPLICATION, args.MAL_MSG_SIZE)
        generator.write(args.OUTPUT_PATH)
    elif args.option == "build":
        builder = Builder(args.TESTCASE, args.APPLICATIONS, args.SCENARIOS)
        builder.build()
    elif args.option == "simulate":
        simulator = Simulator(args.TESTCASE, args.lower, args.upper)
        simulator.simulate()
