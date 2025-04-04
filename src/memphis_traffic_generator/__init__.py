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
    gen_ht_parser.add_argument("-p", "--proportion", help="Percentage of baseline mappings", nargs=1, default=0.75)
    gen_ht_parser.add_argument("-r", "--rtd", help="Add real-time detection tasks for HT scenarios", action="store_true", default=False)
    gen_ht_parser.add_argument("-o", "--output", help="Path to output base folder", default=".")
    gen_ht_parser.add_argument("-s", "--size", help="Manually adjust size. E.g. 4 4 for 4x4", nargs=2, default=None)

    build_parser = subparsers.add_parser("build", help="Build scenarios")
    build_parser.add_argument("TESTCASE", help="Testcase file")
    build_parser.add_argument("APPLICATIONS", help="Applications file")
    build_parser.add_argument("SCENARIOS", help="Scenarios folder")
    build_parser.add_argument("-b", "--no-base", help="Do not build baseline/malicious scenario", action="store_true", default=False)
    build_parser.add_argument("-r", "--with-rtd", help="Build RTD scenarios", action="store_true", default=False)

    sim_parser = subparsers.add_parser("simulate", help="Simulate scenarios")
    sim_parser.add_argument("TESTCASE", help="Testcase path")
    sim_parser.add_argument("-b", "--no-base", help="Do not simulate baseline/malicious scenario", action="store_true", default=False)
    sim_parser.add_argument("-r", "--with-rtd", help="Simulate RTD scenarios", action="store_true", default=False)

    ext_ht_parser = subparsers.add_parser("extract", help="Extract datasets")
    ext_ht_parser.add_argument("TESTCASE", help="Testcase path")
    ext_ht_parser.add_argument("-b", "--no-base", help="Do not extract train/test dataset", action="store_true", default=False)
    ext_ht_parser.add_argument("-r", "--with-rtd", help="Extract RT detection dataset", action="store_true", default=False)
    ext_ht_parser.add_argument("-a", "--appid",  help="Application ID to extract", default=None)

    args = parser.parse_args()
    if args.option == "generate":
        MEMPHIS_V_PATH = getenv(ENV_MEMPHIS_V_PATH)
        if MEMPHIS_V_PATH is None:
            raise ValueError("Environment variable {} not set".format(ENV_MEMPHIS_V_PATH))
        generator = Generator(MEMPHIS_V_PATH, args.APPLICATION, args.proportion, args.rtd, mc_size=args.size)
        generator.write(args.output)
    elif args.option == "build":
        builder = Builder(args.TESTCASE, args.APPLICATIONS, args.SCENARIOS, args.no_base, args.with_rtd)
        builder.build()
    elif args.option == "simulate":
        simulator = Simulator(args.TESTCASE, args.no_base, args.with_rtd)
        simulator.simulate()
    elif args.option == "extract":
        extractor = Extractor(args.TESTCASE, args.no_base, args.with_rtd, appid=args.appid)
        extractor.extract()
    else:
        parser.print_usage()
