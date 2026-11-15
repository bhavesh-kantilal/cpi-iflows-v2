<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" exclude-result-prefixes="xsi">
	<!-- Identity Transform: Copies everything as-is -->
	<xsl:mode on-no-match="shallow-copy"/>
	<!-- Remove elements where xsi:nil = true -->
	<xsl:template match="*[@xsi:nil = 'true']"/>
</xsl:stylesheet>