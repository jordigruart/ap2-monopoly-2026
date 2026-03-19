# Primera pràctica d'AP2: _Monopoly_

En aquesta pràcitca m'ha estat proposat recrear el clàssic joc de taula del _Monopoly_ amb Python. Tot partint d'un esquelet amb algunes funcionalitats ja implementades, he implementat la lògica del joc i he fet que els jugadors automàtics hi disputin partides.

Les partides es poden visualitzar en un navegador.

## Instruccions per fer servir el programa
- Per **simular una partida**, cal executar **`./src/main.py`** (per mitjà de l'intèrprete de Python). És important que s'executi des del directori `.`, que és on es troba aquest README. El programa buidarà el directori `./imgs/` i l'omplirà de noves imatges.
- Si el programa nota que la partida triga més de 400 torns en finalitzar, l'atura. El programa `./src/seedfinder.py` és un _brute-forcer_ que troba un _seed_ on la partida finalitza en menys de 400 torns. Per fer servir aquest valor en simular una partida, cal editar el valor de la constant `SEED` a `./src/const.py` (valor `1383` per defecte).
- Per **mostrar les imatges a la pàgina web**, cal executar `./src/slideshow.py`, també des del directori `.` (important!) i passar els arguments adients. A Windows, hauràs d'emprar PowerShell i executar aquesta comanda:
  ```powershell
  python3 src/slideshow.py partida.html (ls imgs *.svg)
  ```
  A sistemes basats en UNIX, com ara macOS o Linux, podràs fer servir la següent comanda:
  ```bash
  ls imgs | python3 src/slideshow.py partida.html
  ```
- Per **mostrar la pàgina web**, obre el fitxer `./partida.html` amb qualsevol navegador.
- Per **executar els jocs de proves**, executa a la terminal `pytest ./src`, o bé fes servir l'extensió de VSCode vista a classe de laboratori. Les imatges generades en els tests acaben emmagatzemades a `./debug/imgs`.

## Funcionament de la partida
### Modificacions i aclaracions respecte les regles oficials
Generalment, es segueixen [les regles oficials del joc](https://instructions.hasbro.com/api/download/C1009_en-nz_monopoly-classic-game.pdf). S'han pres certes decisions de disseny per facilitar l'implementació que divaguen una mica de les regles oficials:
- El joc es juga amb quatre jugadors.
- Les partides només poden durar 400 torns. Si en acabar el 400è torn encara queda més d'un jugador en peu, la partida acaba.
- No hi ha límit en el número total de cases, hotels o cartes.
- Per construïr un hotel en un carrer, no s'han de tornar a la banca les cases: aquestes romanen en la casella.
- Si un jugador no pot o no vol comprar una propietat, aquesta simplement no es compra (no hi ha subhasta).
- Els jugadors no poden negociar, fer tractes ni intercanviar elements entre ells.
- Les accions de gestió (comprar o vendre cases/hotels, hipotecar/deshipotecar propietats, vendre propietats al banc, cobrar el salari de passar per sortida) només es poden dur a terme després que el jugador mogui i compleixi amb les accions de la casella on cau.
- Si en cap moment un jugador baixa dels $0, és eliminat inmediatament.
- La banca salda tot deute: és a dir, si un deutor ha de pagar una quantitat però no té diners suficients, el creditor rep igualment la totalitat de la quota i el deutor és eliminat.
- La targeta de desplaçar-te a l'utilitat més propera aplica un increment del 1000% respecte l'alquiler sense multiplicador, i no en base a la suma dels daus.
- Els jugadors no poden pagar $50 per sortir de la presó, ni els han de pagar per sortir després de tres torns.

A continuació surten redactades algunes regles oficials poc conegudes que he implementat:
- Quan un jugador **és eliminat**, ha de donar totes les seves propietats al banc, tret de les hipotecades, que ha de donar al jugador que l'ha eliminat. El jugador que rep les propietats hipotecades ha de o bé treure l'hipoteca (pagant el cost de deshipotecar) o assumir-la (pagant un 10% del cost d'hipotecar). El jugador que rep les propietats, per tant, també pot resultar eliminat.
- Hom surt de la presó després de 3 torns. Aquests torns es compten de la següent manera:
  - no es registra un torn en presó fins que el jugador acaba totes les accions del torn
  - el torn on el jugador va a presó no es compta com a torn passat en presó.
- La casella de _Free parking_ no fa res.

### Estratègia dels jugadors
Els jugadors de la partida són en Jordi, la Mireia, l'Arnau i la Marta. L'ordre en que juguen és l'ordre en que els he llistat.

L'estratègia dels jugadors gira entorn a una quantitat límit  de **$40**:
- Si es troben per sota del limit, jugaran de forma econòmica:
  - Si els és oferta l'oportunitat de comprar una propietat, la rebutjarà.
  - Al final del seu torn, intentaran vendre edificis i hipotecar propietats fins que estiguin per sobre o a $40, o bé fins que no tinguin propietats a lliurar.
  - En eliminar altres jugadors i rebre les seves propietats hipotecades, decidiran assumir l'hipoteca en comptes de pagar per treure-la.
- Si es troben per sobre o al limit, gastaràn el que puguin, fins que baixin dels $40 o no puguin gastar.

Si bé el límit és baix, les partides s'allarguen considerablement si esdevé més alt. Serveix com a límit simbòlic, per tal de que certes accions siguin possibles en una partida.

## Funcionament
### Descripció de la base de codi
El directori `src` conté tots els fitxers que fan funcionar el programa. A continuació es fa un resum dels continguts:
- El **subdirectori `data`** conté fitxers de tipus _json_ que emmagatzemen informació dels jugadors, les fitxes, i les cartes. El número de jugadors es pot canviar, fins a un màxim de **4 jugadors**.
- **`main.py`** és el programa principal.
- **`tile.py`** conté:
  - diverses classes que representen els diferents tipus de casella:
    - La classe `Tile` és una classe base per a tipus més especifics.
    - La classe `Property` és una classe base per a caselles posseïbles, que són `Utility`, `Street` i `Station`.
  - la funció  `build_tile(board: Board, **data: Any) -> Tile`, que crea instàncies del tipus adient a partir d'atributs trets del JSON.
- **`player.py`** conté:
  - una classe `Player` que representa el jugador.
  - la funció `build_player(board: Board, **data: Any) -> Player`, que crea instàncies de `Player` a partir d'atributs trets del JSON.
- **`card.py`** conté:
  - diverses classes que representen diferents tipus de carta. La classe `Card` és la classe base per a totes les cartes.
  - la funció `build_card(board: Board, **data: Any) -> Card`, que crea instàncies del tipus adient a partir de les d'atributs trets del JSON.
- **`deck.py`** conté la classe `Deck`, que s'inicialitza a partir d'un path a un JSON que conté l'informació de totes les cartes. La classe té el mòdul `extract`, que retorna una carta aleatòria (sense exhaurir-la).
- **`board.py`** conté:
  - la classe **`Board`**, que representa el tauler de joc complert i gestiona el progrés dels torns i de la partida. Durant la partida es crea una única instància d'aquesta clase, que tot `Tile`, `Player`, `Deck` i `Card` manté guardat en les seves variables internes.
  - la classe **`DebugBoard`**, que hereta `Board` però pren per arguments un vector de **tirades de daus** i de **cartes** que fa servir en comptes de triar aleatòriament. Els mòduls de proves la fan servir per simular partides.
- **`aitools.py`** conté:

- **`draw.py`** conté la funcionalitat de dibuixar el tauler. A destacar és la funció `draw(board: Board, svg_path: str = const.IMAGE_PATH) -> None`, que dibuixa el tauler i el guarda en el _path_ especificat.

### Dibuix i sortida a la terminal
El tauler es dibuixa **diverses vegades** en un mateix torn. Concretament, el tauler es dibuixa quan un jugador:
- tira els daus
- es desplaça
- paga un impost
- obtén una propietat, tant quan la compra o quan la rephipotecada d'un jugador en eliminar-lo
- cau en una propietat que pertany a un jugador diferent i paga l'alquiler
- roba una carta
- va a la presó
- edifica
- desedifica
- hipoteca
- és eliminat
- és lliurat de la presó

Cada vegada que es dibuixa el tauler, el programa també fa un `print` a stdout que descriu la acció.

El mètode cridat per dibuixar el tauler és `Board.draw()` dins de la classe `Board` (no el `draw` de `draw.py`):
> Per tal d'assignar un número a cada imatge s'ha de mantenir un comptador i incrementar-lo cada vegada que es dibuixa el tauler. Això es pot fer mantenint el comptador emmagatzemat en una instància d'una classe.
>
> El tauler es dibuixa des de punts molt diversos en l'execució (vegi la llista anterior). Hi ha mètodes tant en `Player` com en `Tile` com en `Card` que volen dibuixar el tauler. La instància d'aquesta classe, llavors, ha d'estar en tots aquests mètodes. Com que tots tenen una instància de `Board`, em va semblar adequat prendre la decisió de disseny de **tenir el mètode a `Board`**.
> 
> El mètode `Board.draw()` decideix el path on dibuixar segons el path donat al objecte `Board` quan s'inicialitza. Aquest path és, per defecte, `./imgs` per partides normals i `./debug/imgs` per partides de prova o pel _brute-forcer_.

# Autors
Jordi Gruart, Jordi Petit

---

## throwaay
A continuació es presenta un resum del que passa cada torn:

> **Al principi:**
> - Si el jugador comença a la presó:
>   - Pot fer servir una **carta de sortir de la presó** per lliurar-se; tot seguit tira els daus i es desplaça normalment
>   - Si no en té, ha de tirar els daus. Es lliura si treu dobles, els quals fa servir per desplaçar-se
>
>   No pot pagar $50 per sortir de la presó.
>
> - Si el jugador no comença a la presó, simplement tira els daus i es desplaça. Si ha tret dobles per tercera vegada seguida, va directe a la presó i el seu torn acaba.

> **Quan el jugador aterra en una casella:**
> - Si ha passat la casella de sortida, rep una bonificació de $200 abans d'aterrar-hi.
> - Si cau en una casella sense propietari i no vol o no pot comprar-la, no hi ha cap subhasta.
>
> - Si el jugador va a la presó, el seu torn acaba.

> **Després d'efectuar totes les accions anteriors:**
> - El jugador -- independentment de si està empresonat -- pot construïr o derruïr edificis i hipotecar propietats.
> - Aquest tipus d'acció només es pot dur a terme aquí; és a dir, quan totes les accions anteriors han estat completades.
> - El número de cases i d'hotels disponibles és ilimitat.
>
> Si **al final del torn** ha passat tres torns, el jugador és lliurat presó.

> Si en cap moment un jugador baixa dels $0, està eliminat a l'instant.