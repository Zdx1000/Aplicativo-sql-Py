"""Configurações carregadas de variáveis de ambiente (.env) com defaults seguros.

Exponha constantes para uso em toda a aplicação sem acoplar à camada de banco.
"""

from __future__ import annotations

import os
import sys
import json
from pathlib import Path
from typing import List


# --- Carregamento do .env (compatível com PyInstaller/auto-py-to-exe) ---
def _load_env_if_possible() -> None:
    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:
        return

    loaded = False

    try:
        loaded = load_dotenv(dotenv_path=Path.cwd() / ".env", override=False)
    except Exception:
        pass

    try:
        if not loaded and getattr(sys, "frozen", False):
            exe_dir = Path(sys.executable).resolve().parent
            loaded = load_dotenv(dotenv_path=exe_dir / ".env", override=False)
    except Exception:
        pass

    try:
        if not loaded:
            loaded = load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=False)
    except Exception:
        pass

    try:
        if not loaded:
            base = getattr(sys, "_MEIPASS", None)
            if base:
                load_dotenv(dotenv_path=Path(base) / ".env", override=False)
    except Exception:
        pass


_load_env_if_possible()


def _parse_env_list(var_name: str, default: list[str]) -> list[str]:
    """Lê uma lista do ambiente por CSV simples ou JSON.

    Prioridades:
      1) VAR_NAME (se iniciar com '[' e terminar com ']': tenta JSON; caso contrário, CSV)
      2) VAR_NAME_JSON (JSON estrito)
      3) default
    """
    raw = os.getenv(var_name)
    if raw is None:
        raw = os.getenv(f"{var_name}_JSON")
        if raw is None:
            return list(default)
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return [str(x).strip() for x in data if str(x).strip()]
            return list(default)
        except Exception:
            return list(default)

    s = raw.strip()
    # Tenta JSON quando parece uma lista
    if s.startswith("[") and s.endswith("]"):
        try:
            data = json.loads(s)
            if isinstance(data, list):
                return [str(x).strip() for x in data if str(x).strip()]
        except Exception:
            pass
    # Fallback: CSV separado por vírgula
    return [p.strip() for p in s.split(",") if p.strip()]


# Defaults usados caso .env não defina
SETORES_DEFAULT: list[str] = [
    "Produção",
    "Recebimento",
    "Armazenagem e Ressuprimento",
    "SME - Logistica reversa",
    "Controle de Estoque",
    "Efacil",
    "Qualidade",
    "Expedição",
]


# Variável global: lista de setores, configurável via .env
SETORES: List[str] = _parse_env_list("SETORES", SETORES_DEFAULT)
