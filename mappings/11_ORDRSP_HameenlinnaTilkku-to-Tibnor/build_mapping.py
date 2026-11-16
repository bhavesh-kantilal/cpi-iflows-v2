"""Build Map_HammelinnaTilkkuHub_TibnorS4_OrderConfirmation_ORDRSP.

Run:  py -I mappings/11_ORDRSP_HameenlinnaTilkku-to-Tibnor/build_mapping.py
Same shared spec (1002257_ORDRSP_Tilkku-to-Tibnor_MappingSpec_v0.1.xlsx) as the Raahe Tilkku mapping. The logic is
build() in mappings/7_ORDRSP_RaaheTilkku-to-Tibnor/build_mapping.py; only the VM-01 values of this mill differ.
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "ordrsp_tilkku", HERE.parent / "7_ORDRSP_RaaheTilkku-to-Tibnor" / "build_mapping.py")
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)

MILL = dict(
    name="Map_HammelinnaTilkkuHub_TibnorS4_OrderConfirmation_ORDRSP",
    gln="00372389445751",            # Header/InterchangeSender of Hämeenlinna Tilkku (VM-01)
    sndprn="0000086245",             # Tibnor vendor 86245
)

if __name__ == "__main__":
    sys.exit(core.run(MILL, HERE))
