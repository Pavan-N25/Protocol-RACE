"""Configuration loader for Protocol-RACE.

Tries to load `config.yaml` from the repository root. If `pyyaml` is not
installed, falls back to a tiny ad-hoc parser for the specific config layout.
"""
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def _parse_simple_yaml(path: Path):
    cfg = {}
    if not path.exists():
        return cfg
    cur = cfg
    with path.open("r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip()
                v = v.strip()
                if v == "":
                    # create nested dict
                    cur[k] = {}
                    cur = cur[k]
                else:
                    # try to coerce
                    if v.lower() in ("true", "false"):
                        cur[k] = v.lower() == "true"
                    else:
                        try:
                            cur[k] = float(v)
                        except Exception:
                            cur[k] = v
    return cfg


def load_config() -> dict:
    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "config.yaml"
    try:
        import yaml

        with cfg_path.open("r", encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh) or {}
            return cfg
    except Exception:
        logger.debug("PyYAML not available or failed; using simple parser")
        return _parse_simple_yaml(cfg_path)


_CONFIG = load_config()


def get_config() -> dict:
    return _CONFIG
