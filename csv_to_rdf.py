import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD

# Read the CSV file
df = pd.read_csv("synesteticDataset.csv")

# Initialize the Graph
g = Graph()

# Add the Namespace of the Ontology URI
NS = Namespace("http://www.semanticweb.org/digitalhumanities/ontologies/synsonto1#")
# Tell your RDF graph to associate a short prefix string with a full namespace URI
g.bind("", NS)
g.bind("owl", OWL)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

# Take the elements of the CSV file by rows
for index, row in df.iterrows():
    work_id = str(row.get("Work", "")).strip()
    work_type = str(row.get("Work_Type", "")).strip()
    component_id = str(row.get("WorkComponent", "")).strip()
    source_mod = str(row.get("SourceModality", "")).strip()
    target_mod = str(row.get("TargetModality", "")).strip()
    evoked_val = str(row.get("EvokedValue", "")).strip()
    corr_type = str(row.get("CorrespondenceType", "")).strip()
    # Fixed the typo here: reading "SynesthethicTheory" as it is spelled in the CSV
    theory_id = str(row.get("SynesthethicTheory", "")).strip()

    if not work_id or not component_id:
        continue
    
    # Create a URI for each element type
    work_uri = URIRef(NS + work_id)
    component_uri = URIRef(NS + component_id)
    source_mod_uri = URIRef(NS + source_mod)
    target_mod_uri = URIRef(NS + target_mod)
    evoked_val_uri = URIRef(NS + evoked_val)
    theory_uri = URIRef(NS + theory_id)
    corr_type_uri = URIRef(NS + corr_type)

    # Add the triples for works and components to the Graph
    g.add((work_uri, RDF.type, URIRef(NS + work_type)))
    g.add((work_uri, NS.hasComponent, component_uri))
    g.add((component_uri, RDF.type, NS.WorkComponent))
    g.add((component_uri, NS.hasSourceModality, source_mod_uri))
    g.add((component_uri, NS.definedBy, theory_uri))
    g.add((component_uri, NS.evokesValue, evoked_val_uri))

    # Check if there is a value in this column, if there is something, transform it into a string and create a triple
    if pd.notna(row["hasPhysicalOrTextualValue"]):
        val = str(row["hasPhysicalOrTextualValue"]).strip()
        g.add((component_uri, NS.hasPhysicalOrTextualValue, Literal(val, datatype=XSD.string)))

    if pd.notna(row["hasPitch"]):
        pitch = str(row["hasPitch"]).strip()
        g.add((component_uri, NS.hasPitch, Literal(pitch, datatype=XSD.string)))

    g.add((source_mod_uri, RDF.type, NS.SensoryModality))
    g.add((target_mod_uri, RDF.type, NS.SensoryModality))
    
    g.add((evoked_val_uri, RDF.type, NS.EvokedValue))
    g.add((evoked_val_uri, NS.hasTargetModality, target_mod_uri))

    g.add((theory_uri, RDF.type, NS.SynestheticTheory))
    g.add((theory_uri, NS.hasCorrespondenceType, corr_type_uri))

    if pd.notna(row["BibliographicSource"]):
        bib = str(row["BibliographicSource"]).strip()
        g.add((theory_uri, NS.hasBibliographicSource, Literal(bib, datatype=XSD.string)))

    g.add((corr_type_uri, RDF.type, NS.CorrespondenceType))

# Serialize the output into a brand new file and print "Success!" if everything have gone well
output_file = "populated_synsonto.ttl"
g.serialize(destination=output_file, format = "turtle")

print(f"Success!")