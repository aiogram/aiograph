import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from aiograph import Telegraph

access_token = None


@pytest.yield_fixture()
@pytest.mark.asyncio
async def telegraph():
    aiograph = Telegraph(token=access_token)
    yield aiograph
    await aiograph.close()
