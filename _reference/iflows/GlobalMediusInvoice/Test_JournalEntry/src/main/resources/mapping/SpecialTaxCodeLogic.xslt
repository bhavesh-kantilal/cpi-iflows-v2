<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:ns0="urn:sap-com:document:sap:rfc:functions"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="ns0 xs">

    <xsl:output method="xml" indent="yes"/>

    <xsl:param name="taxLogicMap"/>
    <!--<xsl:variable name="taxLogicMap" select="$exchange/getProperty('taxLogicMap')"/>-->

    <xsl:key name="kVendorCurrency" match="/ns0:BAPI_ACC_DOCUMENT_POST/CURRENCYAMOUNT/item" use="ITEMNO_ACC"/>
    <xsl:key name="kTaxItem" match="/ns0:BAPI_ACC_DOCUMENT_POST/ACCOUNTTAX/item" use="ITEMNO_ACC"/>
    <!-- New Key: Group tax items by Tax Code to find partners easily -->
    <xsl:key name="kTaxItemByCode" match="/ns0:BAPI_ACC_DOCUMENT_POST/ACCOUNTTAX/item" use="TAX_CODE"/>

    <xsl:variable name="vVendorItemNo" select="/ns0:BAPI_ACC_DOCUMENT_POST/ACCOUNTPAYABLE/item/ITEMNO_ACC"/>
    <xsl:variable name="vVendorAmount" select="key('kVendorCurrency', $vVendorItemNo)/AMT_DOCCUR"/>
    <xsl:variable name="isCreditMemo" select="number($vVendorAmount) > 0"/>
    
    <!-- Helper function -->
    <xsl:function name="ns0:getLogicType">
        <xsl:param name="mapStr"/>
        <xsl:param name="taxCode"/>
        <xsl:variable name="searchKey" select="concat('|', $taxCode, '=')"/>
        <xsl:if test="contains($mapStr, $searchKey)">
            <xsl:value-of select="substring-before(substring-after($mapStr, $searchKey), '|')"/>
        </xsl:if>
    </xsl:function>

    <!-- Identity Template -->
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <!-- Override Template: Match AMT_DOCCUR -->
    <xsl:template match="CURRENCYAMOUNT/item/AMT_DOCCUR">
        <xsl:variable name="currentItemNo" select="../ITEMNO_ACC"/>
        <xsl:variable name="currentTaxCode" select="key('kTaxItem', $currentItemNo)/TAX_CODE"/>
        <xsl:variable name="logicType" select="ns0:getLogicType($taxLogicMap, $currentTaxCode)"/>

        <xsl:choose>
            <xsl:when test="$isCreditMemo and $logicType = 'ReverseCharge_PartiallyDeductible'">
                <AMT_DOCCUR>
                    <xsl:value-of select=". * -1"/>
                </AMT_DOCCUR>
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy-of select="."/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <!-- Override Template: Match ACCT_KEY -->
    <xsl:template match="ACCOUNTTAX/item/ACCT_KEY">
        <xsl:variable name="currentItemNo" select="../ITEMNO_ACC"/>
        <xsl:variable name="currentTaxCode" select="../TAX_CODE"/>
        <xsl:variable name="logicType" select="ns0:getLogicType($taxLogicMap, $currentTaxCode)"/>

        <xsl:choose>
            <xsl:when test="$isCreditMemo and $logicType = 'ReverseCharge_PartiallyDeductible'">
                <ACCT_KEY>
                    <!-- 
                       Generic Swap Logic: 
                       Find another item with the same Tax Code but different Item Number.
                       Use its Account Key.
                    -->
                    <xsl:variable name="partnerKey" select="key('kTaxItemByCode', $currentTaxCode)[ITEMNO_ACC != $currentItemNo]/ACCT_KEY"/>
                    
                    <xsl:choose>
                        <!-- If a partner was found, use their key -->
                        <xsl:when test="$partnerKey">
                            <xsl:value-of select="$partnerKey[1]"/>
                        </xsl:when>
                        <!-- If no partner found (e.g. single line), keep original -->
                        <xsl:otherwise>
                            <xsl:value-of select="."/>
                        </xsl:otherwise>
                    </xsl:choose>
                </ACCT_KEY>
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy-of select="."/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>