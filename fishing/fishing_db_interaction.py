# This is where the database interactions are
from datetime import datetime, timedelta  # noqa
from pathlib import Path
from enum import Enum

from aiosqlite import connect, OperationalError, Connection

from fishing.utils import Fish, NetsEnum, Shark, Rarity


base_db_path = Path(__file__).parent.parent.parent / "Shark-Bot" / "databases"
shark_file_path = base_db_path / "shark_game.db"


async def get_discord_id(twitch_username: str) -> int:
    async with connect(shark_file_path) as conn:
        async with conn.execute("SELECT user_id FROM dex WHERE twitch_user=?", (twitch_username,)) as cur:
            result = await cur.fetchone()
            if result is None:
                raise ValueError(f"Could not find user {twitch_username}")
            return result[0]


async def get_discord_username(twitch_username: str) -> str:
    async with connect(shark_file_path) as conn:
        async with conn.execute("SELECT username FROM dex WHERE twitch_user=?", (twitch_username,)) as cur:
            result = await cur.fetchone()
            if result is None:
                raise ValueError(f"Could not find user {twitch_username}")
            return result[0]


async def add_fish(fish: Fish):
    discord_id = await get_discord_id(fish.username)
    async with connect(shark_file_path) as conn:
        async with conn.execute("SELECT twitch_id FROM fish WHERE user_id=?", (discord_id,)) as cur:
            result = await cur.fetchone()
            if result is None:
                await conn.execute(
                    "UPDATE fish SET twitch_id=?, twitch_username=? WHERE discord_id=?",
                    (fish.user_id, fish.username, discord_id),
                )
                await conn.commit()

        match fish.rarity:
            case Rarity.TRASH:
                await conn.execute("UPDATE fish SET trash = trash + 1 WHERE twitch_id=?", (fish.user_id,))
            case Rarity.COMMON:
                await conn.execute("UPDATE fish SET common = common + 1 WHERE twitch_id=?", (fish.user_id,))
            case Rarity.SHINY:
                await conn.execute("UPDATE fish SET shiny = shiny + 1 WHERE twitch_id=?", (fish.user_id,))
            case Rarity.LEGENDARY:
                await conn.execute("UPDATE fish SET legendary = legendary + 1 WHERE twitch_id=?", (fish.user_id,))

        new_coin_value = await get_new_coins_for_user(fish, discord_id)

        async with conn.execute("SELECT id FROM dex WHERE user_id=? ORDER BY id DESC", (discord_id,)) as cur:
            result = await cur.fetchone()
            if result is None:
                raise ValueError("User is not in the dex")
            id_value = result[0]

        await conn.execute("UPDATE dex SET coins=? WHERE id=?", (new_coin_value, id_value))

        await conn.commit()


class NetTypes(Enum):
    LEATHER = 1
    GOLD = 2
    TITANIUM = 3
    DOOM = 4


async def is_net_available(username: str, net: str) -> bool:
    async with connect(shark_file_path) as conn:
        all_nets: list = []
        nets_available: dict[str, bool] = {}
        try:
            async with conn.execute(
                'SELECT "rope net", "leather net", "gold net", "titanium net", "net of doom" FROM nets WHERE user_id=?',
                (await get_discord_id(username),),
            ) as cur:
                all_nets.extend(await cur.fetchall())

        except OperationalError:
            return False

    i = 0
    try:
        for _net in all_nets[0]:
            if _net == 0:
                i += 1
            else:
                match i:
                    case NetTypes.LEATHER.value:
                        nets_available["leather net"] = True
                    case NetTypes.GOLD.value:
                        nets_available["gold net"] = True
                    case NetTypes.TITANIUM.value:
                        nets_available["titanium net"] = True
                    case NetTypes.DOOM.value:
                        nets_available["net of doom"] = True
                i += 1
    except IndexError:
        return False
    if net.strip() in nets_available.keys():
        return True
    return False


async def remove_net_use(catch: Shark | Fish):
    async with connect(shark_file_path) as conn:
        net = catch.net_used.net
        discord_id = await get_discord_id(catch.username)
        if isinstance(net, NetsEnum):
            net = str(net)
        async with conn.execute(
            "SELECT net_uses, id FROM dex WHERE user_id=? AND net=? ORDER BY id DESC", (discord_id, net)
        ) as cur:
            result = await cur.fetchone()
            if result is None:
                raise ValueError("Could not find user")
            available_net_uses: int = result[0]
            id_value: int = result[1]
            if available_net_uses - 1 <= 0:
                await disable_net(catch.net_used.net, conn, await get_discord_id(catch.username))
            await conn.execute("UPDATE dex SET net_uses = net_uses - 1 WHERE id=?", (id_value,))
            await conn.commit()


async def disable_net(net: NetsEnum | str, conn: Connection, discord_id: int):
    match net:
        case NetsEnum.ROPE:
            pass
        case NetsEnum.LEATHER:
            await conn.execute("UPDATE nets SET 'leather net'=0 WHERE user_id=?", (discord_id,))
        case NetsEnum.GOLD:
            await conn.execute("UPDATE nets SET 'gold net'=0 WHERE user_id=?", (discord_id,))
        case NetsEnum.TITANIUM:
            await conn.execute("UPDATE nets SET 'titanium net'=0 WHERE user_id=?", (discord_id,))
        case NetsEnum.DOOM:
            await conn.execute("UPDATE nets SET 'net of doom'=0 WHERE user_id=?", (discord_id,))
    await conn.commit()


async def get_shark_names():
    async with connect(shark_file_path) as conn:
        async with conn.execute("SELECT name FROM sharks WHERE rarity = 1") as cur:
            names: list[str] = []
            for name in await cur.fetchall():
                names.append(name[0])
    return names


async def get_shark_info(shark: Shark) -> tuple[str, str]:
    async with connect(shark_file_path) as conn:
        async with conn.execute("SELECT fact, weight FROM sharks WHERE name=?", (shark.name,)) as cur:
            result = await cur.fetchone()
            if result is None:
                raise ValueError("Shark not found!")
            return (result[0], result[1])


async def get_new_coins_for_user(catch: Shark | Fish, discord_id: int):
    async with connect(shark_file_path) as conn:
        async with conn.execute("SELECT coins FROM dex WHERE user_id=? ORDER BY id DESC", (discord_id,)) as cur:
            result = await cur.fetchone()
            if result is None:
                raise ValueError("Could not find User in dex!!")
            coins: int = result[0]

    return coins + catch.coin_value


async def get_user_level(discord_id: int) -> int:
    async with connect(shark_file_path) as conn:
        async with conn.execute("SELECT level FROM dex WHERE user_id=? ORDER BY id DESC LIMIT 1", (discord_id,)) as cur:
            result = await cur.fetchone()
            if result is None:
                raise ValueError("Could not find user in dex!!")
            return result[0]


async def add_shark(shark: Shark):
    user_id = await get_discord_id(shark.username)
    username = await get_discord_username(shark.username)
    shark_info = await get_shark_info(shark)
    async with connect(shark_file_path) as conn:
        await conn.execute(
            "INSERT OR IGNORE INTO dex "
            "(user_id, username, shark, time, fact, weight, net, coins, rarity, level, net_uses, twitch_user, twitch_id, caught_on)"  # noqa
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                user_id,
                username,
                shark.name,
                shark.time_caught,
                shark_info[0],
                shark_info[1],
                NetsEnum.ROPE,
                await get_new_coins_for_user(shark, user_id),
                shark.rarity.value,
                await get_user_level(user_id),
                0,
                shark.username,
                shark.user_id,
                "twitch",
            ),
        )
        await conn.commit()
