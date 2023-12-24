import function
import argparse

parser = argparse.ArgumentParser(usage="\n\tpython3 main.py {setup, update, start, stop, restart}\n")

parser.add_argument('function')

args = parser.parse_args()


if __name__ == "__main__":
    print("starting python clash")
    input_func = args.function 

    if input_func == 'update':
        print("starting update now...")
        function.setup()
    elif input_func == 'start':
        print("start clash core")
    else:
        print('usage')