<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes"/>

    <!-- GLOBAL VARIABLES -->

    <!-- Find the maximum level value from all master data nodes -->
    <xsl:variable name="maxLevel" select="max(//E1BP2054_MASTERDATA_ALE/LEVEL)"/>

    <!-- Extract the ZZOWNER value by finding the correct E1BPPAREX segment -->
    <xsl:variable name="owner" select="normalize-space(substring-after(//E1BPPAREX[contains(VALUEPART1, 'ZZOWNER')]/VALUEPART1, 'ZZOWNER'))"/>

    <!-- Get the main project definition ID from the header -->
    <xsl:variable name="projectDefinitionID" select="/PROJECT02/IDOC/E1BP2054_PROJDEFINITION/PROJECT_DEFINITION"/>

    <!-- 
      Check if an OBJECTSTATUS node exists for the main project that has both STATUS = 'I0046' and INACTIVE = 'X'.
      This variable will hold a node if the condition is met, making it 'true' in a boolean context.
    -->
<xsl:variable name="isProjectInactive"
                  select="//E1BP2054_OBJECTSTATUS_ALE[WBS_OBJECTID = $projectDefinitionID and STATUS = 'I0046' and (INACTIVE = 'X' or not(INACTIVE))]"/>

    <!-- TEMPLATES -->

    <!-- Root template to begin the transformation -->
    <xsl:template match="/PROJECT02">
        <PROJECT02>
            <xsl:apply-templates select="IDOC"/>
        </PROJECT02>
    </xsl:template>

    <!-- Main template that selectively builds the new IDOC structure -->
    <xsl:template match="IDOC">
        <IDOC>
            <!-- 1. Add the new ACTIVE element based on the project status check -->
            <ACTIVE>
                <xsl:choose>
                    <!-- If the 'isProjectInactive' variable found a node, the project is inactive -->
                    <xsl:when test="$isProjectInactive">
                        <xsl:value-of select="'false'"/>
                    </xsl:when>
                    <!-- Otherwise, the project is considered active -->
                    <xsl:otherwise>
                        <xsl:value-of select="'true'"/>
                    </xsl:otherwise>
                </xsl:choose>
            </ACTIVE>
            
            <!-- 2. Add the ExtractedOwner element if a value was found -->
            <xsl:if test="$owner != ''">
                <ZZOWNER>
                    <xsl:value-of select="$owner"/>
                </ZZOWNER>
            </xsl:if>
            
            <!-- 3. Copy the main header segments -->
            <xsl:copy-of select="EDI_DC40"/>
            <xsl:copy-of select="E1BP2054_PROJDEFINITION"/>

            <!-- 4. Copy only the MASTERDATA nodes that are at the highest level -->
            <xsl:copy-of select="E1BP2054_MASTERDATA_ALE[LEVEL = $maxLevel]"/>

        </IDOC>
    </xsl:template>

</xsl:stylesheet>

