# Primera pràctica d'AP2: _Monopoly_

En aquesta pràcitca m'ha estat proposat recrear el clàssic joc de taula del _Monopoly_ amb Python. Tot partint d'un esquelet amb algunes funcionalitats ja implementades, he implementat la lògica del joc i he fet que els jugadors automàtics hi disputin partides.

Les partides es poden visualitzar en un navegador.

## Instruccions per fer servir el programa
- Per **simular una partida**, cal executar `./src/main.py`** (per mitjà de l'intèrprete de Python). És important que s'executi des del directori `.`, que és on es troba aquest README. El programa buidarà el directori `./imgs/` i l'omplirà de noves imatges.
- Si el programa nota que la partida triga més de 400 torns en finalitzar, l'atura. El programa `./src/seedfinder.py` és un _brute-forcer_ que troba un _seed_ on la partida finalitza en menys de 400 torns. Per fer servir aquest valor en simular una partida, cal editar el valor de la constant `SEED` a `./src/const.py` (valor `???` per defecte).
- Per **mostrar les imatges a la pàgina web**, cal executar `./src/slideshow.py`, també des del directori `.` i passar els arguments adients. A Windows, hauràs d'emprar PowerShell i executar aquesta comanda:
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
Generalment, es segueixen [les regles oficials del joc](https://instructions.hasbro.com/api/download/C1009_en-nz_monopoly-classic-game.pdf). S'han pres certes decisions de disseny que divaguen una mica de les regles oficials:
- El joc es juga amb quatre jugadors.
- Les partides només poden durar 400 torns. Si en acabar el 400è torn encara queda més d'un jugador en peu, la partida acaba.
- No hi ha límit en el número total de cases, hotels o cartes.
- Per construïr un hotel en un carrer, no s'han de tornar a la banca les cases: aquestes romanen en la casella.
- Si un jugador no pot o no vol comprar una propietat, aquesta simplement no es compra (no hi ha subhasta).
- Els jugadors no poden negociar, fer tractes ni intercanviar elements entre ells.
- Les accions de gestió (comprar o vendre cases/hotels, hipotecar/deshipotecar propietats, vendre propietats al banc, cobrar el salari de passar per sortida) només es poden dur a terme després que el jugador mogui i compleixi amb les accions de la casella on cau.
- Si en cap moment un jugador baixa dels $0, és eliminat inmediatament.
- La banca salda tot deute: és a dir, si un deutor ha de pagar una quantitat però no té diners suficients, el creditor rep la totalitat de la quota.
- Els jugadors no poden pagar $50 per sortir de la presó, ni els han de pagar per sortir després de tres torns.

A continuació surten redactades algunes regles oficials poc conegudes que he implementat:
- Quan un jugador **és eliminat**, ha de donar totes les seves propietats al banc, tret de les hipotecades, que ha de donar al jugador que l'ha eliminat. El jugador que rep les propietats hipotecades ha de o bé treure l'hipoteca (pagant el cost de deshipotecar) o assumir-la (pagant un 10% del cost d'hipotecar). El jugador que rep les propietats, per tant, també pot resultar eliminat.
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
- **`board.py`** conté:
  - la classe **`Board`**, que representa el tauler de joc complert i gestiona el progrés dels torns i de la partida
  - la classe **`DebugBoard`**, que funciona com el `Board`, però pren per arguments un vector de **tirades de daus** i de **cartes**. La faig servir per testejar.
  - funcions per guardar i carregar taulers en format pickle.
- **`tile.py`** conté:
  - diverses classes que representen els diferents tipus de casella:
    - La classe `Tile` és una classe base per a tipus més especifics.
    - La classe `Property` és una classe base per a caselles posseïbles.
  - la funció  `build_tile(board: Board, data: dict[str, Any]) -> Tile`, que crea caselles del tipus adient
- **`player.py`**

### Dibuix
En diverses ocasions, la l tauler es dibuixa quan un jugador:
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