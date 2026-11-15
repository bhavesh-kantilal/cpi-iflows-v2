<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:ns1="urn:sap-com:document:sap:rfc:functions"
    exclude-result-prefixes="ns1">

    <xsl:output method="xml" indent="yes"/>
	
    <!-- Read the percentage map from property (e.g., "|X4=0.20|") -->
    <xsl:param name="taxPercentageMap"/>
    <!--<xsl:variable name="taxPercentageMap" select="$exchange/getProperty('taxPercentageMap')"/>-->

    <!-- Key to find TAXDATA items by Tax Code (needed for GL lookup) -->
    <xsl:key name="kTaxData" match="//TAXDATA/item" use="TAX_CODE"/>

    <!-- Helper function to get percentage for a tax code -->
    <xsl:function name="ns1:getPercentage">
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

    <!-- 
       TEMPLATE 1: Update TAX_BASE_AMOUNT in TAXDATA 
    -->
    <xsl:template match="TAXDATA/item/TAX_BASE_AMOUNT">
        <xsl:variable name="currentTaxCode" select="../TAX_CODE"/>
        <xsl:variable name="currentTaxAmount" select="../TAX_AMOUNT"/>
        <xsl:variable name="percentage" select="ns1:getPercentage($taxPercentageMap, $currentTaxCode)"/>

        <xsl:choose>
            <!-- Check if we have a percentage and a valid tax amount -->
            <xsl:when test="string-length($percentage) > 0 and number($percentage) != 0">
                <TAX_BASE_AMOUNT>
                    <!-- Formula: TaxAmount / Percentage -->
                    <xsl:value-of select="format-number($currentTaxAmount div $percentage, '0.##')"/>
                </TAX_BASE_AMOUNT>
            </xsl:when>
            <xsl:otherwise>
                <!-- Keep original if no rule applies -->
                <xsl:copy-of select="."/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <!-- 
       TEMPLATE 2: Add TAX_BASE_AMOUNT to GLACCOUNTDATA 
    -->
    <xsl:template match="GLACCOUNTDATA/item">
        <xsl:copy>
            <!-- Copy all existing children first -->
            <xsl:apply-templates select="@* | node()"/>
            
            <!-- Check if we need to append the calculated field -->
            <xsl:variable name="currentTaxCode" select="TAX_CODE"/>
            <xsl:variable name="percentage" select="ns1:getPercentage($taxPercentageMap, $currentTaxCode)"/>
            
            <xsl:if test="string-length($percentage) > 0 and number($percentage) != 0">
                <!-- 
                   Find the corresponding Tax Amount from TAXDATA using the key.
                -->
                <xsl:variable name="taxAmount" select="key('kTaxData', $currentTaxCode)/TAX_AMOUNT"/>
                
                <TAX_BASE_AMOUNT>
                    <xsl:value-of select="format-number($taxAmount div $percentage, '0.##')"/>
                </TAX_BASE_AMOUNT>
            </xsl:if>
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>