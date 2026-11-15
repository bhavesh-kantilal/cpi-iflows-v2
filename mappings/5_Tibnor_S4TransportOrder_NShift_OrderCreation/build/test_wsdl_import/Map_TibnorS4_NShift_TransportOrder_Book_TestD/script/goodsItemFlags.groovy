import com.sap.it.api.mapping.*

/*
 * Which freight order items become an NShift GoodsItem (goods row), and which package id (SSCC) do they carry?
 *
 * S/4 TM sends an item hierarchy: vehicle resource (AVR) -> packages (PKG) -> nested packages (PKG) -> products (PRD).
 * A goods row is a handling unit as the carrier sees it: an item of category PKG or PRD whose parent is NOT a
 * PKG or PRD item (usually its parent is the AVR item, or it has no parent).
 * Nested packages and the products inside a package are not goods rows of their own.
 *
 * Inputs, all in ONE context (flattened in the mapping with removeContexts):
 *   itemId[]   Item/ID, one per Item
 *   category[] Item/CategoryCode, one per Item
 *   childId[]  Item/ID repeated for each HierarchyRelationship (only items that have a parent)
 *   parentId[] HierarchyRelationship/ParentItemID, aligned with childId[]
 *   pkgItem[]  Item/ID repeated for each Package (only items that have a Package)
 *   pkgId[]    Package/ID, aligned with pkgItem[]
 * Outputs, one value per Item, in item order:
 *   0 flag       'true' / 'false'
 *   1 packageId  the item's Package/ID, '' when it has none
 */
def void goodsItemFlags(String[] itemId, String[] category, String[] childId, String[] parentId,
                        String[] pkgItem, String[] pkgId, Output flag, Output packageId, MappingContext context) {
    if (itemId.length != category.length || childId.length != parentId.length || pkgItem.length != pkgId.length) {
        throw new RuntimeException("goodsItemFlags: inputs out of step (itemId " + itemId.length + ", category "
                + category.length + ", childId " + childId.length + ", parentId " + parentId.length
                + ", pkgItem " + pkgItem.length + ", pkgId " + pkgId.length + ")")
    }
    Map<String, String> categoryOf = [:]
    for (int i = 0; i < itemId.length; i++) {
        categoryOf[itemId[i]] = category[i]
    }
    Map<String, String> parentOf = [:]
    for (int i = 0; i < childId.length; i++) {
        parentOf[childId[i]] = parentId[i]
    }
    Map<String, String> packageOf = [:]
    for (int i = 0; i < pkgItem.length; i++) {
        if (!packageOf.containsKey(pkgItem[i])) {
            packageOf[pkgItem[i]] = pkgId[i]
        }
    }
    Set goods = ["PKG", "PRD"] as Set
    for (int i = 0; i < itemId.length; i++) {
        String parentCategory = categoryOf[parentOf[itemId[i]]]
        boolean isGoodsRow = goods.contains(category[i]) && !goods.contains(parentCategory)
        flag.addValue(String.valueOf(isGoodsRow))
        packageId.addValue(packageOf[itemId[i]] ?: "")
    }
}
