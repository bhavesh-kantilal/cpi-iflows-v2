"""Build Map_HammelinnaTilkkuHub_TibnorS4_DeliveryNotice_DESADV.

Run:  py -I mappings/12_DESADV_HameenlinnaTilkku-to-Tibnor/build_mapping.py
Same shared spec (1000761_DESADV_RaaheTilkku-to-Tibnor_MappingSpec_v0.1.xlsx) as the Raahe Tilkku mapping. The logic
is build() in mappings/8_DESADV_RaaheTilkku-to-Tibnor/build_mapping.py; this mill groups by heat number (VM-02).
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "desadv_tilkku", HERE.parent / "8_DESADV_RaaheTilkku-to-Tibnor" / "build_mapping.py")
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)

MILL = dict(
    name="Map_HammelinnaTilkkuHub_TibnorS4_DeliveryNotice_DESADV",
    gln="00372389445751",            # VM-01: Header/InterchangeSender of Hämeenlinna Tilkku
    sndprn="0000086245",
    vendor="86245",
    group_by="heat",                 # VM-02: heat number, one E1EDL11 per SinglePart
)

if __name__ == "__main__":
    sys.exit(core.run(MILL, HERE))
