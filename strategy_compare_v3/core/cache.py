"""
============================================================
Institutional Strategy Comparison Engine V3
File : core/cache.py

Caching Utilities

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import hashlib
import pickle
import shutil
import time
from pathlib import Path
from typing import Any

from core.constants import PROJECT_ROOT
from core.logger import get_logger

logger = get_logger(__name__)

CACHE_DIR = PROJECT_ROOT / "outputs" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class CacheManager:
    """
    Simple disk-based cache manager.
    """

    def __init__(
        self,
        cache_dir: Path = CACHE_DIR
    ):

        self.cache_dir = cache_dir

        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    # -----------------------------------------------------

    @staticmethod
    def _hash_key(key: str) -> str:

        return hashlib.sha256(
            key.encode("utf-8")
        ).hexdigest()

    # -----------------------------------------------------

    def _cache_file(
        self,
        key: str
    ) -> Path:

        filename = (
            self._hash_key(key)
            + ".pkl"
        )

        return self.cache_dir / filename

    # -----------------------------------------------------

    def exists(
        self,
        key: str
    ) -> bool:

        return self._cache_file(
            key
        ).exists()

    # -----------------------------------------------------

    def save(
        self,
        key: str,
        value: Any
    ) -> None:

        path = self._cache_file(key)

        with open(
            path,
            "wb"
        ) as file:

            pickle.dump(
                value,
                file,
                protocol=pickle.HIGHEST_PROTOCOL
            )

        logger.info(
            "Cached: %s",
            key
        )

    # -----------------------------------------------------

    def load(
        self,
        key: str
    ) -> Any:

        path = self._cache_file(key)

        if not path.exists():

            raise FileNotFoundError(
                f"Cache not found: {key}"
            )

        with open(
            path,
            "rb"
        ) as file:

            return pickle.load(file)

    # -----------------------------------------------------

    def delete(
        self,
        key: str
    ) -> None:

        path = self._cache_file(key)

        if path.exists():

            path.unlink()

            logger.info(
                "Removed cache: %s",
                key
            )

    # -----------------------------------------------------

    def clear(self) -> None:

        shutil.rmtree(
            self.cache_dir,
            ignore_errors=True
        )

        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        logger.info(
            "Cache cleared."
        )

    # -----------------------------------------------------

    def cache_size_mb(self) -> float:

        size = sum(

            f.stat().st_size

            for f in self.cache_dir.glob("*.pkl")

        )

        return round(

            size / (1024 ** 2),

            4

        )

    # -----------------------------------------------------

    def cache_count(self) -> int:

        return len(

            list(

                self.cache_dir.glob("*.pkl")

            )

        )

    # -----------------------------------------------------

    def save_with_timestamp(
        self,
        key: str,
        value: Any
    ) -> None:

        payload = {

            "timestamp":

                time.time(),

            "value":

                value

        }

        self.save(
            key,
            payload
        )

    # -----------------------------------------------------

    def load_with_timestamp(
        self,
        key: str,
        max_age_seconds: int | None = None
    ) -> Any:

        payload = self.load(key)

        if max_age_seconds is not None:

            age = (

                time.time()

                -

                payload["timestamp"]

            )

            if age > max_age_seconds:

                raise TimeoutError(

                    "Cached object expired."

                )

        return payload["value"]


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    cache = CacheManager()

    cache.save(
        "sample",
        {"a": 10}
    )

    print(

        cache.load(
            "sample"
        )

    )

    print(

        cache.cache_count()

    )

    print(

        cache.cache_size_mb(),

        "MB"

    )