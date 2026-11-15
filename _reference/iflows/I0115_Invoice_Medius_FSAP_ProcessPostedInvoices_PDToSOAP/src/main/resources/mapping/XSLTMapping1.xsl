<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:ns104="http://sap.com/xi/SAPSCORE/SFIN"
    exclude-result-prefixes="ns104">

    <xsl:output method="xml" indent="yes"/>

    <!-- Identity transform -->
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <!-- Override ProductTaxItem -->
    <xsl:template match="ProductTaxItem">
        <xsl:variable name="taxCode" select="TaxCode"/>

        <!-- Position of this TaxCode among previous ProductTaxItem nodes -->
        <xsl:variable name="index"
            select="count(preceding-sibling::ProductTaxItem[TaxCode = $taxCode]) + 1"/>

        <!-- Split classification -->
        <xsl:variable name="parts"
            select="tokenize(TaxItemClassification, '_')"/>

        <xsl:copy>
            <xsl:copy-of select="TaxCode"/>

            <!-- Replace TaxItemClassification -->
            <TaxItemClassification>
                <xsl:value-of select="$parts[$index]"/>
            </TaxItemClassification>

            <xsl:copy-of select="AmountInTransactionCurrency"/>
            <xsl:copy-of select="TaxBaseAmountInTransCrcy"/>
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>
