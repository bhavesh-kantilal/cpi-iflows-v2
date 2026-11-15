<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes"/>

    <xsl:template match="/root">
        <root>
            <xsl:copy-of select="invoice[not(taxLines)]"/>
            <xsl:for-each select="invoice">
                <invoice>
                    <xsl:copy-of select="*[not(self::taxLines)]"/>
                    <xsl:for-each select="taxLines">
                        <xsl:sort select="taxCode" order="ascending"/>
                        <xsl:sort select="number(percentage)" order="ascending"/>
                        <xsl:copy-of select="."/>
                    </xsl:for-each>
                </invoice>
            </xsl:for-each>
        </root>
    </xsl:template>
</xsl:stylesheet>
