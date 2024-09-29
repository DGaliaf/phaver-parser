import asyncio
import time

import requests

from models import Profile, HeaderData

from utils import fileUtils

class PhaverParser:
    def __init__(self):
        self.graphUrls = "https://gql.next.phaver.com/v1/graphql"

        self.header = self.__genHeader(HeaderData(
            bearerToken="",
            baggage="",
            sentry="",
            requestID=""
        ))

    def __genHeader(self, headerData: HeaderData) -> dict:
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

    def getFollowers(self, profileID: str, limit: int = 20, offset: int = 0) -> list[str]:
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

        response = requests.post(self.graphUrls, headers=self.header, data=payload)
        sleep_dur = 4
        while response.status_code == 429:
            time.sleep(sleep_dur)
            response = requests.post(self.graphUrls, headers=self.header, data=payload)

            sleep_dur += 0.5

        data = response.json()

        if data.get("errors") is not None:
            print("Can`t get JWT token, plz refresh,", data.get("errors")[0].get("message"))
            return []

        followers_ids = []
        for follower in data.get("data").get("followers"):
            followers_ids.append(follower.get("profileId"))

        return followers_ids

    def getProfile(self, profileID: str) -> Profile:
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

        response = requests.post(self.graphUrls, headers=self.header, data=payload)
        sleep_dur = 4
        while response.status_code == 429:
            time.sleep(sleep_dur)
            response = requests.post(self.graphUrls, headers=self.header, data=payload)

            sleep_dur += 0.5

        data = response.json()

        if data.get("errors") is not None:
            print("Can`t get JWT token, plz refresh,", data.get("errors")[0].get("message"))
            return Profile()

        profile: dict = data.get("data").get("profile")

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

    def getMembers(self, communityId: str, limit: int = 100000, offset: int = 475) -> list[str]:
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

        response = requests.post(self.graphUrls, headers=self.header, data=payload)
        sleep_dur = 4
        while response.status_code == 429:
            time.sleep(sleep_dur)
            response = requests.post(self.graphUrls, headers=self.header, data=payload)

            sleep_dur += 0.5

        data = response.json()

        if data.get("errors") is not None:
            print("Can`t get JWT token, plz refresh,", data.get("errors")[0].get("message"))
            return []

        ids: list[str] = []
        for member in data.get("data").get("community_members"):
            ids.append(member.get("profile").get("id"))

        return ids

    async def start(self, communityID: str):
        members_ids = self.getMembers(communityId=communityID)
        l_m, count = len(members_ids), 1

        for member_id in members_ids:
            print(f"[+] {count}/{l_m}")
            count += 1

            profile = self.getProfile(profileID=member_id)
            profileBIO = profile.generateBio()

            followers = self.getFollowers(profileID=member_id)

            await fileUtils.addLinesToFileAsync("results/to_parse.txt", followers)

            if profile.isEligible():
                await fileUtils.addLineToFileAsync("results/eligible.txt", profileBIO)
            else:
                await fileUtils.addLineToFileAsync("results/not_eligible.txt", profileBIO)


async def main():
    phaverParser = PhaverParser()

    await phaverParser.start("6210cc7a-a4a8-4dfa-bf57-f79d13654c3c")


if __name__ == "__main__":
    asyncio.run(main())
