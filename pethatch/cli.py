"""命令行入口：跑孵化样例。"""

import argparse

from .hatch import Egg, HatchError, claim


def build_parser():
    parser = argparse.ArgumentParser(prog="pet-hatch", description="宠物孵化")
    parser.add_argument("--sample", default="early", help="early / repeat")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "early":
        egg = Egg("e1", 0, 3600)
        try:
            claim(egg, 100)
            print("claimed=True")
        except HatchError:
            print("claimed=rejected")
    elif args.sample == "repeat":
        egg = Egg("e1", 0, 100)
        pets = 0
        for _ in range(2):
            try:
                if claim(egg, 500):
                    pets += 1
            except HatchError:
                pass
        print("pets=%d" % pets)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
