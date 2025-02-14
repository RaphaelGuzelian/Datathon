dico_sentiment_couleur = {"Positive" : [], "Negative" : [], "Neutral" : []}

# Fonction pour extraire le titre du poème
def extract_title(json_data):
    return json_data['title']

# Fonction pour extraire le lien de l'image
def extract_image_link(content):
    # Convertir le contenu en chaîne de caractères
    content_str = str(content)
    soup = BeautifulSoup(content_str, 'html.parser')
    img_tag = soup.find('img')
    if img_tag and 'src' in img_tag.attrs:
        return img_tag['src']
    return None


# Fonction pour extraire les trois couleurs dominantes de l'image
def extract_dominant_colors(url_image, sentiment, nomb_bins = 4, num_colors=3):
    if url_image is None:
        return

    if not url_image.startswith("https:"):
        url_image = "https:" + url_image

    response = requests.get(url_image)

    if response.status_code != 200:
        return

    imgfile = PIL.Image.open(io.BytesIO(response.content))
    numarray = np.array(imgfile.getdata(), np.uint8)

    clusters = KMeans(n_clusters=nomb_bins, n_init=2)
    clusters.fit(numarray)
    npbins = np.arange(0, nomb_bins + 1)
    histogram = np.histogram(clusters.labels_, bins=npbins)
    labels = np.unique(clusters.labels_)

    # Trie les histogrammes en ordre décroissant
    sorted_histogram = sorted(enumerate(histogram[0]), key=lambda x: x[1], reverse=True)

    # Sélectionne les trois couleurs les plus représentées
    selected_labels = [item[0] for item in sorted_histogram[:num_colors]]

    for label in selected_labels:
        rgb_code = "#%02x%02x%02x" % (
            math.ceil(clusters.cluster_centers_[label][0]),
            math.ceil(clusters.cluster_centers_[label][1]),
            math.ceil(clusters.cluster_centers_[label][2]),
        )

        # Récupération des composantes RGB
        r = int(rgb_code[1:3], 16)
        g = int(rgb_code[3:5], 16)
        b = int(rgb_code[5:7], 16)
        temp = [r, g, b]

        min_colours = {}
        for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - temp[0]) ** 2
            gd = (g_c - temp[1]) ** 2
            bd = (b_c - temp[2]) ** 2
            min_colours[(rd + gd + bd)] = name

        # On cherche la couleur la plus proche de la nôtre
        couleur_dominante = min_colours[min(min_colours.keys())]

        # On ajoute la couleur au sentiment correspondant
        dico_sentiment_couleur[sentiment].append(couleur_dominante)



# Fonction pour analyser le sentiment du titre
def analyze_sentiment(title):
    # Traduire le titre du français vers l'anglais
    translator = Translator()
    title_english = translator.translate(title, src='fr', dest='en').text

    # Analyser le sentiment de la version anglaise du titre
    sid = SentimentIntensityAnalyzer()
    sentiment_score = sid.polarity_scores(title_english)
    print(sentiment_score)

    # Classer en fonction du score de positivité
    pos = sentiment_score["pos"]
    neg = sentiment_score["neg"]
    neu = sentiment_score["neu"]

    if (pos > neg) and (pos > neu):
      return "Positive"
    elif (neg > pos) and (neg > neu):
      return "Negative"
    else :
      return "Neutral"

# Fonction pour afficher les graphes
def show():
  # Initialiser les compteurs pour chaque catégorie
  positive_counter = Counter(dico_sentiment_couleur['Positive'])
  negative_counter = Counter(dico_sentiment_couleur['Negative'])
  neutral_counter = Counter(dico_sentiment_couleur['Neutral'])

  # Les données à afficher
  categories = ['Positive', 'Negative', 'Neutral']

  # Créer une figure et des sous-plots pour chaque catégorie
  fig, axs = plot.subplots(3, 1, figsize=(10, 12), sharex=True)

  # Tracer un graphe à barres pour chaque catégorie
  for i, (category, all_colors) in enumerate(zip(categories, [positive_counter, negative_counter, neutral_counter])):
      ax = axs[i]
      color_names = list(all_colors.keys())
      occurrences = list(all_colors.values())

      # Tracer les barres avec la couleur associée
      bars = ax.bar(color_names, occurrences, color=color_names)

      # Ajouter les étiquettes et le titre
      ax.set_ylabel('Occurrences')
      ax.set_title(f'Colors for {category} Sentiment')

  # Ajouter une légende
  axs[2].legend(bars, color_names, title='Colors')

  # Afficher le graphique
  plot.show()




for post in posts[:5]:
  print("\n")

  titre = extract_title(post)
  print("Titre : ", titre)

  url_image = extract_image_link(post)
  print("URL image  : ", url_image)

  sentiment = analyze_sentiment(titre)
  print("Sentiment : ", sentiment)

  print(dico_sentiment_couleur)
  print("\n")

  extract_dominant_colors(url_image, sentiment)

show()