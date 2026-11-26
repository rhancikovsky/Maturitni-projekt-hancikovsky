# Flappy Bird - Python / Pygame

Jednoducha 2D hra jako skolni projekt.

## Spusteni ve Windows

1. Nainstaluj Python 3 z https://www.python.org/downloads/ (pri instalaci zatrhni **Add Python to PATH**).
2. Otevri slozku projektu ve VS Code.
3. Otevri terminal ve VS Code (Terminal -> New Terminal).
4. Nainstaluj knihovnu:

```bash
py -m pip install -r requirements.txt
```

5. Spust hru:

```bash
py main.py
```

Pokud prikaz `py` nefunguje, zkus `python` misto `py`.

## Ovladani

- Mezernik nebo sipka nahoru: skok
- Klik mysi: skok / start / restart
- ESC: ukoncit hru

## Co projekt obsahuje

- gravitaci a skok ptacka
- nahodne generovane trubky
- detekci kolizi
- pocitani skore
- ulozeni nejlepsiho skore do `best_score.json`
- menu a obrazovku Game Over

Grafika je kreslena primo v Pygame, takze nejsou potreba zadne obrazky ani zvuky.
