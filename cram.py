import tkinter
import threading
import time
import argparse 

######################################################################
## Igra

IGRALEC_RED = "rdeci"
IGRALEC_BLUE = "modri"
NEPOKRITO = "belo"
NI_KONEC = "ni konec"

def nasprotnik(igralec):
    if igralec == IGRALEC_RED:
        return IGRALEC_BLUE
    elif igralec == IGRALEC_BLUE:
        return IGRALEC_RED
    else:
        assert False, "nasprotnik: prepovedan nasprotnik"

class Igra():
    def __init__(self, velikost):
        self.velikost = velikost
        self.plosca = []
        for i in range(self.velikost):
            self.plosca.append([NEPOKRITO for j in range(self.velikost)])
        self.na_potezi = IGRALEC_RED
        self.zgodovina = []

    def kopija_igre(self):
        """Vrne kopijo te igre."""
        k = Igra(velikost)
        k.plosca = [self.plosca[i][:] for i in range(self.velikost)]
        k.na_potezi = self.na_potezi
        k.zgodovina = self.zgodovina
        return k

    def zgodovina_igre(self):
        """Shrani trenutno stanje igre."""
        z_plosca = [self.plosca[i][:] for i in range(self.velikost)]
        z_na_potezi = self.na_potezi
        self.zgodovina.append((z_plosca, z_na_potezi))
        return z_na_potezi
 
    def veljavne_poteze(self):
        """Vrne seznam veljavnih potez."""
        veljavne = []
        for i in range(self.velikost):
            for j in range(self.velikost):
                if self.plosca[i][j] == NEPOKRITO:
                    if self.plosca[i+1][j] == NEPOKRITO:
                        veljavne.append((i,j,i+1,j))
                    elif self.plosca[i][j+1] == NEPOKRITO:
                        veljavne.append((i,j,i,j+1))
        return veljavne

    def naredi_potezo(self, pozicija1, pozicija2):
        """Vrne stanje igre po potezi ali None, ce je poteza neveljavna."""
        (i1,j1) = pozicija1
        (i2,j2) = pozicija2
        self.veljavne_poteze()
        for i in veljavne_poteze():
            if (i == (i1, j1, i2, j2)) or (i == (i2, j2, i1, j1)): # Primerja povlecene poteze z veljavnimi.
                self.plosca[i1][j1] = self.na_potezi
                self.plosca[i2][j2] = self.na_potezi
                self.zgodovina_igre()
                stanje = self.stanje_igre()
                if stanje == NI_KONEC:
                    self.na_potezi = nasprotnik(self.na_potezi) # Igre ni konec.
                else:
                    self.na_potezi = None # Igre je konec.
                return stanje
            elif (self.plosca[i1][j1] != NEPOKRITO) or (self.plosca[i2][j2] != NEPOKRITO) or (self.na_potezi == None): # Neveljevne poteze.
                return None
            else:
                assert False, "igra: prepovedana poteza"

    def stanje_igre(self):
        """Ugotovi, kaksno je trenutno stanje igre. Vrne:
           - IGRALEC_RED, ce je igre konec in je zmagal IGRALEC_RED
           - IGRALEC_BLUE, ce je igre konec in je zmagal IGRALEC_BLUE
           - NI_KONEC, ce igre se ni konec
        """
        zmagovalec = self.na_potezi
        for i in range(self.velikost):
            for j in range(self.velikost):
                if self.plosca[i][j] == NEPOKRITO:
                    if self.plosca[i+1][j] == NEPOKRITO:
                        return NI_KONEC # Igre ni konec.
                    elif self.plosca[i][j+1] == NEPOKRITO:
                        return NI_KONEC # Igre ni konec.
                    else:
                        return zmagovalec # Igre je konec.

    
######################################################################
## Igralec racunalnik

class Racunalnik():
    def __init__(self, gui, algoritem):
        self.gui = gui
        self.algoritem = algoritem
        self.vlakno = None # Vlakno, ki razmislja.

    def igraj(self):
        """Igraj potezo, ki jo vrne algoritem."""
        # Naredimo vlakno, ki mu podamo kopijo igre.
        self.vlakno = threading.Thread(target=lambda: self.algoritem.izracunaj_potezo(self.gui.igra.kopija_igre()))
        self.vlakno.start()
        while self.algoritem.poteza is None:
            time.sleep(0.1) # Pocaka 100ms.
            if self.algoritem.poteza: # Algoritem je nasel potezo.
                self.gui.povleci_potezo(self.algoritem.poteza)
                self.vlakno = None
            elif self.algoritem.zapri: # Razmislanje je prekinjeno.
                break

    def prekini(self):
        """Prekinemo razmisljanje algortitma."""
        if self.vlakno:
            self.algoritem.prekini()
            self.vlakno.join()
            self.vlakno = None

    def klik(self, pozicija1):
        # Računalnik ignorira klike.
        pass
    
    def spust(self, pozicija2):
        # Računalnik ignorira spuste.
        pass
    
######################################################################
## Algoritem minimax

UTEZ = 1000
NESKONCNO = UTEZ + 1

class Minimax():

    def __init__(self, globina):
        self.globina = globina
        self.igra = None
        self.kdo_sem = None  # Katerega igralca igramo.
        self.poteza = None
        self.zapri = False

    def prekini(self):
        """Metoda, ki jo pokliče GUI, ker je uporabnik zaprl okno ali izbral novo igro."""
        self.zapri = True

    def izracunaj_potezo(self, igra):
        """Izračunaj potezo za trenutno stanje dane igre."""
        self.zapri = False
        self.igra = igra # Dobimo kopijo igre.
        self.kdo_sem = self.igra.na_potezi
        self.poteza = None
        (poteza, vrednost) = self.minimax(self.globina, True) # Pozenemo minimax.
        if self.zapri is False:
            self.poteza = poteza

    def vrednost_igre(self):
        """vrednost_igre() sešteje vrednosti vseh vrstic/stolpcev na plošči."""
        # Slovar, ki pove, koliko so vredne posamezne vrstice/stolpci, kjer je "p : v":
        # x je stevilo nezasedenih polj v vrstici/stolpcu in y vrednost vrstice/stolpca.
        if self.igra.velikost == 4: # Ce je igralno polje velikosti 4x4.
            vrednosti_vrstic_stolpcev = {
                0 : Minimax.UTEZ,
                2 : Minimax.UTEZ//10,
                4 : 0,
                3 : -Minimax.UTEZ//10,
                1 : -Minimax.UTEZ
            }
        elif self.igra.velikost == 6: # Ce je igralno polje velikosti 6x6.
            vrednosti_vrstic_stolpcev = {
                0 : Minimax.UTEZ,
                2 : Minimax.UTEZ//10,
                4 : Minimax.UTEZ//100,
                6 : 0,
                5 : -Minimax.UTEZ//100,
                3 : -Minimax.UTEZ//10,
                1 : -Minimax.UTEZ
            }
        elif self.igra.velikost == 8: # Ce je igralno polje velikosti 8x8.
            vrednosti_vrstic_stolpcev = {
                0 : Minimax.UTEZ,
                2 : Minimax.UTEZ//10,
                4 : Minimax.UTEZ//100,
                6 : Minimax.UTEZ//1000,
                8 : 0,
                7 : -Minimax.UTEZ//1000,
                5 : -Minimax.UTEZ//100,
                3 : -Minimax.UTEZ//10,
                1 : -Minimax.UTEZ
            }   
        vrednost = 0
        for i in range(self.igra.velikost):
            for j in range(self.igra.velikost):
                if self.igra.plosca[i][j] == NEPOKRITO:
                    p1 += 1
                elif self.igra.plosca[j][i] == NEPOKRITO:
                    p2 += 1
            vrednost += vrednosti_vrstic_stolpcev.get(p1) + vrednosti_vrstic_stolpcev.get(p2)
        return vrednost

    def minimax(self, globina, maksimiziramo):
        """Glavna metoda minimax."""
        if self.zapri:
            return (None, 0) # Igro prekinemo.
        rezultat = self.igra.stanje_igre()
        if (rezultat == IGRALEC_RED) or (rezultat == IGRALEC_BLUE): # Igre je konec.
            if zmagovalec == self.kdo_sem:
                return (None, Minimax.ZMAGA)
            elif zmagovalec == nasprotnik(self.kdo_sem):
                return (None, -Minimax.ZMAGA)
        elif rezultat == NI_KONEC: # Igre ni konec.
            if globina == 0: # Zmanjkalo globine.
                return (None, self.vrednost_igre())
            else:
                if maksimiziramo:  # Maksimiziramo
                    naj_poteza = None
                    naj_vrednost = -Minimax.NESKONCNO
                    for p in self.igra.veljavne_poteze():
                        (pozicija1, pozicija2) = p
                        self.igra.naredi_potezo(pozicija1,pozicija2)
                        vrednost = self.minimax(globina-1, not maksimiziramo)[2]
                        (self.igra.plosca, self.igra.na_potezi) = self.igra.zgodovina.pop()
                        if vrednost > naj_vrednost:
                            naj_vrednost = vrednost
                            naj_poteza = p
                            
                else: # Minimiziramo
                    naj_poteza = None
                    naj_vrednost = Minimax.NESKONCNO
                    for p in self.igra.veljavne_poteze():
                        (pozicija1, pozicija2) = p
                        self.igra.naredi_potezo(pozicija1,pozicija2)
                        vrednost = self.minimax(globina-1, not maksimiziramo)[2]
                        (self.igra.plosca, self.igra.na_potezi) = self.igra.zgodovina.pop()
                        if vrednost < naj_vrednost:
                            naj_vrednost = vrednost
                            naj_poteza = p

                assert (naj_poteza is not None), "minimax: izračunana poteza je None"
                return (naj_poteza, naj_vrednost)
        else:
            assert False, "minimax: prepovedano stanje igre"

######################################################################
