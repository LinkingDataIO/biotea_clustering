from SPARQLWrapper import SPARQLWrapper, JSON
from docs import conf
from docs import sparql_queries as sparqlt
import math
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as hcluster
import json
import mpld3


def get_feature_matrix(dataset):
    observations = []
    article_index = []
    total_documents = len(dataset['documents'])
    for article_uri, document in dataset['documents'].items():
        label = document['metadata']['uri'].replace("http://linkingdata.io/pmcdoc/pmc/", "")
        article_index.append(dict(id=label, title=document['metadata']['title']))
        feature_vector = []
        for term, document_frequency in dataset['terms_document_frequency'].items():
            if term in document['annotations']:
                idf = math.log(total_documents/document_frequency)
                max_tf = max(document['annotations'], key=document['annotations'].get)
                max_tf = document['annotations'][max_tf]
                tf = 0.5 + (0.5 * document['annotations'][term]/max_tf)
                feature_vector.append(tf * idf)
            else:
                feature_vector.append(0.0)
        observations.append(feature_vector)
    return dict(index=article_index, observations=observations)


def get_dataset_stats(filter_term_uri, ontology_uri):
    query = sparqlt.STATS_COUNT_QUERY.format(term_uri=filter_term_uri, ontology_uri=ontology_uri)
    results = query_endpoint(query)
    articles_count = results[0]['articleCount']['value']
    annotations_count = results[0]['annotationCount']['value']
    return dict(articles=articles_count, annotations=annotations_count)


def get_articles_data(filter_term_uri, ontology_uri):
    articles_data = {}
    query = sparqlt.ARTICLES_BY_YEAR.format(term_uri=filter_term_uri, ontology_uri=ontology_uri)
    results = query_endpoint(query)
    labels = []
    values = []
    for result in results:
        labels.append(result['year']['value'])
        values.append(result['articlesByYear']['value'])
    articles_data['year'] = dict(labels=labels, values=values)

    query = sparqlt.ARTICLES_BY_JOURNAL.format(term_uri=filter_term_uri, ontology_uri=ontology_uri)
    results = query_endpoint(query)
    labels = []
    values = []
    for result in results:
        labels.append(result['journalTitle']['value'])
        values.append(result['articlesByJournal']['value'])
    articles_data['journal'] = dict(labels=labels, values=values)
    return articles_data


def get_dataset_annotations(filter_term_uri, ontology_uri):
    documents = {}
    terms_document_frequency = {}
    annotations_index = {}
    limit = 1000
    offset = 0

    query = sparqlt.GET_ANNOTATIONS_QUERY.format(term_uri=filter_term_uri,
                                                 ontology_uri=ontology_uri,
                                                 limit=limit,
                                                 offset=offset)
    results = query_endpoint(query)
    while results:
        for result in results:
            article_uri = result['articleUri']['value']
            article_title = result['articleTitle']['value']
            term_uri = result['termUri']['value']
            term_freq = float(result['termFrequency']['value'])
            if article_uri not in documents:
                documents[article_uri] = {}
                documents[article_uri]['annotations'] = {}
                documents[article_uri]['metadata'] = dict(uri=article_uri, title=article_title)
            documents[article_uri]['annotations'][term_uri] = term_freq
            if term_uri not in terms_document_frequency:
                terms_document_frequency[term_uri] = 1
                annotations_index[term_uri] = result['termLabel']['value']
            else:
                terms_document_frequency[term_uri] += 1
        offset += limit
        query = sparqlt.GET_ANNOTATIONS_QUERY.format(term_uri=filter_term_uri,
                                                     ontology_uri=ontology_uri,
                                                     limit=limit,
                                                     offset=offset)
        results = query_endpoint(query)
    return dict(documents=documents,
                terms_document_frequency=terms_document_frequency,
                annotations_index=annotations_index)


def query_endpoint(query):
    sparql = SPARQLWrapper(conf.BIOTEA_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.query()
    results = sparql.query().convert()
    return results['results']['bindings']


def create_tree(index, clusters):
    tree = {}
    for i, merge in enumerate(clusters):
        if merge[0] < len(index):
            a = {
                'name': index[int(merge[0])]['id'],
                'length': merge[2],
                'title': index[int(merge[0])]['title']
            }
        else:
            a = tree[int(merge[0])]

        if merge[1] < len(index):
            b = {
                'name': index[int(merge[1])]['id'],
                'length': merge[2],
                'title': index[int(merge[1])]['title']
            }
        else:
            b = tree[int(merge[1])]
        tree[i + len(index)] = {
            'branchset': [a, b],
            'name': merge[2],
            'length': merge[2]
        }
    root = {
        'branchset': [tree[len(clusters) + len(index) - 1]],
        'name': 'root',
        'length': 0.0
    }
    return root


def tree_paths(root, paths):
    if type(root['children'][0]) is str:
        paths.append(str(root['distance']) + '|' + str(root['children'][0]))
    else:
        return str(root['distance']) + '|' + tree_paths(root['children'][0])


# annotations_snomed = get_dataset_annotations("http://purl.bioontology.org/ontology/SNOMEDCT/41607009",
#                                              "http://purl.obolibrary.org/obo/GO_")
# dataset = get_feature_matrix(annotations_snomed)
#
# # clustering
# thresh = 0.7
# clusters = hcluster.linkage(dataset['observations'], metric="cosine")
# labels = [item['id'] for item in dataset['index']]
# dn = hcluster.dendrogram(clusters, labels=labels)
# plt.figure()
# hcluster.set_link_color_palette(['m', 'c', 'y', 'k'])
# fig, axes = plt.subplots(1, 2, figsize=(8, 3))
# dn1 = hcluster.dendrogram(clusters, labels=labels, ax=axes[0], above_threshold_color='y', orientation='top')
# dn2 = hcluster.dendrogram(clusters, labels=labels, ax=axes[1], above_threshold_color='#bcbddc', orientation='right')
#
# f_clusters = hcluster.fcluster(clusters, t=0.93)
# #print(f_clusters)
# #plt.show()
#
# #print(hcluster.dendrogram(clusters))
# #print('holi')
# print(clusters)
# root = create_tree(dataset['index'], clusters)
# print(json.dumps(root))
# mpld3.show()