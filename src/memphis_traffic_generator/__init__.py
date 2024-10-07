from argparse import ArgumentParser
from os import getenv
from .generator import Generator
from .builder import Builder
from .simulator import Simulator
from .extractor import Extractor

ENV_MEMPHIS_V_PATH = "MEMPHIS_V_PATH"

def memphis_tg():
    parser = ArgumentParser(description="Memphis Traffic Generator")
    subparsers = parser.add_subparsers(dest="option")

    gen_app_parser = subparsers.add_parser("generate-app", help="Generate testcase and scenarios for app-based anomaly")
    gen_app_parser.add_argument("APPLICATION", help="Application name to generate")
    gen_app_parser.add_argument("-o", "--output", help="Path to output base folder", default=".")
    gen_app_parser.add_argument("-m", "--msize", help="Size of the malicious message", default="96")

    gen_ht_parser = subparsers.add_parser("generate-ht", help="Generate testcases and scenarios for HT-based anomaly")
    gen_ht_parser.add_argument("APPLICATION", help="Application name to generate")
    gen_ht_parser.add_argument("-o", "--output", help="Path to output base folder", default=".")
    gen_ht_parser.add_argument("-m", "--with-management", help="Add ODA detection tasks", action="store_true", default=False)
    
    build_parser = subparsers.add_parser("build", help="Generate testcase and scenarios")
    build_parser.add_argument("TESTCASE", help="Testcase file")
    build_parser.add_argument("APPLICATIONS", help="Applications file")
    build_parser.add_argument("SCENARIOS", help="Scenarios folder")

    sim_parser = subparsers.add_parser("simulate", help="Generate testcase and scenarios")
    sim_parser.add_argument("TESTCASE", help="Testcase path")
    sim_parser.add_argument("-l", "--lower", help="Lower bound", default=None)
    sim_parser.add_argument("-u", "--upper", help="Upper bound", default=None)

    ext_app_parser = subparsers.add_parser("extract-app", help="Extract dataset from app-based anomaly simulations")
    ext_app_parser.add_argument("TESTCASE", help="Testcase path")
    ext_app_parser.add_argument("-o", "--output", help="Output file", default=None)
    ext_app_parser.add_argument("-l", "--lower",  help="Lower bound", default=None)
    ext_app_parser.add_argument("-u", "--upper",  help="Upper bound", default=None)

    ext_ht_parser = subparsers.add_parser("extract-ht", help="Extract dataset from HT-based anomaly simulations")
    ext_ht_parser.add_argument("TESTCASE", help="Normal testcase path")
    ext_ht_parser.add_argument("TESTCASE_M", help="Anomalous testcase path")
    ext_ht_parser.add_argument("-o", "--output", help="Output file", default=None)
    ext_ht_parser.add_argument("-l", "--lower",  help="Lower bound", default=None)
    ext_ht_parser.add_argument("-u", "--upper",  help="Upper bound", default=None)

    ext_single_parser = subparsers.add_parser("extract-single", help="Extract dataset from single scenario with no HT")
    ext_single_parser.add_argument("SCENARIO", help="Normal scenario path")
    ext_single_parser.add_argument("-o", "--output", help="Output file", default=None)
    ext_single_parser.add_argument("-l", "--lower",  help="Lower bound", default=None)
    ext_single_parser.add_argument("-u", "--upper",  help="Upper bound", default=None)

    args = parser.parse_args()
    if args.option == "generate-app" or args.option == "generate-ht":
        MEMPHIS_V_PATH = getenv(ENV_MEMPHIS_V_PATH)
        if MEMPHIS_V_PATH is None:
            raise ValueError("Environment variable {} not set".format(ENV_MEMPHIS_V_PATH))

        if args.option == "generate-app":
            generator = Generator(MEMPHIS_V_PATH, args.APPLICATION, mal_msg_size=args.msize)
        else:
            generator = Generator(MEMPHIS_V_PATH, args.APPLICATION, trojan=True, oda=args.with_management)

        generator.write(args.output)
    elif args.option == "build":
        builder = Builder(args.TESTCASE, args.APPLICATIONS, args.SCENARIOS)
        builder.build()
    elif args.option == "simulate":
        simulator = Simulator(args.TESTCASE, args.lower, args.upper)
        simulator.simulate()
    elif args.option == "extract-app":
        extractor = Extractor(args.TESTCASE, args.lower, args.upper)
        extractor.extract(args.output)
    elif args.option == "extract-ht":
        extractor = Extractor(args.TESTCASE, args.lower, args.upper, args.TESTCASE_M)
        extractor.extract(args.output)
    elif args.option == "extract-single":
        extractor = Extractor(None, args.lower, args.upper, None, args.SCENARIO)
        extractor.extract(args.output)
    else:
        parser.print_usage()
