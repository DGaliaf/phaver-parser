import asyncio
import time

import requests

from models import Profile, HeaderData

from utils import fileUtils

import logging.config

ERROR_FORMAT = "%(levelname)s at %(asctime)s in %(funcName)s in %(filename) at line %(lineno)d: %(message)s"
DEBUG_FORMAT = "%(lineno)d in %(filename)s at %(asctime)s: %(message)s"
LOG_CONFIG = {'version': 1,
              'formatters': {'error': {'format': ERROR_FORMAT},
                             'debug': {'format': DEBUG_FORMAT}},
              'handlers': {'console': {'class': 'logging.StreamHandler',
                                       'formatter': 'debug',
                                       'level': logging.DEBUG},
                           'file': {'class': 'logging.FileHandler',
                                    'filename': 'logs.log',
                                    'formatter': 'error',
                                    'level': logging.ERROR}},
              'root': {'handlers': ('console', 'file'), 'level': 'DEBUG'}
              }

logging.config.dictConfig(LOG_CONFIG)


class PhaverParser:
    def __init__(self):
        self.graphUrls = "https://gql.next.phaver.com/v1/graphql"

        content = """baggage: sentry-environment=production,sentry-release=dbbc47a5-014e-44e1-a594-5fa296ee2a1a,sentry-public_key=12c9b70d3efa4706a3151d7f03413d72,sentry-trace_id=344f46ebb1a7461e991defeb8f9a6a10
Authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjZjYzNmY2I2NDAzMjc2MGVlYjljMjZmNzdkNDA3YTY5NGM1MmIwZTMiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoi0JTQsNC90LjQuyDQpdC-0LTQvtGBIiwiaHR0cHM6Ly9oYXN1cmEuaW8vand0L2NsYWltcyI6eyJ4LWhhc3VyYS1hbGxvd2VkLXJvbGVzIjpbInVzZXIiXSwieC1oYXN1cmEtZGVmYXVsdC1yb2xlIjoidXNlciIsIngtaGFzdXJhLXVzZXItaWQiOiJEUzJtUDhrUElhZkhudUZxRkpOd3VKbkZDd2syIn0sInR5cGUiOiJ1c2VyIiwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tL3BoYXZlci1wcm9kIiwiYXVkIjoicGhhdmVyLXByb2QiLCJhdXRoX3RpbWUiOjE3MjU3MTEwMzIsInVzZXJfaWQiOiJEUzJtUDhrUElhZkhudUZxRkpOd3VKbkZDd2syIiwic3ViIjoiRFMybVA4a1BJYWZIbnVGcUZKTnd1Sm5GQ3drMiIsImlhdCI6MTcyNzYxMDYzMiwiZXhwIjoxNzI3NjE0MjMyLCJlbWFpbCI6ImRhbmlsZ2FsaWFmZXIyMDAwQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7ImFwcGxlLmNvbSI6WyIwMDAzMjcuMTAzNzU3NWQ3ODU0NDE5YmE2ZmQ5MDE3MTI2ZmFiOTguMTIxMCJdLCJlbWFpbCI6WyJkYW5pbGdhbGlhZmVyMjAwMEBnbWFpbC5jb20iXX0sInNpZ25faW5fcHJvdmlkZXIiOiJhcHBsZS5jb20ifX0.JMRkLY91j6HLLSY_aChR2vcOvO62OC4GwYoWXOTDXRX2TPU5sRv23bxVABWjQmQ7FvxoHZ3E-a_cMdVoXf_JVZH6P6RG4UH_k-th8GQftPnRQZBZOncL0x49VIVKiNn1GkvkEnVjGFmOpV-LMKpC1HgGQfHqX2_TXGBIdBBOxHk0-srT-xgk25krlb2fBtxURNjdaoaQ1nyiF1tjAW1lKwEfvhopTxbU3G0-kXcuuU1nNsRFwgrstPe6Eyhb-UkynqnFeatzTGLESlqW1FZ_gt3y-CDEZLjUsku2EUgbczaG_oREu-MyiLW6jM5wBdwjwrbw4Wk9JZ0UhWCKZkWc6g
Accept-Language: ru
Accept-Encoding: gzip, deflate, br
sentry-trace: 344f46ebb1a7461e991defeb8f9a6a10-b2f85fd3a65a1926
x-request-id: e38d071d-6d72-4563-86e4-8faf20603243"""

        self.header = self.__genHeader(self.__parseHeaderStr(content))

    @staticmethod
    def __parseHeaderStr(content: str) -> HeaderData:
        lines = content.strip().splitlines()

        data = []
        for line in lines:
            k, v = line.strip().split(": ")

            if k in ["Accept-Language", "Accept-Encoding"]:
                continue

            data.append(v)

        return HeaderData(
            bearerToken=data[1],
            baggage=data[0],
            sentry=data[2],
            requestID=data[3]
        )

    @staticmethod
    def __genHeader(headerData: HeaderData) -> dict:
        return {
            'Host': 'gql.next.phaver.com',
            'Accept': '*/*',
            'baggage': headerData.sentry,
            'Authorization': headerData.bearerToken,
            'Accept-Language': 'ru',
            'sentry-trace': headerData.sentry,
            'x-request-id': headerData.requestID,
            'User-Agent': 'Phaver/1665995179 CFNetwork/1568.100.1 Darwin/24.0.0',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json'
        }

    def __makeRequest(self, payload: str) -> dict:
        response = requests.post(self.graphUrls, headers=self.header, data=payload)

        sleep_dur = 4
        while response.status_code == 429:
            logging.warning(f"429 Too Many Requests | Sleeping for a {sleep_dur}")

            time.sleep(sleep_dur)
            response = requests.post(self.graphUrls, headers=self.header, data=payload)

            sleep_dur += 0.5

        return response.json()

    def getFollowers(self, profileID: str, limit: int = 20, offset: int = 0) -> list[str]:
        logging.debug(f"Getting {profileID}`s followers")

        payload = (f'{{"query":"query FollowersQuery($followedProfileId: String!, $limit: Int!, $offset: Int!) {{\\n  '
                   f'followers(\\n    limit: $limit\\n    offset: $offset\\n    where: {{followedProfileId: {{_eq: $followedProfileId}}, '
                   f'profile: {{bAt: {{_is_null: true}}}}}}\\n    order_by: {{createdAt: desc}}\\n  ) {{\\n    '
                   f'...FollowerFieldsFragment\\n    __typename\\n  }}\\n}}\\n\\nfragment ImageFieldsFragment on images {{\\n  '
                   f'id\\n  profileId\\n  size\\n  bucket\\n  createdAt\\n  updatedAt\\n  filename\\n  width\\n  height\\n  blurhash\\n  '
                   f'contentType\\n  pages\\n  sourceUrl\\n  status\\n  __typename\\n}}\\n\\nfragment LensProfileFieldsFragment on '
                   f'lens_profiles {{\\n  id\\n  lensProfileId\\n  lensHandle\\n  status\\n  txId\\n  ownerAddress\\n  followModule\\n  '
                   f'isUserFollowing\\n  isFollowPending\\n  image {{\\n    ...ImageFieldsFragment\\n    __typename\\n  }}\\n  __typename\\n}}\\n\\n'
                   f'fragment NftFieldsFragment on connected_nfts {{\\n  id\\n  profileId\\n  chainId\\n  nftName\\n  nft_description\\n  '
                   f'nftTokenId\\n  contractAddress\\n  createdAt\\n  updatedAt\\n  image {{\\n    ...ImageFieldsFragment\\n    __typename\\n  }}\\n  '
                   f'verifiedNftProject {{\\n    id\\n    image {{\\n      ...ImageFieldsFragment\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  '
                   f'__typename\\n}}\\n\\nfragment FarcasterProfileFragment on farcaster_profiles {{\\n  tokenId\\n  displayName\\n  name\\n  '
                   f'isUserFollowing\\n  imageRel {{\\n    ...ImageFieldsFragment\\n    __typename\\n  }}\\n  __typename\\n}}\\n\\n'
                   f'fragment ProfileFieldsFragment on profiles {{\\n  id\\n  name\\n  username\\n  description\\n  credLevel\\n  image {{\\n    '
                   f'...ImageFieldsFragment\\n    __typename\\n  }}\\n  createdAt\\n  updatedAt\\n  lensProfile {{\\n    ...LensProfileFieldsFragment\\n    '
                   f'__typename\\n  }}\\n  timeoutUntil\\n  badge\\n  verification\\n  nft {{\\n    ...NftFieldsFragment\\n    __typename\\n  }}\\n  '
                   f'bAt\\n  xmtpWallet\\n  farcasterProfile {{\\n    ...FarcasterProfileFragment\\n    __typename\\n  }}\\n  isUserFollowing\\n  '
                   f'__typename\\n}}\\n\\nfragment FollowerFieldsFragment on followers {{\\n  profileId\\n  profile {{\\n    ...ProfileFieldsFragment\\n    '
                   f'isUserFollowing\\n    __typename\\n  }}\\n  followedProfileId\\n  followedProfile {{\\n    ...ProfileFieldsFragment\\n    '
                   f'isUserFollowing\\n    __typename\\n  }}\\n  createdAt\\n  __typename\\n}}","variables":{{"limit":{limit},"offset":{offset},'
                   f'"followedProfileId":"{profileID}"}}}}')

        data = self.__makeRequest(payload=payload)

        if data.get("errors") is not None:
            logging.error(f"Can`t get JWT token, plz refresh | Err: {data.get("errors")[0].get("message")}")
            return []

        followers_ids = []
        for follower in data.get("data").get("followers"):
            followers_ids.append(follower.get("profileId"))

        logging.debug(f"Parsed {len(followers_ids)} {profileID}`s followers")
        return followers_ids

    def getProfile(self, profileID: str) -> Profile:
        logging.debug(f"Getting {profileID} profile")

        payload: str = (
            f'{{"query":"query ProfileQuery($profileId: String!) {{\\n  profile: profiles_by_pk(id: $profileId) '
            f'{{\\n    ...ProfileDetailedFieldsFragment\\n    __typename\\n  }}\\n}}\\n\\nfragment ImageFieldsFragment on '
            f'images {{\\n  id\\n  profileId\\n  size\\n  bucket\\n  createdAt\\n  updatedAt\\n  filename\\n  '
            f'width\\n  height\\n  blurhash\\n  contentType\\n  pages\\n  sourceUrl\\n  status\\n  '
            f'__typename\\n}}\\n\\nfragment LensProfileFieldsFragment on lens_profiles {{\\n  id\\n  '
            f'lensProfileId\\n  lensHandle\\n  status\\n  txId\\n  ownerAddress\\n  followModule\\n  '
            f'isUserFollowing\\n  isFollowPending\\n  image {{\\n    ...ImageFieldsFragment\\n    __typename\\n  '
            f'}}\\n  __typename\\n}}\\n\\nfragment NftFieldsFragment on connected_nfts {{\\n  id\\n  profileId\\n  '
            f'chainId\\n  nftName\\n  nft_description\\n  nftTokenId\\n  contractAddress\\n  createdAt\\n  '
            f'updatedAt\\n  image {{\\n    ...ImageFieldsFragment\\n    __typename\\n  }}\\n  verifiedNftProject '
            f'{{\\n    id\\n    image {{\\n      ...ImageFieldsFragment\\n      __typename\\n    }}\\n    '
            f'__typename\\n  }}\\n  __typename\\n}}\\n\\nfragment FarcasterProfileFragment on farcaster_profiles '
            f'{{\\n  tokenId\\n  displayName\\n  name\\n  isUserFollowing\\n  imageRel {{\\n    '
            f'...ImageFieldsFragment\\n    __typename\\n  }}\\n  __typename\\n}}\\n\\nfragment '
            f'ProfileFieldsFragment on profiles {{\\n  id\\n  name\\n  username\\n  description\\n  credLevel\\n '
            f'image {{\\n    ...ImageFieldsFragment\\n    __typename\\n  }}\\n  createdAt\\n  updatedAt\\n  '
            f'lensProfile {{\\n    ...LensProfileFieldsFragment\\n    __typename\\n  }}\\n  timeoutUntil\\n  '
            f'badge\\n  verification\\n  nft {{\\n    ...NftFieldsFragment\\n    __typename\\n  }}\\n  bAt\\n  '
            f'xmtpWallet\\n  farcasterProfile {{\\n    ...FarcasterProfileFragment\\n    __typename\\n  }}\\n  '
            f'isUserFollowing\\n  __typename\\n}}\\n\\nfragment ProfileSocialMediaFieldsFragment on profiles {{\\n  '
            f'instagram\\n  facebook\\n  youtube\\n  twitter\\n  pinterest\\n  snapchat\\n  linkedin\\n  tiktok\\n  '
            f'website\\n  telegram\\n  discord\\n  __typename\\n}}\\n\\nfragment ProfileDetailedFieldsFragment on '
            f'profiles {{\\n  ...ProfileFieldsFragment\\n  ...ProfileSocialMediaFieldsFragment\\n  profileAggregates '
            f'{{\\n    followerCount\\n    followingCount\\n    __typename\\n  }}\\n  ccProfiles {{\\n    id\\n    '
            f'handle\\n    __typename\\n  }}\\n  coverImage {{\\n    ...ImageFieldsFragment\\n    __typename\\n  }}\\n  '
            f'__typename\\n}}","variables":{{"profileId":"{profileID}"}}}}')

        data = self.__makeRequest(payload=payload)

        if data.get("errors") is not None:
            logging.error(f"Can`t get JWT token, plz refresh | Err: {data.get("errors")[0].get("message")}")
            return Profile()

        profile: dict = data.get("data").get("profile")

        logging.debug(f"Got {profileID} profile\n{profile}")

        return Profile(
            name=profile.get("name"),
            username=profile.get("username"),
            descr=profile.get("description"),
            handle="" if profile.get("lensProfile") is None else profile.get("lensProfile").get("lensHandle"),
            wallet="" if profile.get("lensProfile") is None else profile.get("lensProfile").get("ownerAddress"),
            youtube=profile.get("youtube"),
            twitter=profile.get("twitter"),
            linkedin=profile.get("linkedin"),
            website=profile.get("website"),
            telegram=profile.get("telegram"),
            discord=profile.get("discord"),
        )

    def getMembers(self, communityId: str, limit: int = 100000, offset: int = 0) -> list[str]:
        logging.debug(f"Getting {communityId}`s members")

        payload: str = (
            f'{{"query":"query CommunityMembersQuery($communityId: String!, $limit: Int!, $offset: Int!) {{\\n  '
            f'community_members(\\n    limit: $limit\\n    offset: $offset\\n    order_by: {{createdAt: desc}}\\n '
            f'   where: {{communityId: {{_eq: $communityId}}, profile: {{bAt: {{_is_null: true}}}}}}\\n  ) {{\\n    '
            f'...CommunityMembersFieldsFragment\\n    __typename\\n  }}\\n}}\\n\\nfragment ImageFieldsFragment on '
            f'images {{\\n  id\\n  profileId\\n  size\\n  bucket\\n  createdAt\\n  updatedAt\\n  filename\\n  '
            f'width\\n  height\\n  blurhash\\n  contentType\\n  pages\\n  sourceUrl\\n  status\\n  '
            f'__typename\\n}}\\n\\nfragment LensProfileFieldsFragment on lens_profiles {{\\n  id\\n  '
            f'lensProfileId\\n  lensHandle\\n  status\\n  txId\\n  ownerAddress\\n  followModule\\n  '
            f'isUserFollowing\\n  isFollowPending\\n  image {{\\n    ...ImageFieldsFragment\\n    __typename\\n  '
            f'}}\\n  __typename\\n}}\\n\\nfragment NftFieldsFragment on connected_nfts {{\\n  id\\n  profileId\\n  '
            f'chainId\\n  nftName\\n  nft_description\\n  nftTokenId\\n  contractAddress\\n  createdAt\\n  '
            f'updatedAt\\n  image {{\\n    ...ImageFieldsFragment\\n    __typename\\n  }}\\n  verifiedNftProject '
            f'{{\\n    id\\n    image {{\\n      ...ImageFieldsFragment\\n      __typename\\n    }}\\n    '
            f'__typename\\n  }}\\n  __typename\\n}}\\n\\nfragment FarcasterProfileFragment on farcaster_profiles '
            f'{{\\n  tokenId\\n  displayName\\n  name\\n  isUserFollowing\\n  imageRel {{\\n    '
            f'...ImageFieldsFragment\\n    __typename\\n  }}\\n  __typename\\n}}\\n\\nfragment '
            f'ProfileFieldsFragment on profiles {{\\n  id\\n  name\\n  username\\n  description\\n  credLevel\\n '
            f' image {{\\n    ...ImageFieldsFragment\\n    __typename\\n  }}\\n  createdAt\\n  updatedAt\\n  '
            f'lensProfile {{\\n    ...LensProfileFieldsFragment\\n    __typename\\n  }}\\n  timeoutUntil\\n  '
            f'badge\\n  verification\\n  nft {{\\n    ...NftFieldsFragment\\n    __typename\\n  }}\\n  bAt\\n  '
            f'xmtpWallet\\n  farcasterProfile {{\\n    ...FarcasterProfileFragment\\n    __typename\\n  }}\\n  '
            f'isUserFollowing\\n  __typename\\n}}\\n\\nfragment CommunityMembersFieldsFragment on '
            f'community_members {{\\n  profile {{\\n    ...ProfileFieldsFragment\\n    __typename\\n  }}\\n  '
            f'createdAt\\n  userRole\\n  communityId\\n  profileId\\n  __typename\\n}}",'
            f'"variables":{{"limit":{limit},"offset":{offset},"communityId":"{communityId}"}}}}')

        data = self.__makeRequest(payload=payload)

        if data.get("errors") is not None:
            logging.error(f"Can`t get JWT token, plz refresh | Err: {data.get("errors")[0].get("message")}")
            return []

        ids: list[str] = []
        for member in data.get("data").get("community_members"):
            ids.append(member.get("profile").get("id"))

        logging.debug(f"Got {len(ids)} {communityId}`s members")
        return ids

    async def start(self, communityID: str):
        logging.debug(f"Start parsing...")

        members_ids = self.getMembers(communityId=communityID)
        l_m, count = len(members_ids), 1

        for member_id in members_ids:
            logging.debug(f"Progress: {count}/{l_m} users parsed")
            count += 1

            profile = self.getProfile(profileID=member_id)
            profileBIO = profile.generateBio()

            followers = self.getFollowers(profileID=member_id)

            await fileUtils.addLinesToFileAsync("results/to_parse.txt", followers)

            if profile.isEligible():
                logging.debug(f"Account {member_id} is eligible")
                await fileUtils.addLineToFileAsync("results/eligible.txt", profileBIO)
            else:
                logging.debug(f"Account {member_id} is not eligible")
                await fileUtils.addLineToFileAsync("results/not_eligible.txt", profileBIO)

        logging.debug("Parsing end.")

    async def startLocal(self, pathToIDs: str):
        logging.debug(f"Start parsing...")

        ids = fileUtils.readFile(filePath=pathToIDs)

        count, l_m = 1, len(ids)
        for id in ids:
            if len(id) > 29:
                await fileUtils.removeLineFromFileAsync("results/to_parse.txt", id)
                continue

            logging.debug(f"Progress: {count}/{l_m} users parsed")
            count += 1

            profile = self.getProfile(profileID=id)
            profileBIO = profile.generateBio()

            followers = self.getFollowers(profileID=id)

            await fileUtils.addLinesToFileAsync("results/to_parse.txt", followers)

            if profile.isEligible():
                logging.debug(f"Account {id} is eligible")
                await fileUtils.addLineToFileAsync("results/eligible.txt", profileBIO)
            else:
                logging.debug(f"Account {id} is not eligible")
                await fileUtils.addLineToFileAsync("results/not_eligible.txt", profileBIO)

            await fileUtils.removeLineFromFileAsync("results/to_parse.txt", id)

        logging.debug("Parsing end.")


async def main():
    phaverParser = PhaverParser()

    # await phaverParser.start("6210cc7a-a4a8-4dfa-bf57-f79d13654c3c")
    await phaverParser.startLocal("results/to_parse.txt")



if __name__ == "__main__":
    asyncio.run(main())
