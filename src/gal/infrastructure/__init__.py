"""Entrada e saída: arquivos de texto e persistência da tabela léxica."""

from gal.infrastructure.file_io import read_text, write_text, write_tokens
from gal.infrastructure.table_storage import load_table, save_table

__all__ = ["load_table", "read_text", "save_table", "write_text", "write_tokens"]
