Pour commencer, créez un environnement virtuel Python 3 et activez-le :

```bash
python3 -m venv .venv
source env/bin/activate  # Sur Windows : env\Scripts\activate
```

Installez les dépendances requises avec la commande suivante :

```bash
pip install -r requirements.txt
```

Ensuite, lancez l'application avec Streamlit :

```bash
streamlit run app.py
```