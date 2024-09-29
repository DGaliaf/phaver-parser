import re


class Profile:
    class Wallet:
        def __init__(self, handle: str, wallet: str):
            self.handle: str = handle
            self.wallet: str = wallet

        def __str__(self):
            return f"Lens Profile:\n    -Handle: {self.handle}\n    -Wallet: {self.wallet}"

    class Socials:
        def __init__(self, youtube: str, twitter: str, linkedin: str, website: str, telegram: str, discord: str):
            self.youtube: str = youtube
            self.twitter: str = twitter
            self.linkedin: str = linkedin
            self.website: str = website
            self.telegram: str = telegram
            self.discord: str = discord

        def getSocials(self) -> dict:
            return {
                "youtube": self.youtube,
                "twitter": self.twitter,
                "linkedin": self.linkedin,
                "website": self.website,
                "telegram": self.telegram,
                "discord": self.discord
            }

        def __str__(self):
            return (
                f"Socials:\n    -Youtube: {self.youtube}\n    -Twitter: {self.twitter}\n    -LinkedIn: {self.linkedin}\n  "
                f"  -Website: {self.website}\n    -Telegram: {self.telegram}\n    -Discord: {self.discord}\n")

    def generateBio(self):
        socials_content = "[ "

        socials = self.socials.getSocials()
        for social in socials:
            socials_content += f"{social}:{socials[social]}, "

        socials_content += " ]"

        return f"{self.name} | {self.username} | {self.descr} | {self.wallet.handle} | {self.wallet.wallet} | {socials_content}"

    def isEligible(self) -> bool:
        def __hasNeededBio() -> bool:
            if re.search(
                    'dev|developer|Developer|Dev|Solidity|Engineer|engineer|solidity|backend|Backend|Frontend|frontend|manager|moderator|mod|content|Content|Manager|Programmer|programmer|intern|Intern|Collab|collab|dm|DM',
                    "" if self.descr is None else self.descr):
                return True

        def __hasLink() -> bool:
            links = self.socials.getSocials()

            is_all_empty = True
            for v in links:
                if links[v] != "" or links[v] != " ":
                    is_all_empty = False

            return not is_all_empty

        if __hasNeededBio() and __hasLink():
            return True

    def __init__(self, name: str | None = None, username: str | None = None, descr: str | None = None,
                 handle: str | None = None,
                 wallet: str | None = None, youtube: str | None = None, twitter: str | None = None,
                 linkedin: str | None = None, website: str | None = None, telegram: str | None = None,
                 discord: str | None = None):
        self.name: str = name
        self.username: str = username
        self.descr: str = descr
        self.wallet: Profile.Wallet = self.Wallet(
            handle=handle,
            wallet=wallet
        )
        self.socials: Profile.Socials = self.Socials(
            youtube=youtube,
            twitter=twitter,
            linkedin=linkedin,
            website=website,
            telegram=telegram,
            discord=discord
        )

    def __str__(self):
        return f"Profile:\n  -Name:{self.name}\n  -Username:{self.username}\n  -BIO:{self.descr}\n  -{self.wallet}\n-{self.socials}\n"