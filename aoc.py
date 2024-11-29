import argparse
import importlib

parser = argparse.ArgumentParser(
    prog='AoC 2024',
    description='Runs solutions for Advent of Code 2024'
)
parser.add_argument('day', type=int, choices=range(1, 26))
parser.add_argument('part', type=int, choices=[1, 2])
parser.add_argument('-t', '--test', action='store_true',
                    help="Use to run on example/test file.")

args = parser.parse_args()

try:
    module_name = f'solutions.day{args.day}'
    module = importlib.import_module(module_name)
    run_func = getattr(module, 'run')
    if run_func:
        input_file_name = 'inputs/day' + str(args.day) + ('-test' if args.test else '') + '.txt'
        with open(input_file_name, 'r') as input_file:
            run_func(input_file, args.part)
except ModuleNotFoundError:
    print(f'No implementation for day {args.day} found.')
except OSError:
    print(f'Input file for day {args.day} {'(test) ' if args.test else ''}not found.')
