import pandas as pd

def toExcel(fromPath: str = "../results/eligible.txt", toPath: str = "../results/data/output.xlsx", delimiter: str = "\n") -> None:
    import pandas as pd

    def to_excel():
        with open(fromPath, "r") as inp:
            data = []

            i = inp.read().split(delimiter)

            for j in i:
                data = j.split("|")

                if len(data) < 6:
                    continue
                # Name | Username | BIO | Handle | Wallet | Socials

                data.append({
                    "Name": data[0],
                    "Username": data[1],
                    "BIO": data[2],
                    "Handle": data[3],
                    "Wallet": data[4],
                    "Socials": data[5]
                })

        df = pd.DataFrame(data)

        df.to_excel(toPath, index=False)

    if __name__ == "__main__":
        to_excel()


if __name__ == "__main__":
    toExcel()