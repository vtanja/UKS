# UKS

Projekat iz predmeta Upravljanje konfiguracijom softvera. Projekat radili:

- E2  49/2020 Tanja Vukmirović
- E2 117/2020 Nikolina Šarenac
- E2 162/2020 Veljko Vuković
- E2  79/2020 Balša Šarenac

## Pokretanje

Za pokretanje aplikacije je potrebno da podesite virtuelno okruženje. Ako nemate virtuelno okruzenje, instalirajte ga sa

```commandline
pip install virtualenv
```

Onda mozete kreirati novo okruzenje, aktivirati ga i instalirati potrebne dependency-je:

```commandline
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Nakon što ste podesili virtuelno okruženje pozicionirajte se u folder /uks u kome se nalazi fajl manage.py. 
Odatle aplikaciju možete pokrenuti sa:

```commandline
python manage.py runserver
```
