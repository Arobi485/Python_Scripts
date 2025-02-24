import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

# Read the text from a file
with open('sample_text.txt', 'r', encoding='utf-8') as file:
    text = file.read()

# Define stopwords to exclude from the word cloud
stopwords = set(STOPWORDS)
# Add any additional stopwords if needed
stopwords.update(['example', 'words', 'to', 'remove'])

# Generate the word cloud
wordcloud = WordCloud(
    width=800,
    height=400,
    background_color='white',
    stopwords=stopwords,
    min_font_size=10
).generate(text)

# Display the generated image
plt.figure(figsize=(15, 7.5), facecolor=None)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.tight_layout(pad=0)
plt.show()