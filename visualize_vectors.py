import pandas as pd
import numpy as np
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import cosine
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns

def visualize(data, lemma):

    df = pd.read_csv('{}_vectors_arxh.csv'.format(data), sep= '\t', encoding='UTF-8')

    df = df[df['lemma'] == lemma]

    df['vectors'] = df['vectors'].apply(lambda y: [float(x) for x in y.split(', ')])


    # cosine_dist = pairwise_distances(np.array(df.vectors.to_list()), metric="cosine")

    tsne = TSNE(n_components=2, perplexity=5, n_iter=5000, metric='cosine')

    tsne_results = tsne.fit_transform(df.vectors.to_list())


    df['tsne-2d-one'] = tsne_results[:,0]
    df['tsne-2d-two'] = tsne_results[:,1]
    plt.figure(figsize=(16,10))
    sns.scatterplot(
        x="tsne-2d-one", y="tsne-2d-two",
        hue="sense_2",
        style="sense_2",
        palette=sns.color_palette("hls", df.sense_2.unique().shape[0]),
        data=df,
        legend="full"
    )

visualize('training_data', 'ἀρχή')
