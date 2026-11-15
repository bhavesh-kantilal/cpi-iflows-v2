<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:ns0="urn:sap-com:document:sap:rfc:functions"
    exclude-result-prefixes="ns0">

    <xsl:output method="xml" indent="yes"/>
	
	<xsl:param name="taxLogicMap"/>

    <!-- Index ACCOUNTTAX items by ITEMNO_ACC for fast lookup -->
    <xsl:key name="kTaxItem" match="/ns0:BAPI_ACC_DOCUMENT_POST/ACCOUNTTAX/item" use="ITEMNO_ACC"/>

    <!-- Helper function to get logic type for a specific tax code -->
    <xsl:function name="ns0:getLogicType">
        <xsl:param name="mapStr"/>
        <xsl:param name="taxCode"/>
        <xsl:variable name="searchKey" select="concat('|', $taxCode, '=')"/>
        <xsl:if test="contains($mapStr, $searchKey)">
            <xsl:value-of select="substring-before(substring-after($mapStr, $searchKey), '|')"/>
        </xsl:if>
    </xsl:function>

    <!-- Identity Template: Copy everything exactly as is by default -->
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <!-- Specific Template: Only target AMT_BASE inside CURRENCYAMOUNT items -->
    <xsl:template match="CURRENCYAMOUNT/item/AMT_BASE">
        <!-- 1. Find the Item Number of the current line -->
        <xsl:variable name="itemNo" select="../ITEMNO_ACC"/>      
        <!-- 2. Look up the corresponding Tax info using the key -->
        <xsl:variable name="acctKey" select="key('kTaxItem', $itemNo)/ACCT_KEY"/>
        <!-- Find the tax code for THIS specific item -->
        <xsl:variable name="currentTaxCode" select="key('kTaxItem', $itemNo)/TAX_CODE"/>
		<!-- Check the logic type for THIS specific tax code -->
        <xsl:variable name="logicType" select="ns0:getLogicType($taxLogicMap, $currentTaxCode)"/>
        <xsl:choose>
            <!-- 3. Condition: Is the Account Key 'ESE' or VST? -->
            <xsl:when test="$logicType = 'ReverseCharge_TaxBaseAmount' and ($acctKey = 'ESE' or $acctKey = 'VST')">
                <!-- Yes: Set AMT_BASE to the value of sibling AMT_DOCCUR -->
                <AMT_BASE>
                    <xsl:value-of select="../AMT_DOCCUR"/>
                </AMT_BASE>
            </xsl:when>
            <xsl:otherwise>
                <!-- No: Keep the original value -->
                <xsl:copy-of select="."/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>