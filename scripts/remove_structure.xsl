<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">

    <xsl:output method="xml"/>

    <xsl:template match="/">
        <xsl:for-each
            select="collection('/home/mgl/Bureau/Travail/projets/alignement/alignement_global_unilingue/data/Target?select=*.xml')">
            <xsl:message>Found you <xsl:value-of select="tei:TEI/@xml:id"/></xsl:message>
            <xsl:variable name="output_path">
                <xsl:value-of select="tei:TEI/@xml:id"/>
                <xsl:text>.xml</xsl:text>
            </xsl:variable>
            <xsl:result-document
                href="/home/mgl/Bureau/Travail/projets/alignement/alignement_global_unilingue/data/transform/{$output_path}">
                <xsl:apply-templates/>
            </xsl:result-document>
        </xsl:for-each>
    </xsl:template>


    <xsl:template match="node() | @*">
        <xsl:copy>
            <xsl:apply-templates select="node() | @*"/>
        </xsl:copy>
    </xsl:template>


    <xsl:template
        match="tei:facsimile | tei:head[parent::tei:div[@type = 'partie']] | tei:div[@type = 'partie']/descendant::node()[not(self::tei:w or self::tei:pc or self::tei:div or self::tei:head or self::tei:p or self::text())]"/>

    <xsl:template
        match="tei:head | tei:div[@type = 'chapitre'] | tei:div[@type = 'glose'] | tei:div[@type = 'traduction'] | tei:p">
        <xsl:apply-templates/>
    </xsl:template>




</xsl:stylesheet>
