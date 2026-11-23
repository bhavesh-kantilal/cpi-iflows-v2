<xsl:stylesheet version="3.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:ns1="urn:sap-com:document:sap:rfc:functions"
    exclude-result-prefixes="xsl">

  <xsl:output method="xml" indent="yes"/>

  <!-- Identity template: copies everything by default -->
  <xsl:mode on-no-match="shallow-copy"/>

  <!-- Special handling for ITEMDATA -->
  <xsl:template match="ns1:BAPI_INCOMINGINVOICE_CREATE1/ITEMDATA">
    <ITEMDATA>
      <xsl:for-each-group 
          select="item"
          group-by="concat(
                      string(PO_NUMBER),'|',
                      string(PO_ITEM),'|',
                      string(REF_DOC),'|',
                      string(REF_DOC_YEAR),'|',
                      string(REF_DOC_IT),'|',
                      string(TAX_CODE),'|',
                      string(COND_TYPE)
                    )">
        <item>
          <!-- Copy fields from first item, but sum ITEM_AMOUNT + QUANTITY -->
          <xsl:for-each select="current-group()[1]/*">
            <xsl:choose>
              <xsl:when test="local-name() = 'ITEM_AMOUNT'">
                <ITEM_AMOUNT>
                  <xsl:value-of select="format-number(sum(current-group()/ITEM_AMOUNT), '0.0000')"/>
                </ITEM_AMOUNT>
              </xsl:when>
              <xsl:when test="local-name() = 'QUANTITY'">
                <QUANTITY>
                  <xsl:value-of select="format-number(sum(current-group()/QUANTITY), '0.0000')"/>
                </QUANTITY>
              </xsl:when>
              <!-- Copy all other fields unchanged -->
              <xsl:otherwise>
                <xsl:copy-of select="."/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:for-each>
        </item>
      </xsl:for-each-group>
    </ITEMDATA>
  </xsl:template>

</xsl:stylesheet>
