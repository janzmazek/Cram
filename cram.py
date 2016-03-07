import tkinter

# Privzeta minimax globina, če je nismo podali ob zagonu v ukazni vrstici
MINIMAX_PRIVZETA_GLOBINA = 3 

######################################################################
## Igra

IGRALEC_RED = "rdeči"
IGRALEC_BLUE = "modri"
NEPOKRITO = "belo"
NI_KONEC = "ni konec"
VELIKOST_PLOSCE = 4

def nasprotnik(igralec):
    if igralec == IGRALEC_RED:
        return IGRALEC_BLUE
    elif igralec == IGRALEC_BLUE:
        return IGRALEC_RED
    else:
        assert False, "prepovedan nasprotnik"

class Igra():
    def __init__(self):
        self.plosca = []
		for i in range(VELIKOST_PLOSCE):
			self.plosca.append([NEPOKRITO for j in range(VELIKOST_PLOSCE)])
        self.na_potezi = IGRALEC_RED

    def kopija(self):
        """Vrni kopijo te igre."""
        k = Igra()
        k.plosca = [self.plosca[i][:] for i in range(VELIKOST_PLOSCE)]
        k.na_potezi = self.na_potezi
        return k
        
    def veljavne_poteze(self):
        poteze = []
        for i in range(VELIKOST_PLOSCE):
            for j in range(VELIKOST_PLOSCE):
                if self.plosca[i][j] is NEPOKRITO:
                    if self.plosca[i+1][j] is NEPOKRITO:
                        poteze.append((i,j,i+1,j))
                    elif self.plosca[i][j+1] is NEPOKRITO:
                        poteze.append((i,j,i,j+1))
        return poteze

    def povleci_potezi(self, pozicija1, pozicija2):
        """Povleci_potezi(i1, j1, i2, j2) vrne stanje_igre() po potezi ali None, ce je poteza neveljavna."""
        (i1,j1) = pozicija1
        (i2,j2) = pozicija2
        self.veljavne_poteze()
        for i in range(len(poteze)):
            if poteze[i] is (i1, j1, i2, j2) or (i2, j2, i1, j1):
                # Primerja povlečene poteze z veljavnimi
                igrac = self.na_potezi
                self.plosca[i1][j1] = self.na_potezi
                self.plosca[i2][j2] = self.na_potezi
                stanje = self.stanje_igre()
                if stanje == NI_KONEC:
                    # Igre ni konec, zdaj je na potezi nasprotnik
                    self.na_potezi = nasprotnik(self.na_potezi)
                else:
                    # Igre je konec
                    self.na_potezi = None
                return stanje
            elif (self.plosca[i1][j1] != NEPOKRITO) or (self.plosca[i2][j2] != NEPOKRITO) or (self.na_potezi == None):
                # neveljavna poteza
                return None
            else:
                assert False, "prepovedana poteza"

    def stanje_igre(self):
        """Ugotovi, kakšno je trenutno stanje igre. Vrne:
           - IGRALEC_RED, če je igre konec in je zmagal IGRALEC_RED
           - IGRALEC_BLUE, če je igre konec in je zmagal IGRALEC_BLUE
           - NI_KONEC, če igre še ni konec
        """
        
        for i in range(VELIKOST_PLOSCE):
            for j in range(VELIKOST_PLOSCE):
                if self.plosca[i][j] is NEPOKRITO:
                    if self.plosca[i+1][j] is NEPOKRITO:
                        # Našli smo prazni ploscici, igre ni konec
                        return NI_KONEC
                    elif self.plosca[i][j+1] is NEPOKRITO:
                        # Našli smo prazni ploscici, igre ni konec
                        return NI_KONEC
                    else:
                        # Igre je konec
                        return igrac


######################################################################
## Igralec računalnik

class Racunalnik():
    def __init__(self, gui, algoritem):
        self.gui = gui
        self.algoritem = algoritem # Algoritem, ki izračuna potezo
        self.vlakno = None # Vlakno, ki razmišlja

    def igraj(self):
        """Igraj potezo, ki jo vrne algoritem."""
        # Naredimo vlakno:
        self.vlakno = threading.Thread(...)
        # Poženemo vlakno:
        self.vlakno.start()
        # Gremo preverjat, če sta bili najdeni potezi:
        ...

    def preveri_potezi(self):
        #Vsakih 100ms preveri, ali je algoritem že izračunal potezi.


    def prekini(self):
        # To metodo kliče GUI, če je treba prekiniti razmišljanje.


    def klik(self, pozicija1):
        # Računalnik ignorira klike.
        pass
    
    def spust(self, pozicija2):
        # Računalnik ignorira spuste.
        pass
    
######################################################################
