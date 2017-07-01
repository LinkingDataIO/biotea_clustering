from flask import Flask, request, jsonify
from docs import conf
import biotea_clustering as bioteac
import scipy.cluster.hierarchy as hcluster
from flask_cors import CORS


app = Flask(__name__)

CORS(app)


@app.route("/cluster")
def get_clusters():
    ontology = request.args.get('ontology')
    ontology = conf.ONTOLOGIES_INDEX[ontology]
    concept_uri = request.args.get('concept')

    annotations_dataset = bioteac.get_dataset_annotations(concept_uri, ontology)
    dataset = bioteac.get_feature_matrix(annotations_dataset)
    tree = {}
    if dataset['observations']:
        clusters = hcluster.linkage(dataset['observations'], metric="cosine", method="complete")
        tree = bioteac.create_tree(dataset['index'], clusters)
        h_flat_cluster = hcluster.fcluster(clusters, 0.66)
    flat_cluster = {}
    for i, cluster in enumerate(h_flat_cluster.tolist()):
        document_uri = "http://linkingdata.io/pmcdoc/pmc/" + dataset['index'][i]['id']
        document = annotations_dataset['documents'][document_uri]
        if cluster not in flat_cluster:
            flat_cluster[cluster] = {}
            flat_cluster[cluster]['articles'] = set()
            flat_cluster[cluster]['annotations'] = document['annotations'].keys()
        flat_cluster[cluster]['articles'].add(dataset['index'][i]['id'])
        flat_cluster[cluster]['annotations'] &= document['annotations'].keys()
    for cluster in flat_cluster:
        flat_cluster[cluster]['articles'] = list(flat_cluster[cluster]['articles'])
        flat_cluster[cluster]['annotations'] = list(flat_cluster[cluster]['annotations'])
        for i, annotation in enumerate(flat_cluster[cluster]['annotations']):
            term_uri = flat_cluster[cluster]['annotations'][i]
            flat_cluster[cluster]['annotations'][i] = dict(uri=term_uri,
                                                           label=annotations_dataset['annotations_index'][term_uri])
    result = dict(tree=tree, flat=flat_cluster)
    return jsonify(result)


@app.route("/targetstats")
def get_stats():
    ontology = request.args.get('ontology')
    ontology = conf.ONTOLOGIES_INDEX[ontology]
    concept_uri = request.args.get('concept')
    stats = bioteac.get_dataset_stats(concept_uri, ontology)
    return jsonify(stats)


@app.route("/dashboard")
def get_dashboard():
    ontology = request.args.get('ontology')
    ontology = conf.ONTOLOGIES_INDEX[ontology]
    concept_uri = request.args.get('concept')
    stats = bioteac.get_articles_data(concept_uri, ontology)
    return jsonify(stats)


