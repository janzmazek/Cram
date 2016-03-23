import tkinter
import threading
import time
import argparse 

######################################################################
## Igra

RDECI = "rdeci"
MODRI = "modri"
NEPOKRITO = "belo"
NI_KONEC = "ni konec"

def nasprotnik(igralec):
    if igralec == RDECI:
        return MODRI
    elif igralec == MODRI:
        return RDECI
    else:
        assert False, "nasprotnik: prepovedan nasprotnik"

class Igra():
    def __init__(self, velikost):
        self.velikost = velikost
        self.plosca = []
        for i in range(self.velikost):
            self.plosca.append([NEPOKRITO for j in range(self.velikost)])
        self.na_potezi = RDECI
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
                    if self.plosca[i-1][j] == NEPOKRITO:
                        veljavne.append((i,j,i-1,j))
                    elif self.plosca[i][j-1] == NEPOKRITO:
                        veljavne.append((i,j,i,j-1))
        return veljavne

    def naredi_potezo(self, pozicija1, pozicija2):
        """Vrne kdo je naredil potezo in stanje igre po potezi oz. None, ce je poteza neveljavna."""
        (i1,j1) = pozicija1
        (i2,j2) = pozicija2
        veljavne = self.veljavne_poteze()
        for i in veljavne:
            if i == (i1, j1, i2, j2) or i == (i2, j2, i1, j1): # Primerja povlecene poteze z veljavnimi.
                self.plosca[i1][j1] = self.na_potezi
                self.plosca[i2][j2] = self.na_potezi
                self.zgodovina_igre()
                igralec = self.na_potezi
                stanje = self.stanje_igre()
                if stanje == NI_KONEC:
                    self.na_potezi = nasprotnik(self.na_potezi) # Igre ni konec.
                else:
                    self.na_potezi = None # Igre je konec.
                return (igralec, stanje)
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
        for i in range(self.velikost):
            for j in range(self.velikost):
                if self.plosca[i][j] == NEPOKRITO:
                    if self.plosca[i+1][j] == NEPOKRITO:
                        return NI_KONEC # Igre ni konec.
                    elif self.plosca[i][j+1] == NEPOKRITO:
                        return NI_KONEC # Igre ni konec.
                    else:
                        return self.na_potezi # Igre je konec.

    
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
                (pozicija1, pozicija2) = self.algoritem.poteza
                self.gui.naredi_potezo(pozicija1, pozicija2)
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
        """Glavna metoda minimax. Vrne potezo in njeno vrednost."""
        rezultat = self.igra.stanje_igre()
        if (rezultat == RDECI) or (rezultat == MODRI): # Igre je konec.
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
                        self.igra.naredi_potezo(pozicija1, pozicija2)
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
                        self.igra.naredi_potezo(pozicija1, pozicija2)
                        vrednost = self.minimax(globina-1, not maksimiziramo)[2]
                        (self.igra.plosca, self.igra.na_potezi) = self.igra.zgodovina.pop()
                        if vrednost < naj_vrednost:
                            naj_vrednost = vrednost
                            naj_poteza = p

                assert (naj_poteza is not None), "minimax: izračunana poteza je None"
                return (naj_poteza, naj_vrednost)
        else:
            assert False, "minimax: prepovedano stanje igre"
        if self.zapri:
            return (None, 0) # Igro prekinemo.
        
######################################################################
## Igralec človek

class Clovek():
    def __init__(self, gui):
        self.gui = gui
        self.poteza = None

    def igraj(self):
        # Smo na potezi. Zaenkrat ne naredimo nic, ampak
        # cakamo, da bo uporanik kliknil na ploščo.
        pass

    def prekini(self):
        # Clovek igorira prekinitev razmisljanja.
        pass

    def klik(self, pozicija1):
        self.poteza = pozicija1 # Zapise pozicijo1.
        
        
    def spust(self, pozicija2):
        if self.poteza:
            self.gui.naredi_potezo(self.poteza, pozicija2)
            self.poteza = None


######################################################################
#GUI

ENOTA = 75
POKRITO="rdeco/modro"
        
class Gui():

    def __init__(self, master):
        self.igra = None
        self.plosca = None
        self.rdeci = None # Rdeči igralec
        self.modri = None # Modri igralec
        self.nacin = 2
        self.velikost = 4
        self.tezavnost = 2
        
        # Če uporabnik zapre okno naj se poklice self.zapri_okno
        master.protocol("WM_DELETE_WINDOW", lambda: self.prekini_igro(master))
        
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

        self.pripravi_igro(master)

    def pripravi_igro(self, master):
        self.naredi_polje(master, self.velikost) # Igralno območje
        self.naredi_crte(self.velikost) # Črte na igralnem polju
        self.naredi_napis(master, "Dobrodošli v Cram!", self.velikost) # Napis
        self.plosca.bind("<Button-1>", self.plosca_klik) # Klik na plosco
        self.plosca.bind("<ButtonRelease-1>", self.plosca_spust) # Spust na plosci
        # Začnemo igro
        if self.nacin == 1:
            self.zacni_igro(Clovek(self), Racunalnik(self, Minimax(self.tezavnost)))
        elif self.nacin == 2:
            self.zacni_igro(Clovek(self), Clovek(self))
        else:
            assert False, "gui: neveljaven nacin"
        
    def zacni_igro(self, rdeci, modri):
        self.plosca.delete(POKRITO)
        self.igra = Igra(self.velikost)
        self.rdeci = rdeci
        self.modri = modri
        self.rdeci.igraj()
        
    def koncaj_igro(self, zmagovalec):
        self.naredi_napis("Zmagal je {0}.".format(zmagovalec))

    def prekini_igro(self, master):
        """Sporoci igralcem, da nehajo razmisljati in zapre okno."""
        if self.rdeci: self.rdeci.prekini()
        if self.modri: self.modri.prekini()
        master.destroy()

    def spremeni_nacin(self, master, nacin):
        self.nacin = nacin
        self.pripravi_igro(master)

    def spremeni_velikost(self, master, velikost):
        self.plosca.destroy()
        self.velikost = velikost
        self.pripravi_igro(master)

    def spremeni_tezavnost(self, master, tezavnost):
        self.tezavnost = tezavnost
        self.pripravi_igro(master)

    def naredi_polje(self, master, velikost):
        self.plosca = tkinter.Canvas(master, width=velikost*ENOTA, height=velikost*ENOTA, bg="AntiqueWhite1")
        self.plosca.grid(row=1, column=1)
        # Onemogoči resize
        master.resizable(0,0)

    def naredi_crte(self, velikost):
        d = ENOTA
        for i in range(1, velikost):
            self.plosca.create_line(i*d, 0*d, i*d, velikost*d, fill="light slate grey", width=3)
            self.plosca.create_line(0*d, i*d, velikost*d, i*d, fill="light slate grey", width=3)

    def naredi_napis(self, master, vrednost, velikost):
        napis = tkinter.StringVar(master, value = vrednost)
        tkinter.Label(master, textvariable = napis).grid(row = velikost + 1, column = 1)

    def plosca_klik(self, event):
        """Obdela klike na plosco."""
        i1 = event.x // ENOTA
        j1 = event.y // ENOTA
        if self.igra.na_potezi == RDECI:
            self.rdeci.klik((i1,j1)) # Rdeci dobi pozicijo1. 
        elif self.igra.na_potezi == MODRI:
            self.modri.klik((i1,j1)) # Modri dobi pozicijo1.
        else:
            pass
        print("Kliknil si na ({0},{1})".format(i1,j1))

    def plosca_spust(self, event):
        """Obdela spuste na plosco."""
        i2 = event.x // ENOTA
        j2 = event.y // ENOTA
        if self.igra.na_potezi == RDECI:
            print("Spustil si na ({0},{1})".format(i2,j2))
            self.rdeci.spust((i2,j2)) # Rdeci dobi pozicijo2. 
        elif self.igra.na_potezi == MODRI:
            self.modri.spust((i2,j2)) # Modri dobi pozicijo2.
        else:
            pass
        print("Spustil si na ({0},{1})".format(i2,j2))

    def pobarvaj_rdece(self, x, y):
        self.plosca.create_rectangle(x*ENOTA, y*ENOTA, (x+1)*ENOTA, (y+1)*ENOTA, fill="red", tag=POKRITO)
        
    def pobarvaj_modro(self, x, y):
        self.plosca.create_rectangle(x*ENOTA, y*ENOTA, (x+1)*ENOTA, (y+1)*ENOTA, fill="blue", tag=POKRITO)

    def naredi_potezo(self, pozicija1, pozicija2):
        """Naredi potezo 1 (klik) in 2 (spust). Ce je neveljavna, ne naredi nic."""
        # Logika igre je v self.igra.
        (igralec, stanje) = self.igra.naredi_potezo(pozicija1, pozicija2)
        if (igralec, stanje): # Narisemo potezo.
            if igralec == RDECI:
                self.pobarvaj_rdece(pozicija1, pozicija2) # Pobarva rdece.
            elif igralec == MODRI:
                self.pobarvaj_modro(pozicija1, pozicija2) # Pobarva modro.
            # Preveri stanje igre.
            if stanje == NI_KONEC: # Igra se nadaljuje.
                if self.igra.na_potezi == RDECI:
                    self.naredi_napis("Na potezi je rdeči igralec.")
                    self.rdeci.igraj()
                elif self.igra.na_potezi == MODRI:
                    self.naredi_napis("Na potezi je modri igralec.")
                    self.modri.igraj()
            else: # Igre je konec.
                self.koncaj_igro(stanje)
        else: # Neveljavna poteza.
            pass
        
######################################################################
#GLAVNI PROGRAM
        
root = tkinter.Tk()
root.title("Cram")
aplikacija = Gui(root)
root.mainloop()
