def sort_balance():
    with open("../results/balances/balances.txt", "r") as balances:
        lines = balances.readlines()

        for line in lines:
            addr, balance = line.split(":")
            print(addr, balance)

            if 320 <= float(balance.strip()) <= 400:
                file_path = "../results/balances/sorted/320_400.txt"
            elif 401 <= float(balance.strip()) <= 1000:
                file_path = "../results/balances/sorted/401_1000.txt"
            elif float(balance.strip()) >= 1001:
                file_path = "../results/balances/sorted/1001_plus.txt"
            else:
                file_path = "../results/balances/sorted/etc.txt"

            with open(file_path, "a") as b_output:
                b_output.write(f"{addr}\n")

if __name__ == "__main__":
    sort_balance()