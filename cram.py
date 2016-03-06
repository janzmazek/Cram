import tkinter

# Privzeta minimax globina, če je nismo podali ob zagonu v ukazni vrstici
MINIMAX_PRIVZETA_GLOBINA = 3 

######################################################################
## Igra

IGRALEC_RED = "rdeči"
IGRALEC_BLUE = "modri"
NI_KONEC = "ni konec"
VELIKOST_PLOSCE = 4

def nasprotnik(igralec):
    if igralec == IGRALEC_RED:
        return IGRALEC_BLUE
    else:
        return IGRALEC_RED

class Igra():
    def __init__(self):
        self.plosca = []
		for i in range(VELIKOST_PLOSCE):
			self.plosca.append([None for j in range(VELIKOST_PLOSCE)])
        self.na_potezi = IGRALEC_RED

    def veljavne_poteze(self):
        poteze = []
        for i in range(VELIKOST_PLOSCE):
            for j in range(VELIKOST_PLOSCE):
                if self.plosca[i][j] is None:
                    if self.plosca[i+1][j] is None:
                        poteze.append((i,j,i+1,j))
                    elif self.plosca[i][j+1] is None:
                        poteze.append((i,j,i,j+1))
        return poteze

    def povleci_potezi(self, i, j):
        """Povleci_potezi(i,j) vrne stanje_igre() po potezi ali None, ce je poteza neveljavna."""
        if self.plosca[i][j] is not None:
            # neveljavna poteza
            return None
        else:
            if self.plosca[i+1][j] is None:
                p = self.na_potezi
                self.plosca[i][j] = self.na_potezi
                self.plosca[i+1][j] = self.na_potezi
                stanje = self.stanje_igre()
                if stanje == NI_KONEC:
                    # Igre ni konec, zdaj je na potezi nasprotnik
                    self.na_potezi = nasprotnik(self.na_potezi)
                else:
                    # Igre je konec
                    self.na_potezi = None
                return stanje
            elif self.plosca[i][j+1] is None:
                p = self.na_potezi
                self.plosca[i][j] = self.na_potezi
                self.plosca[i][j+1] = self.na_potezi
                stanje = self.stanje_igre()
                 if stanje == NI_KONEC:
                    # Igre ni konec, zdaj je na potezi nasprotnik
                    self.na_potezi = nasprotnik(self.na_potezi)
                else:
                    # Igre je konec
                    self.na_potezi = None
                return stanje

    def stanje_igre(self):
        """Ugotovi, kakšno je trenutno stanje igre. Vrne:
           - IGRALEC_RED, če je igre konec in je zmagal IGRALEC_RED
           - IGRALEC_BLUE, če je igre konec in je zmagal IGRALEC_BLUE
           - NI_KONEC, če igre še ni konec
        """
        
        for i in range(VELIKOST_PLOSCE):
            for j in range(VELIKOST_PLOSCE):
                if self.plosca[i][j] is None:
                    if self.plosca[i+1][j] is None:
                        # Našli smo prazni ploscici, igre ni konec
                        return NI_KONEC
                    elif self.plosca[i][j+1] is None:
                        # Našli smo prazni ploscici, igre ni konec
                        return NI_KONEC
                    else:
                        # Igre je konec
                        return p
                        


######################################################################
