FROM python:3.9.7-slim
WORKDIR /app
COPY ./cmd/api ./
RUN pip install textblob
RUN python -m nltk.downloader punkt averaged_perceptron_tagger movie_reviews stopwords
RUN python -m textblob.download_corpora
ENTRYPOINT ["python3", "sentiment-analyzer.py"]