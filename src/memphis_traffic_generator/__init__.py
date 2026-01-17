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

    gen_ht_parser = subparsers.add_parser("generate", help="Generate testcases and scenarios for HT-based anomaly")
    gen_ht_parser.add_argument("APPLICATION", help="Application name to generate")
    gen_ht_parser.add_argument("-p", "--proportion", help="Percentage of baseline mappings", nargs=1, default=0.8)
    gen_ht_parser.add_argument("-o", "--output", help="Path to output base folder", default=".")
    gen_ht_parser.add_argument("-s", "--starting-size", help="Manually adjust size. E.g. 4 4 for 4x4", nargs=2, default=None)
    gen_ht_parser.add_argument("-m", "--mal-app", help="Reserve space for malicious application", action="store_true", default=False)
    gen_ht_parser.add_argument("-f", "--floating-point", help="Include FP RTD", action="store_true", default=False)

    build_parser = subparsers.add_parser("build", help="Build scenarios")
    build_parser.add_argument("TESTCASE", help="Testcase file")
    build_parser.add_argument("APPLICATIONS", help="Applications file")
    build_parser.add_argument("SCENARIOS", help="Scenarios folder")
    build_parser.add_argument("-b", "--with-base", help="Build baseline scenarios", action="store_true", default=False)
    build_parser.add_argument("-t", "--with-test", help="Build test scenarios", action="store_true", default=False)
    build_parser.add_argument("-m", "--with-ht", help="Build RTD scenarios w/ HT", action="store_true", default=False)
    build_parser.add_argument("-a", "--with-mapp", help="Build RTD scenarios w/ Mapp", action="store_true", default=False)
    build_parser.add_argument("-f", "--with-fp", help="Build RTD scenarios FP based", action="store_true", default=False)

    sim_parser = subparsers.add_parser("simulate", help="Simulate scenarios")
    sim_parser.add_argument("TESTCASE", help="Testcase path")
    sim_parser.add_argument("-b", "--with-base", help="Simulate baseline scenarios", action="store_true", default=False)
    sim_parser.add_argument("-t", "--with-test", help="Simulate test scenarios", action="store_true", default=False)
    sim_parser.add_argument("-m", "--with-ht",   help="Simulate RTD scenarios w/ HT", action="store_true", default=False)
    sim_parser.add_argument("-a", "--with-mapp", help="Simulate RTD scenarios w/ Mapp", action="store_true", default=False)
    sim_parser.add_argument("-f", "--with-fp",   help="Simulate RTD scenarios FP based", action="store_true", default=False)

    ext_ht_parser = subparsers.add_parser("extract", help="Extract datasets")
    ext_ht_parser.add_argument("TESTCASE", help="Testcase path")
    ext_ht_parser.add_argument("-b", "--with-base",    help="Extract baseline scenarios", action="store_true", default=False)
    ext_ht_parser.add_argument("-t", "--with-test-ht", help="Extract test scenarios (HT w/o RTD)", action="store_true", default=False)
    ext_ht_parser.add_argument("-r", "--with-test-rtd",help="Extract test scenarios (RTD w/o HT)", action="store_true", default=False)
    ext_ht_parser.add_argument("-m", "--with-ht",      help="Extract RTD scenarios w/ HT", action="store_true", default=False)
    ext_ht_parser.add_argument("-a", "--with-mapp",    help="Extract RTD scenarios w/ Mapp", action="store_true", default=False)
    ext_ht_parser.add_argument("-f", "--with-fp",      help="Extract FP-based INSTEAD OF l.q.", action="store_true", default=False)

    args = parser.parse_args()
    if args.option == "generate":
        MEMPHIS_V_PATH = getenv(ENV_MEMPHIS_V_PATH)
        if MEMPHIS_V_PATH is None:
            raise ValueError("Environment variable {} not set".format(ENV_MEMPHIS_V_PATH))
        generator = Generator(MEMPHIS_V_PATH, args.APPLICATION, args.proportion, with_mapp=args.mal_app, with_fp=args.floating_point, starting_size=args.starting_size)
        generator.write(args.output)
    elif args.option == "build":
        builder = Builder(args.TESTCASE, args.APPLICATIONS, args.SCENARIOS, args.with_base, args.with_test, args.with_ht, args.with_mapp, args.with_fp)
        builder.build()
    elif args.option == "simulate":
        simulator = Simulator(args.TESTCASE, args.with_base, args.with_test, args.with_ht, args.with_mapp, args.with_fp)
        simulator.simulate()
    elif args.option == "extract":
        extractor = Extractor(args.TESTCASE, args.with_base, args.with_test_ht, args.with_test_rtd, args.with_ht, args.with_mapp, args.with_fp)
        extractor.extract()
    else:
        parser.print_usage()
