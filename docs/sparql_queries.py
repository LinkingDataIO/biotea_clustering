GET_ANNOTATIONS_QUERY = """
PREFIX oa: <http://www.w3.org/ns/oa#>
PREFIX biotea: <https://biotea.github.io/biotea-ontololgy#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?articleUri ?termUri ?termFrequency ?termLabel ?articleTitle
{{
    SELECT DISTINCT ?articleUri ?termUri ?termFrequency ?termLabel ?articleTitle
    {{
        ?annotation a oa:Annotation .
        ?annotation oa:hasTarget ?paragraph .
        ?annotation oa:hasBody ?termUri .
        ?annotation oa:hasBody ?textualBody .
        ?annotation biotea:tf ?termFrequency .
        ?textualBody a oa:TextualBody ;
                    rdf:value ?termLabel .
        ?paragraph oa:hasSource ?articleUri .
        FILTER (STRSTARTS(STR(?termUri), "{ontology_uri}"))
        {{
            SELECT DISTINCT ?articleUri ?articleTitle
            {{
                ?annot a oa:Annotation ;
                  oa:hasTarget ?paragraph ;
                  oa:hasBody <{term_uri}> .
                ?paragraph oa:hasSource ?articleUri .
                ?articleUri dcterms:title ?articleTitle .
            }}
        }}
    }} ORDER BY ?termUri ?termFrequency 
}} LIMIT {limit} OFFSET {offset}
"""

STATS_COUNT_QUERY = """
PREFIX oa: <http://www.w3.org/ns/oa#>
PREFIX biotea: <https://biotea.github.io/biotea-ontololgy#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT (COUNT(DISTINCT(?articleUri)) as ?articleCount)  (COUNT(DISTINCT(?annotation))  as ?annotationCount)
{{
    SELECT DISTINCT ?articleUri ?annotation ?termFrequency ?articleTitle
    {{
        ?annotation a oa:Annotation .
        ?annotation oa:hasTarget ?paragraph .
        ?annotation oa:hasBody ?termUri .
        ?annotation biotea:tf ?termFrequency .
        ?paragraph oa:hasSource ?articleUri .
        FILTER (STRSTARTS(STR(?termUri), "{ontology_uri}"))
        {{
            SELECT DISTINCT ?articleUri ?articleTitle
            {{
                ?annot a oa:Annotation ;
                  oa:hasTarget ?paragraph ;
                  oa:hasBody <{term_uri}> .
                ?paragraph oa:hasSource ?articleUri .
                ?articleUri dcterms:title ?articleTitle .
            }}
        }}
    }}
}}
"""

ARTICLES_BY_YEAR = """
PREFIX oa: <http://www.w3.org/ns/oa#>
PREFIX biotea: <https://biotea.github.io/biotea-ontololgy#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX bibo: <http://purl.org/ontology/bibo/>


SELECT ?year (COUNT(DISTINCT(?articleUri))  as ?articlesByYear)
{{
    SELECT DISTINCT ?articleUri ?annotation ?termFrequency ?articleTitle ?year
    {{
        ?annotation a oa:Annotation .
        ?annotation oa:hasTarget ?paragraph .
        ?annotation oa:hasBody ?termUri .
        ?annotation biotea:tf ?termFrequency .
        ?paragraph oa:hasSource ?articleUri .
        ?articleUri dcterms:issued ?year .
        FILTER (STRSTARTS(STR(?termUri), "{ontology_uri}"))
        {{
            SELECT DISTINCT ?articleUri ?articleTitle
            {{
                ?annot a oa:Annotation ;
                  oa:hasTarget ?paragraph ;
                  oa:hasBody <{term_uri}> .
                ?paragraph oa:hasSource ?articleUri .
                ?articleUri dcterms:title ?articleTitle .
            }}
        }}
    }}
}} GROUP BY ?year ORDER BY ?year
"""


ARTICLES_BY_JOURNAL = """
PREFIX oa: <http://www.w3.org/ns/oa#>
PREFIX biotea: <https://biotea.github.io/biotea-ontololgy#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX bibo: <http://purl.org/ontology/bibo/>


SELECT ?journalTitle (COUNT(DISTINCT(?articleUri))as ?articlesByJournal)
{{
    SELECT DISTINCT ?articleUri ?annotation ?termFrequency ?articleTitle ?journalTitle
    {{
        ?annotation a oa:Annotation .
        ?annotation oa:hasTarget ?paragraph .
        ?annotation oa:hasBody ?termUri .
        ?annotation biotea:tf ?termFrequency .
        ?paragraph oa:hasSource ?articleUri .
        ?articleUri dcterms:isPartOf ?issue .
        ?issue dcterms:isPartOf ?journal .
        ?journal a <http://purl.org/ontology/bibo/Journal>.
        ?journal dcterms:title ?journalTitle .
        FILTER (STRSTARTS(STR(?termUri), "{ontology_uri}"))
        {{
            SELECT DISTINCT ?articleUri ?articleTitle
            {{
                ?annot a oa:Annotation ;
                  oa:hasTarget ?paragraph ;
                  oa:hasBody <{term_uri}> .
                ?paragraph oa:hasSource ?articleUri .
                ?articleUri dcterms:title ?articleTitle .
            }}
        }}
    }}
}} GROUP BY ?journalTitle

"""