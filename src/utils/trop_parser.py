"""
Parser dos arquivos brutos .trop (formato SINEX-TRO / NGL) do GNSS.
Extrai a série de TRWET (Zenith Wet Delay) a partir dos arquivos diários
disponíveis em database/dados_gnss/<ESTACAO>/<ESTACAO>.<ANO>.trop/*.trop
"""

import re
from pathlib import Path

import pandas as pd

_EPOCH_RE = re.compile(r"^(\d{2}):(\d{3}):(\d{5})$")


def _epoch_to_datetime(epoch: str):
    """Converte um epoch NGL no formato AA:DDD:SSSSS para Timestamp."""
    m = _EPOCH_RE.match(epoch)
    if not m:
        return None
    yy, doy, sod = int(m.group(1)), int(m.group(2)), int(m.group(3))
    year = 2000 + yy
    return pd.Timestamp(year=year, month=1, day=1) + pd.Timedelta(days=doy - 1, seconds=sod)


def parse_trop_file(path: Path) -> list:
    """Extrai pares (data_completa, TRWET) do bloco +TROP/SOLUTION de um arquivo .trop."""
    rows = []
    in_block = False
    with open(path, "r", encoding="latin1") as f:
        for line in f:
            if line.startswith("+TROP/SOLUTION"):
                in_block = True
                continue
            if line.startswith("-TROP/SOLUTION"):
                break
            if not in_block or line.startswith("*"):
                continue
            parts = line.split()
            if len(parts) < 5:
                continue
            ts = _epoch_to_datetime(parts[1])
            if ts is None:
                continue
            try:
                trwet = float(parts[4])
            except ValueError:
                continue
            rows.append((ts, trwet))
    return rows


def parse_station_trwet(station_dir: Path) -> pd.DataFrame:
    """Percorre todos os arquivos .trop de uma estação e monta o DataFrame completo."""
    all_rows = []
    for trop_file in sorted(station_dir.glob("*.trop/*.trop")):
        all_rows.extend(parse_trop_file(trop_file))

    df = pd.DataFrame(all_rows, columns=["data_completa", "TRWET"])
    if not df.empty:
        df.sort_values("data_completa", inplace=True)
        df.reset_index(drop=True, inplace=True)
    return df