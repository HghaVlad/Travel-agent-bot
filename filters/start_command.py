from aiogram.dispatcher.filters import Filter
from aiogram.utils.deep_linking import decode_payload


class IsJourneyShare(Filter):
    async def check(self, message) -> bool:
        args = message.get_args()
        payload = decode_payload(args)
        return "journey_share" in payload


class IsFriendRequest(Filter):
    async def check(self, message) -> bool:
        args = message.get_args()
        payload = decode_payload(args)
        return "friend_request" in payload


class IsNotLink(Filter):
    async def check(self, message) -> bool:
        args = message.get_args()
        payload = decode_payload(args)
        return "journey_share" not in payload and "friend_request" not in payload
