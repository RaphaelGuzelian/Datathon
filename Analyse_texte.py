dico_sentiment_couleur = {"Positive" : [], "Negative" : [], "Neutral" : []}

# Fonction pour extraire le texte du poème
def extract_text(post):
    return post['content-text']

# Fonction pour extraire le lien de l'image
def extract_image_link(content):
    # Convertir le contenu en chaîne de caractères
    content_str = str(content)
    soup = BeautifulSoup(content_str, 'html.parser')
    img_tag = soup.find('img')
    if img_tag and 'src' in img_tag.attrs:
        return img_tag['src']
    return None

# Fonction pour nettoyer le texte du poème
def clean_text(text):
    # Supprimer les noms d'auteur
    authors_to_exclude = ['Jean Coulombe', 'Denis Samson', 'Alain Larose']
    text_without_author = [word for word in text if word not in authors_to_exclude]

    # Supprimer les caractères spéciaux, les chiffres et les espaces indésirables
    cleaned_text = re.sub(r'[^A-Za-zÀ-ÿ\s\']', '', ' '.join(text_without_author))

    # Supprimer les espaces en double
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    return cleaned_text

# Fonction pour analyser le sentiment du texte
def analyze_sentiment(text):
    # Nettoyer le texte avant de l'analyser
    cleaned_text = clean_text(text)

    # Traduire le texte du français vers l'anglais
    translator = Translator()
    text_english = translator.translate(cleaned_text, src='fr', dest='en').text
    print(text_english)

    # Analyser le sentiment de la version anglaise du texte
    sid = SentimentIntensityAnalyzer()
    sentiment_score = sid.polarity_scores(text_english)
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


for post in posts:
  text = extract_text(post)

  url_image = extract_image_link(post)
  print("URL image  : ", url_image)

  sentiment = analyze_sentiment(text)
  print("Sentiment : ", sentiment)

  extract_dominant_colors(url_image, sentiment)

print(dico_sentiment_couleur)