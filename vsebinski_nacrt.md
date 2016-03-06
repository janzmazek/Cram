# Vsebinski načrt

## Opis aplikacije

V glavnem oknu dva igralca igrata [Cram](https://en.wikipedia.org/wiki/Cram_(game)). Nasprotni igralec je lahko človek ali računalnik. Igralec igra tako, da klikne na dva polja, na katera želi postaviti domino.

Aplikacija je v enem od treh stanj:

1. Začetek – uporabnik izbere eno izmed dveh možnostih igranja
	* človek – človek
	* človek – računalnik

2. Igra – med igro so v oknu podatki
	* trenutna razporeditev domin
	* kdo je trenutno na potezi

3. Konec igre – prikaže zmagovalca

Prehod med stanji:

* Prehod iz začetka v igro: sproži ga uporabnik, ko izbere način igranja
* Prehod iz igre v konec igre: sproži ga uporabniški vmesnik, ko ugotovi, da je konec igre
* Prehod iz konca igre v začetek igre: uporabnik uporabnik klikne na gump "igraj še enkrat".

## Struktura programa

Aplikacija je napisana v Pythonu 3 in je iz dveh delov:

1. Uporabniški vmesnik: uporablja knjižico [tkinter](http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html).
2. Računalniški igralec: računalnik bo izbiral svoje poteze z algoritmom [minimax](https://en.wikipedia.org/wiki/Minimax). V prihodnosti ga bomo nadgradili z [alfa-beta rezanjem](https://en.wikipedia.org/wiki/Alpha–beta_pruning).

### Razredi

Vsi razredi so v datoteki "cram.py".

#### Razred "GUI"
Razred, v katerem je definiran uporabniški vmesnik. Metode:
* "zacni_igro(self, Igralec_red, Igralec_blue)": začni igrati igro z danimi igralci
* "koncaj_igro(self, zmagovalec)": končaj igro z danim zmagovalecem

#### Razred "igra"
Objekt tega razreda vsebuje trenutno stanje igre. Ima naslednje metode:
* "veljavne_poteze(self)": vrne seznam parov polj, kamor je možno položiti domino
* "povleci_potezi(self,i1,j1,i2,j2)": odigraj potezi na polju "(i1,j1)" in "(i2,j2)", pri čemer je "i" vrstica in "j" stolpec
* "stanje_igre(self)": ugotovi, kakšno je trenutno stanje igre: ni konec, zmagal je "red", zmagal je "blue"
* "na_potezi": kdo je na potezi: "igralec_red", "igralec_blue" ali "None"

#### Igralci
Razne vrste igralcev (človek, algoritem minimax, algoritem alfa-beta) predstavimo vsakega s svojim razredom. Objekt, ki predstavlja igralca, mora imeti naslednje metode:

* "__ init __(self, gui)": konstruktorju podamo objekt `gui`, s katerim lahko dostopa do uporabniškega vmesnika in stanja igre
* "igraj(self)": GUI pokliče to metodo, ko je igralec na potezi
* "klik(self, i, j)": GUI pokliče to metodo, če je igralec na potezi in je uporabnik kliknil polje "(i,j)" na plošči
* "spust"(self, i, j)": GUI pokliče to metodo, če je igralec že kliknil na polje in končal klik na polju "(i,j)" na plošči

##### Razred "clovek"
Igralec je človek, potezo dobi s klikom na miško.

##### Razred "minimax"
Igralec računalnik, ki igra z metodo minimax.
