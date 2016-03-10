import tkinter
import threading
import time
import argparse

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
        assert False, "nasprotnik: prepovedan nasprotnik"

class Igra():
    def __init__(self):
        self.plosca = []
        for i in range(VELIKOST_PLOSCE):
            self.plosca.append([NEPOKRITO for j in range(VELIKOST_PLOSCE)])
        self.na_potezi = IGRALEC_RED
        self.zgodovina = []

    def kopija_igre(self):
        """Vrne kopijo te igre."""
        k = Igra()
        k.plosca = [self.plosca[i][:] for i in range(VELIKOST_PLOSCE)]
        k.na_potezi = self.na_potezi
        k.zgodovina = self.zgodovina
        return k

    def zgodovina_igre(self):
        """Shrani trenutno stanje igre."""
        z_plosca = [self.plosca[i][:] for i in range(VELIKOST_PLOSCE)]
        z_na_potezi = self.na_potezi
        self.zgodovina.append((z_plosca, z_na_potezi))
        return z_na_potezi
 
    def veljavne_poteze(self):
        """Vrni seznam veljavnih potez."""
        veljavne = []
        for i in range(VELIKOST_PLOSCE):
            for j in range(VELIKOST_PLOSCE):
                if self.plosca[i][j] == NEPOKRITO:
                    if self.plosca[i+1][j] == NEPOKRITO:
                        veljavne.append((i,j,i+1,j))
                    elif self.plosca[i][j+1] == NEPOKRITO:
                        veljavne.append((i,j,i,j+1))
        return veljavne

    def naredi_potezo(self, pozicija1, pozicija2):
        """naredi_potezo(i1, j1, i2, j2) vrne stanje_igre() po potezi ali None, ce je poteza neveljavna."""
        (i1,j1) = pozicija1
        (i2,j2) = pozicija2
        self.veljavne_poteze()
        for i in veljavne_poteze():
            if (i == (i1, j1, i2, j2)) or (i == (i2, j2, i1, j1)): # Primerja povlečene poteze z veljavnimi.
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
        """Ugotovi, kakšno je trenutno stanje igre. Vrne:
           - IGRALEC_RED, če je igre konec in je zmagal IGRALEC_RED
           - IGRALEC_BLUE, če je igre konec in je zmagal IGRALEC_BLUE
           - NI_KONEC, če igre še ni konec """
        zmagovalec = self.na_potezi
        for i in range(VELIKOST_PLOSCE):
            for j in range(VELIKOST_PLOSCE):
                if self.plosca[i][j] == NEPOKRITO:
                    if self.plosca[i+1][j] == NEPOKRITO:
                        return NI_KONEC # Igre ni konec.
                    elif self.plosca[i][j+1] == NEPOKRITO:
                        return NI_KONEC # Igre ni konec.
                    else:
                        return zmagovalec # Igre je konec.

    
######################################################################
## Igralec računalnik

class Racunalnik():
    def __init__(self, gui, algoritem):
        self.gui = gui
        self.algoritem = algoritem
        self.vlakno = None # Vlakno, ki razmišlja.

    def igraj(self):
        """Igraj potezo, ki jo vrne algoritem."""
        # Naredimo vlakno, ki mu podamo *kopijo* igre (da ne bo zmedel GUIja).
        self.vlakno = threading.Thread(target=lambda: self.algoritem.izracunaj_potezo(self.gui.igra.kopija()))
        self.vlakno.start()
        while self.algoritem.poteza is None:
            time.sleep(0.1)
            if self.algoritem.poteza is not None:
                self.gui.povleci_potezo(self.algoritem.poteza)
                self.vlakno = None

    def prekini(self):
        """Prekinemo razmišljanje algortitma."""
        if self.vlakno is not None:
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
        self.koncaj = False

    def prekini(self):
        """Metoda, ki jo pokliče GUI, ker je uporabnik zaprl okno ali izbral novo igro."""
        self.koncaj = True

    def izracunaj_potezo(self, igra):
        """Izračunaj potezo za trenutno stanje dane igre."""
        self.koncaj = False
        self.igra = igra # Dobimo kopijo igre.
        self.kdo_sem = self.igra.na_potezi
        self.poteza = None
        (poteza, vrednost) = self.minimax(self.globina, True) # Poženemo minimax.
        if self.koncaj is False:
            self.poteza = poteza

    def vrednost_igre(self):
        """vrednost_igre() sešteje vrednosti vseh vrstic/stolpcev na plošči."""
        # Slovar, ki pove, koliko so vredne posamezne vrstice/stolpci, kjer je "p : v":
        # x je število nezasedenih polj v vrstici/stolpcu in y vrednost vrstice/stolpca.
        if VELIKOST_PLOSCE == 4:
            vrednosti_vrstic_stolpcev = {
                0 : Minimax.UTEZ,
                2 : Minimax.UTEZ//10,
                4 : 0,
                3 : -Minimax.UTEZ//10,
                1 : -Minimax.UTEZ
            }
        elif VELIKOST_PLOSCE == 6:
            vrednosti_vrstic_stolpcev = {
                0 : Minimax.UTEZ,
                2 : Minimax.UTEZ//10,
                4 : Minimax.UTEZ//100,
                6 : 0,
                5 : -Minimax.UTEZ//100,
                3 : -Minimax.UTEZ//10,
                1 : -Minimax.UTEZ
            }
        elif VELIKOST_PLOSCE == 8:  
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
        for i in range(VELIKOST_PLOSCE):
            for j in range(VELIKOST_PLOSCE):
                if self.igra.plosca[i][j] == NEPOKRITO:
                    p1 += 1
                elif self.igra.plosca[j][i] == NEPOKRITO:
                    p2 += 1
            vrednost += vrednosti_vrstic_stolpcev.get(p1) + vrednosti_vrstic_stolpcev.get(p2)
        return vrednost

    def minimax(self, globina, maksimiziramo):
        if self.koncaj is True:
            return (None, 0) # Igro prekinemo.
        rezultat = self.igra.stanje_igre()
        if (rezultat == IGRALEC_RED) or (rezultat == IGRALEC_BLUE): # Igre je konec, vrnemo njeno vrednost.
            if zmagovalec == self.kdo_sem:
                return (None, Minimax.ZMAGA)
            elif zmagovalec == nasprotnik(self.kdo_sem):
                return (None, -Minimax.ZMAGA)
        elif rezultat == NI_KONEC: # Igre ni konec.
            if globina == 0:
                return (None, self.vrednost_igre())  
            else:
                if maksimiziramo: # Maksimiziramo
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
#GUI
class Gui():
    #stranica kvadratka
    enota=75
    
    #spremenljivke
    nacin=1
    velikost=4
    tezavnost=2

    def __init__(self, master):

        # Če uporabnik zapre okno naj se poklice self.zapri_okno
        master.protocol("WM_DELETE_WINDOW", lambda: self.zapri_okno(master))
        
        # Glavni menu
        menu = tkinter.Menu(master)
        master.config(menu=menu) # Dodamo glavni menu v okno

        # Podmenu za izbiro načina igre
        menu_igra = tkinter.Menu(menu)
        menu.add_cascade(label="Igra", menu=menu_igra)
        menu_igra.add_command(label="Človek vs. računalniku", command=lambda: self.spremeni_nacin(master, 1))
        menu_igra.add_command(label="Človek vs. človeku", command=lambda: self.spremeni_nacin(master, 2))

        # Podmenu za izbiro velikosti
        menu_velikost = tkinter.Menu(menu)
        menu.add_cascade(label="Velikost", menu=menu_velikost)
        menu_velikost.add_command(label="4x4", command=lambda: self.spremeni_velikost(master, 4))
        menu_velikost.add_command(label="6x6", command=lambda: self.spremeni_velikost(master, 6))
        menu_velikost.add_command(label="8x8", command=lambda: self.spremeni_velikost(master, 8))

        # Podmenu za izbiro težavnosti
        menu_tezavnost = tkinter.Menu(menu)
        menu.add_cascade(label="Težavnost", menu=menu_tezavnost)
        menu_tezavnost.add_command(label="Težko", command=lambda: self.spremeni_tezavnost(master, 3))
        menu_tezavnost.add_command(label="Srednje", command=lambda: self.spremeni_tezavnost(master, 2))
        menu_tezavnost.add_command(label="Lahko", command=lambda: self.spremeni_tezavnost(master, 1))

        # Igralno območje
        self.ustvari_okno(master, Gui.velikost)

        # Črte na igralnem polju
        self.narisi_crte(Gui.velikost)

    def spremeni_nacin(self, master, nacin):
        Gui.nacin=nacin

    def spremeni_velikost(self, master, velikost):
        self.plosca.destroy()
        Gui.ustvari_okno(self, master, velikost)
        Gui.narisi_crte(self, velikost)
        Gui.velikost=velikost

    def spremeni_tezavnost(self, master, tezavnost):
        Gui.tezavnost=tezavnost

    def zapri_okno(self, master):
        """Ta metoda se pokliče, ko uporabnik zapre aplikacijo."""
        # Vlaknom, ki tečejo vzporedno, je treba sporočiti, da morajo
        # končati, sicer se bo okno zaprlo, aplikacija pa bo še vedno
        # delovala.
        #self.prekini_igralce()
        # Dejansko zapremo okno.
        master.destroy()

    def ustvari_okno(self, master, velikost):
        self.plosca=tkinter.Canvas(master, width=velikost*Gui.enota, height=velikost*Gui.enota, bg="AntiqueWhite1")
        self.plosca.grid(row=1, column=1)
        # Onemogoči resize
        master.resizable(0,0)

    def narisi_crte(self,velikost):
        """Nariši črte v igralnem polju"""
        d = Gui.enota
        for i in range(1, velikost):
            self.plosca.create_line(i*d, 0*d, i*d, velikost*d, fill="light slate grey", width=3)
            self.plosca.create_line(0*d, i*d, velikost*d, i*d, fill="light slate grey", width=3)

######################################################################
#GLAVNI PROGRAM
root = tkinter.Tk()
root.title("Cram")
aplikacija = Gui(root)
root.mainloop()
