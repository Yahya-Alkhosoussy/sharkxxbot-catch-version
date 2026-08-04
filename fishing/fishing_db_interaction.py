# This is where the database interactions are
from datetime import datetime, timedelta # noqa
from pathlib import Path
from typing import Any
from enum import Enum

from aiosqlite import connect, OperationalError

from fishing.utils import Fish

base_db_path = Path(__file__).parent.parent / "Shark-Bot" / "databases"
shark_file_path = base_db_path / "shark_game.db"


async def add_fish(fish: Fish):
    async with connect(shark_file_path) as conn:
        await conn.execute("INSERT OR IGNORE INTO fish (rarity, net_used, size) VALUES (?, ?, ?)", (None, None, None))
        await conn.commit()

class NetTypes(Enum):
    LEATHER = 1
    GOLD = 2
    TITANIUM = 3
    DOOM = 4

async def is_net_available(username: str, net: str) -> bool:
    async with connect(shark_file_path) as conn:
        all_nets: Any = []
        nets_available: dict[str, bool] = {}
        try:
            async with conn.execute(f"SELECT * FROM '{username} nets'") as cur:
                all_nets.extend(await cur.fetchall())
        except OperationalError:
            return False

    i = 0
    try:
        for net in all_nets[0]:
            if net == 0:
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
    if net in nets_available.keys():
        return True
    return False


async def get_shark_names():
    async with connect(shark_file_path) as conn:
        async with conn.execute("SELECT name FROM sharks WHERE rarity = 1") as cur:
            names: list[str] = []
            for name in await cur.fetchall():
                names.append(name[0])
    return names

async def add_shark(username: str, rarity: str, time: str, net_uses: int):
    pass
