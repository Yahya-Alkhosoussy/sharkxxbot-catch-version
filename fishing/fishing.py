from datetime import datetime
from random import randint
from zoneinfo import ZoneInfo

from twitchAPI.chat import Chat, ChatCommand, ChatUser

from fishing.fishing_db_interaction import add_fish, add_shark, get_shark_names, is_net_available  # noqa
from fishing.utils import Boost, Fish, Nets, Rarity, Shark, SharkRarity, Size


# Fishing Functionality
class Fishing:
    def __init__(self, chat: Chat):
        self.chat = chat

    def __get_fish_rarity(self) -> Rarity:
        fish_rarity = randint(1, 100)
        if fish_rarity <= 10:
            return Rarity.LEGENDARY
        if fish_rarity <= 40:
            return Rarity.SHINY
        return Rarity.COMMON

    # helper function
    async def __get_caught_item(self, user: ChatUser, net_used: Nets, boost: Boost) -> Fish | Shark:
        catch_type = randint(1, 100)
        if catch_type <= 5:
            names = await get_shark_names()
            idx = randint(0, len(names) - 1)
            shark = names[idx]
            time = datetime.now().astimezone(ZoneInfo("America/Chicago"))
            time_caught = f"{time.date()} {time.hour}"
            return Shark(user.name, int(user.id), net_used, shark, SharkRarity.VERY_COMMON, Rarity.COMMON, boost, time_caught)
        elif catch_type <= 25:
            fish_rarity = self.__get_fish_rarity()
            return Fish(user.name, int(user.id), fish_rarity, net_used, Size.LARGE, boost)
        if catch_type <= 50:
            fish_rarity = self.__get_fish_rarity()
            return Fish(user.name, int(user.id), fish_rarity, net_used, Size.MEDIUM, boost)
        if catch_type <= 80:
            fish_rarity = self.__get_fish_rarity()
            return Fish(user.name, int(user.id), fish_rarity, net_used, Size.SMALL, boost)
        return Fish(user.name, int(user.id), Rarity.TRASH, net_used, Size.LARGE, boost)

    async def fishing_cmd(self, cmd: ChatCommand):
        if cmd.text[len("!fish") :] != "":
            available = await is_net_available(cmd.user.name, cmd.text[len("!fish") :])
            if not available:
                net = Nets("rope net")
                await cmd.reply("This net is not available or I could not find it. Using basic net.")
            else:
                net = Nets(cmd.text[len("!fish") :].strip())
        else:
            net = Nets("rope net")

        odd = randint(0, 99)
        catch_odds = net.get_catch_odds
        if odd >= catch_odds:
            boost = Boost(False, 2)
            catch = await self.__get_caught_item(cmd.user, net, boost)
            if isinstance(catch, Shark):
                await add_shark(catch)
                await cmd.reply(f"You have successfully caught a {catch.name}! You got {catch.coin_value} coins.")
                return
            await add_fish(catch)
            await cmd.reply(f"You have successfully caught a {catch.rarity} fish! You got {catch.coin_value} coins.")
        else:
            await cmd.reply("Unfortunately you have failed to catch anything.")
