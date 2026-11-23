<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:ns0="urn:sap-com:document:sap:rfc:functions"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="ns0 xs">

    <xsl:output method="xml" indent="yes"/>

    <!-- 
    ================================================================================
     XSLT Stylesheet for Reversing Tax Signs
    ================================================================================
     Assumption: This XSLT is executed ONLY if the routing conditions are met.
     
     Logic:
     1. For EACH item (amount or account key), check if its specific TAX_CODE 
        has the 'ReverseCharge_PartiallyDeductible' flag in the taxLogicMap.
     2. If yes, reverse the sign / swap the key.
     3. If no, leave it alone (even if the document is a credit memo).
    ================================================================================
    -->

    <xsl:param name="taxLogicMap"/>
    
    <!-- Keys for fast lookups -->
    <xsl:key name="kTaxItem" match="/ns0:BAPI_ACC_DOCUMENT_POST/ACCOUNTTAX/item" use="ITEMNO_ACC"/>
    <xsl:key name="kTaxItemByCode" match="/ns0:BAPI_ACC_DOCUMENT_POST/ACCOUNTTAX/item" use="TAX_CODE"/>

    <!-- Helper function to get logic type for a specific tax code -->
    <xsl:function name="ns0:getLogicType">
        <xsl:param name="mapStr"/>
        <xsl:param name="taxCode"/>
        <xsl:variable name="searchKey" select="concat('|', $taxCode, '=')"/>
        <xsl:if test="contains($mapStr, $searchKey)">
            <xsl:value-of select="substring-before(substring-after($mapStr, $searchKey), '|')"/>
        </xsl:if>
    </xsl:function>

    <!-- Identity Template: Copy everything by default -->
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <!-- Override Template: Match AMT_DOCCUR -->
    <xsl:template match="CURRENCYAMOUNT/item/AMT_DOCCUR">
        <xsl:variable name="currentItemNo" select="../ITEMNO_ACC"/>
        <!-- Find the tax code for THIS specific item -->
        <xsl:variable name="currentTaxCode" select="key('kTaxItem', $currentItemNo)/TAX_CODE"/>
        <!-- Check the logic type for THIS specific tax code -->
        <xsl:variable name="logicType" select="ns0:getLogicType($taxLogicMap, $currentTaxCode)"/>

        <xsl:choose>
            <!-- Only modify if this specific item's tax code requires it -->
            <xsl:when test="$logicType = 'ReverseCharge_PartiallyDeductible'">
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
        <!-- Check the logic type for THIS specific tax code -->
        <xsl:variable name="logicType" select="ns0:getLogicType($taxLogicMap, $currentTaxCode)"/>

        <xsl:choose>
            <!-- Only modify if this specific item's tax code requires it -->
            <xsl:when test="$logicType = 'ReverseCharge_PartiallyDeductible'">
                <ACCT_KEY>
                    <!-- Generic Swap Logic: Find partner with same Tax Code but different Item No -->
                    <xsl:variable name="partnerKey" select="key('kTaxItemByCode', $currentTaxCode)[ITEMNO_ACC != $currentItemNo]/ACCT_KEY"/>
                    
                    <xsl:choose>
                        <xsl:when test="$partnerKey">
                            <xsl:value-of select="$partnerKey[1]"/>
                        </xsl:when>
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