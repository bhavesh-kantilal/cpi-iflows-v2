"""Build Map_TibnorS4_HammelinnaTilkkuHub_PurchaseOrder_ORDERS02.

Run:  py -I mappings/10_ORDERS_Tibnor-to-HameenlinnaTilkku/build_mapping.py
Spec 1002249_ORDERS_Tibnor-to-HameenlinnaTilkku_MappingSpec_v0.1.xlsx has the same rules as the Raahe Tilkku spec,
except that Property ZMA is not sent (OP-02). The logic is build() in
mappings/6_ORDERS_Tibnor-to-RaaheTilkku/build_mapping.py; only the VM-01 values of this mill differ.
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "orders_tilkku", HERE.parent / "6_ORDERS_Tibnor-to-RaaheTilkku" / "build_mapping.py")
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)

MILL = dict(
    name="Map_TibnorS4_HammelinnaTilkkuHub_PurchaseOrder_ORDERS02",
    vendor="0000086245",                 # E1EDKA1[LF]-PARTN of Hämeenlinna Tilkku (VM-01 key)
    gln="00372389445751",                # VM-01 -> Header/InterchangeRecipient
    routing_out="HAMF.M.TILKKU",         # VM-01 -> Header/MessageRoutingOutbound (+ environment suffix)
    send_zma=False,                      # #44 Property ZMA: not for Hämeenlinna Tilkku (OP-02)
)

if __name__ == "__main__":
    sys.exit(core.run(MILL, HERE))
