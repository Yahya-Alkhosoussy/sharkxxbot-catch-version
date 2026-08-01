# This is where the database interactions are
from datetime import datetime, timedelta # noqa
from pathlib import Path

from aiosqlite import connect

from fishing.utils import Fish

base_db_path = Path(__file__).parent.parent / "Shark-Bot" / "databases"
shark_file_path = base_db_path / "shark_game.db"


async def add_fish(fish: Fish):
    async with connect(shark_file_path) as conn:
        await conn.execute("INSERT OR IGNORE INTO fish (rarity, net_used, size) VALUES (?, ?, ?)", (None, None, None))
        await conn.commit()
