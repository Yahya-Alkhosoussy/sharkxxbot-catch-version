from fishing.utils import Fish, Nets, Rarity, Size, Boost, Shark, SharkRarity # noqa
from twitchAPI.chat import Chat, ChatCommand
from fishing.fishing_db_interaction import is_net_available, get_shark_names, add_shark, add_fish # noqa
from random import randint
from datetime import datetime
from zoneinfo import ZoneInfo

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
    async def __get_caught_item(self, username: str, net_used: Nets, boost: Boost, user_id: int = 0) -> Fish | Shark:
        catch_type = randint(1, 100)
        if catch_type <= 5:
            names = await get_shark_names()
            idx = randint(0, len(names) - 1)
            shark = names[idx]
            return Shark(user_id, net_used, shark, SharkRarity.VERY_COMMON, Rarity.COMMON, boost)
        elif catch_type <= 25:
            fish_rarity = self.__get_fish_rarity()
            return Fish(fish_rarity, net_used, Size.LARGE, boost)
        if catch_type <= 50:
            fish_rarity = self.__get_fish_rarity()
            return Fish(fish_rarity, net_used, Size.MEDIUM, boost)
        if catch_type <= 80:
            fish_rarity = self.__get_fish_rarity()
            return Fish(fish_rarity, net_used, Size.SMALL, boost)
        return Fish(Rarity.TRASH, net_used, Size.LARGE, boost)

    async def fishing_cmd(self, cmd: ChatCommand):
        available = is_net_available(cmd.name, cmd.text[len('!fishing') :])
        if not available:
            net = Nets("rope net")
        else:
            net = Nets(cmd.text[len('!fishing') :])

        odd = randint(0, 99)
        catch_odds = net.get_catch_odds
        if odd <= catch_odds:
            boost = Boost(False, 2)
            catch = await self.__get_caught_item(cmd.name, net, boost)
            if isinstance(catch, Shark):
                time = datetime.now().astimezone(ZoneInfo("America/Chicago"))
                time_caught = f"{time.date()} {time.hour}"
                await add_shark(cmd.name, SharkRarity.COMMON, time_caught, 0)
                return
