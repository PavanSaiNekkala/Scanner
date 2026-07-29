"""
serialization.py
================

Institutional Serialization Framework.
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

import pandas as pd


# ==========================================================
# Serializer
# ==========================================================


class Serializer:
    """
    Institutional serialization engine.
    """

    def __init__(
        self,
        output_directory: str | Path = "outputs",
    ) -> None:

        self.output_directory = Path(
            output_directory,
        )

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def resolve(
        self,
        filename: str,
    ) -> Path:
        """
        Resolve file path.
        """

        return (
            self.output_directory
            / filename
        )

# ==========================================================
# JSON
# ==========================================================


    def save_json(
        self,
        obj: Any,
        filename: str,
        indent: int = 4,
    ) -> Path:
        """
        Save object as JSON.
        """

        path = self.resolve(
            filename,
        )

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                obj,
                file,
                indent=indent,
                default=str,
            )

        return path

    def load_json(
        self,
        filename: str,
    ) -> Any:
        """
        Load JSON.
        """

        path = self.resolve(
            filename,
        )

        with open(
            path,
            encoding="utf-8",
        ) as file:

            return json.load(
                file,
            )

# ==========================================================
# CSV
# ==========================================================


    def save_csv(
        self,
        dataframe: pd.DataFrame,
        filename: str,
        **kwargs,
    ) -> Path:
        """
        Save DataFrame as CSV.
        """

        path = self.resolve(
            filename,
        )

        dataframe.to_csv(
            path,
            **kwargs,
        )

        return path

    def load_csv(
        self,
        filename: str,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Load CSV.
        """

        path = self.resolve(
            filename,
        )

        return pd.read_csv(
            path,
            **kwargs,
        )

# ==========================================================
# Pickle
# ==========================================================


    def save_pickle(
        self,
        obj: Any,
        filename: str,
    ) -> Path:
        """
        Save pickle.
        """

        path = self.resolve(
            filename,
        )

        with open(
            path,
            "wb",
        ) as file:

            pickle.dump(
                obj,
                file,
            )

        return path

    def load_pickle(
        self,
        filename: str,
    ) -> Any:
        """
        Load pickle.
        """

        path = self.resolve(
            filename,
        )

        with open(
            path,
            "rb",
        ) as file:

            return pickle.load(
                file,
            )


# ==========================================================
# Excel
# ==========================================================

    def save_excel(
        self,
        dataframe: pd.DataFrame,
        filename: str,
        sheet_name: str = "Sheet1",
        index: bool = False,
    ) -> Path:
        """
        Save DataFrame as Excel.
        """

        path = self.resolve(
            filename,
        )

        with pd.ExcelWriter(
            path,
            engine="openpyxl",
        ) as writer:

            dataframe.to_excel(
                writer,
                sheet_name=sheet_name,
                index=index,
            )

        return path

    def load_excel(
        self,
        filename: str,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Load Excel file.
        """

        path = self.resolve(
            filename,
        )

        return pd.read_excel(
            path,
            **kwargs,
        )


# ==========================================================
# Parquet
# ==========================================================

    def save_parquet(
        self,
        dataframe: pd.DataFrame,
        filename: str,
        compression: str = "snappy",
        **kwargs,
    ) -> Path:
        """
        Save DataFrame as Parquet.
        """

        path = self.resolve(
            filename,
        )

        dataframe.to_parquet(
            path,
            compression=compression,
            index=False,
            **kwargs,
        )

        return path

    def load_parquet(
        self,
        filename: str,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Load Parquet file.
        """

        path = self.resolve(
            filename,
        )

        return pd.read_parquet(
            path,
            **kwargs,
        )


# ==========================================================
# Feather
# ==========================================================

    def save_feather(
        self,
        dataframe: pd.DataFrame,
        filename: str,
        **kwargs,
    ) -> Path:
        """
        Save DataFrame as Feather.
        """

        path = self.resolve(
            filename,
        )

        dataframe.reset_index(
            drop=True,
        ).to_feather(
            path,
            **kwargs,
        )

        return path

    def load_feather(
        self,
        filename: str,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Load Feather file.
        """

        path = self.resolve(
            filename,
        )

        return pd.read_feather(
            path,
            **kwargs,
        )

# ==========================================================
# File Utilities
# ==========================================================

    def exists(
        self,
        filename: str,
    ) -> bool:
        """
        Return True if file exists.
        """

        return self.resolve(
            filename,
        ).exists()

    def delete(
        self,
        filename: str,
    ) -> bool:
        """
        Delete a file.
        """

        path = self.resolve(
            filename,
        )

        if not path.exists():
            return False

        path.unlink()

        return True

    def list_files(
        self,
        pattern: str = "*",
    ) -> list[Path]:
        """
        List files in output directory.
        """

        return sorted(
            self.output_directory.glob(
                pattern,
            )
        )

    def clear(
        self,
        pattern: str = "*",
    ) -> int:
        """
        Delete matching files.
        """

        count = 0

        for file in self.list_files(
            pattern,
        ):

            if file.is_file():

                file.unlink()

                count += 1

        return count


# ==========================================================
# Metadata
# ==========================================================

    def metadata(
        self,
        filename: str,
    ) -> dict[str, Any]:
        """
        Return file metadata.
        """

        path = self.resolve(
            filename,
        )

        if not path.exists():

            raise FileNotFoundError(
                path,
            )

        stat = path.stat()

        return {
            "name": path.name,
            "path": str(path),
            "suffix": path.suffix,
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
        }

    def file_size(
        self,
        filename: str,
    ) -> int:
        """
        Return file size in bytes.
        """

        path = self.resolve(
            filename,
        )

        if not path.exists():

            raise FileNotFoundError(
                path,
            )

        return path.stat().st_size


# ==========================================================
# Dunder Methods
# ==========================================================

    def __repr__(
        self,
    ) -> str:
        """
        String representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"output_directory='{self.output_directory}')"
        )
    

__all__ = [
    "Serializer",
]