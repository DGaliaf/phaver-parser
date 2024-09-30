import re


def get_wallet():
    with open("../results/eligible.txt", "r") as file:
        with open("../results/wallets.txt", "a") as output:
            output.write("\n".join(re.findall(r'0x\S{40}', file.read())))


if __name__ == "__main__":
    get_wallet()
