<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">

    <xsl:output method="xml"/>


    <xsl:template match="node() | @*">
        <xsl:copy>
            <xsl:apply-templates select="node() | @*"/>
        </xsl:copy>
    </xsl:template>


    <xsl:template match="tei:facsimile | tei:teiHeader | comment()"/>
    
    <xsl:template match="tei:head | tei:div[@type='chapitre'] | tei:div[@type = 'glose'] | tei:div[@type = 'traduction'] | tei:p">
        <xsl:apply-templates/>
    </xsl:template>




</xsl:stylesheet>
