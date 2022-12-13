import os
import sys


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Error. Too few parameters.")
        sys.exit(1)

    if len(sys.argv) > 3:
        print("Error. Too many parameters.")
        sys.exit(1)
    param_name = sys.argv[1]
    param_value = sys.argv[2]

    if param_name != "--path":
        print(f"Error. Unknown parameter '{param_name}'.")
        sys.exit(1)

    if not os.path.exists(param_value):
        print(f"Error. The system cannot find the path '{param_value}'.")
        sys.exit(1)

    print("Processing...")

    for filename in os.listdir(param_value):
        if filename.endswith("_parsed"):
            name = os.path.join(param_value,filename)
            for file in os.listdir(name):
                if(file.startswith("markdown")):
                    os.remove(os.path.join(name,file))


    print("Success.")