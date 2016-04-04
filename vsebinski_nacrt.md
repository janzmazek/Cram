# Vsebinski načrt

## Opis aplikacije

V glavnem oknu dva igralca igrata [Cram](https://en.wikipedia.org/wiki/Cram_(game)). Nasprotni igralec je lahko človek ali računalnik. Igralec položi domino tako, da klikne na prazno polje ter spusti na sosednjem praznem polju. Karkoli drugega se šteje kot neveljavna poteza.

Aplikacija je v enem od treh stanj:

1. Začetek – uporabnik izbere kašn igro želi igrati
	
	1.način igranja

	* človek – človek
	* človek – računalnik
	* računalnik – računalnik
	
	2.velikost igralnega polja

	* 5x5
	* 6x6
	* 7x7
	
	3.težavnost igre
	
	* lahko
	* težko
	
2. Igra – med igro so v oknu podatki
	* trenutna razporeditev domin
	* kdo je trenutno na potezi

3. Konec igre – prikaže zmagovalca in možnost ponovne igre

Prehod med stanji:

* Prehod iz začetka v igro: sproži ga uporabnik, ko izbere način, velikost in težavnost igre.
* Prehod iz igre v konec igre: sproži ga uporabniški vmesnik, ko ugotovi, da je konec igre
* Prehod iz konca igre v začetek igre: uporabnik ponovno izbere način, velikost in težavnost igre.

## Struktura programa

Aplikacija je napisana v Pythonu 3 in je iz dveh delov:

1. Uporabniški vmesnik: uporablja knjižico [tkinter](http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html).
2. Računalniški igralec: računalnik bo izbiral svoje poteze z algoritmom [minimax](https://en.wikipedia.org/wiki/Minimax). V prihodnosti ga bomo nadgradili z [alfa-beta rezanjem](https://en.wikipedia.org/wiki/Alpha–beta_pruning).

### Razredi

Vsi razredi so v datoteki "cram.py".

#### Razred "GUI"
Razred, v katerem je definiran uporabniški vmesnik. Metode:

* "pripravi_igro(self, master)": pripravi igro, ki jo zahteva uporabnik.
* "zacni_igro(self, rdeci, modri)": prične igro z danima igralcema.
* "prekini_igro(self, rdeci, modri)": prekine igro v primeru, da uporabnik zapusti igro.
* "koncaj_igro(self, zmagovalec)": konča igro in izpiše zmagovalca.
* "ponovi_igro(self, event)": klik na ploščo ponovi igro.
* "spremeni_nacin(self, master, nacin)", "spremeni_velikost(self, master, velikost)" in "spremeni_tezavnost(self, master, tezavnost)": Uporabnik spreminja način, velikost in težavnost igre.
* "naredi_polje(self, master, velikost)" in "naredi_crte(self, velikost)": ustvarimo polje dane velikosti.
* "plosca_klik(self, event)" in "plosca_spust(self, event)": lovi klike in spuste na ploščo.
* "pobarvaj_rdece(self,i1,j1,i2,j2)" in "pobarvaj_modro(self,i1,j1,i2,j2)": polje kamor je igralec položil domino pobarva.
* "naredi_potezo(self,i1,j1,i2,j2)": odigra potezi na polju "(i1,j1)" in "(i2,j2)".

#### Razred "igra"
Objekt tega razreda vsebuje logiko igre. Ima naslednje metode:

* "kopija_igre(self)": naredi kopijo igre.
* "zgodovina_igre(self)": shrani trenutno stanje igre, da se lahko algoritem vrne vanj.
* "veljavne_poteze(self)": vrne seznam parov polj, kamor je možno položiti domino.
* "naredi_potezo(self,i1,j1,i2,j2)": preveri veljavnost potez "(i1,j1)" in "(i2,j2)", pri čemer je "i" vrstica in "j" stolpec.
* "stanje_igre(self)": ugotovi, če je igre konec ali ne.
* "na_potezi": kdo je na potezi: "rdeci", "modri" ali "None".

#### Igralci
Razne vrste igralcev (človek, algoritem minimax, algoritem alfa-beta) predstavimo vsakega s svojim razredom. Objekt, ki predstavlja igralca, mora imeti naslednje metode:

* "__ init __(self, gui)": konstruktorju podamo objekt `gui`, s katerim lahko dostopa do uporabniškega vmesnika in stanja igre
* "igraj(self)": GUI pokliče to metodo, ko je igralec na potezi. V razredu računaknik ustvari vlakno v katerem požene algoritem, v razredu človek pa čaka na klik na polje.
* "preveri(self)": preveri, če je igralec že naredil potezo.
* "prekini(self)":  prekine razmišljanje igralcev.
* "klik(self, i, j)": igralec je na potezi in je kliknil na polje "(i,j)".
* "spust"(self, i, j)": igralec je na potezi in je končal na polju "(i,j)".

##### Razred "človek"
Igralec je človek, potezo dobi s klikom na miško.

##### Razred "računalnik"
Igralec je računalnik, ki ustvari novo vlakno v katerem deluje algoritem.

##### Razred "algoritem"
Razred, ki vsebuje metodo minimax in alfa-beta:

* "__ init __(self, igra)": konstruktorju podamo objekt `igra`, s katerim dostopa do kopije igre.
* "izracunaj_potezo(self, globina)": računalnik pokliče to metodo, da najde najboljšo potezo, po metodi, ki je podana z globino.
* "vrednost_igre(self)": vrne vrednost igre po odigrani potezi izbrane metode.
* "minimax(self, globina, maksimiziramo)": ovrednoti možne poteze po metodi minimax ter vrne najboljšo potezo.
* "alfabeta(self, globina, maksimiziramo)": ovrednoti možne poteze po metodi z alfa-beta rezanjem in vrne najboljšo potezo.
