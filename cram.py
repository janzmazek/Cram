import tkinter
import threading
import time
import argparse 

######################################################################
## Igra

RDECI = "rdeci"
MODRI = "modri"
NEPOKRITO = "belo"
KONEC = "konec"
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
        k = Igra(self.velikost)
        k.plosca = [self.plosca[i][:] for i in range(self.velikost)]
        k.na_potezi = self.na_potezi
        k.zgodovina = self.zgodovina
        return k

    def zgodovina_igre(self):
        """Shrani trenutno stanje igre."""
        plosca_prej = [self.plosca[i][:] for i in range(self.velikost)]
        na_potezi_prej = self.na_potezi
        self.zgodovina = (plosca_prej, na_potezi_prej)
        return plosca_prej
 
    def veljavne_poteze(self):
        """Vrne seznam veljavnih potez."""
        veljavne = []
        for i in range(self.velikost):
            for j in range(self.velikost):
                if self.plosca[i][j] == NEPOKRITO:
                    if i+1 < self.velikost and self.plosca[i+1][j] == NEPOKRITO:
                        veljavne.append((i,j,i+1,j))
                        veljavne.append((i+1,j,i,j))
                    if j+1 < self.velikost and self.plosca[i][j+1] == NEPOKRITO:
                        veljavne.append((i,j,i,j+1))
                        veljavne.append((i,j+1,i,j))
        return veljavne

    def naredi_potezo(self, x1, y1, x2, y2):
        """Preveri, če je poteza veljavna. Vrne kdo je naredil potezo in stanje po potezi oz. None, če je neveljavna."""
        poteza = (x1, y1, x2, y2)
        veljavne = self.veljavne_poteze()
        for i in range(len(veljavne)):
            # Primerja povlecene poteze z veljavnimi.
            if veljavne[i] == poteza:
                self.zgodovina_igre()
                self.plosca[x1][y1] = self.na_potezi
                self.plosca[x2][y2] = self.na_potezi
                igralec = self.na_potezi
                stanje = self.stanje_igre()
                if stanje == NI_KONEC:
                    self.na_potezi = nasprotnik(self.na_potezi) # Igre ni konec.
                return (igralec, stanje)
        return (self.na_potezi, None) # Če ne najde veljavne poteze.

    def stanje_igre(self):
        """Preveri stanje igre."""
        stanje = KONEC
        for i in range(self.velikost):
            for j in range(self.velikost):
                if self.plosca[i][j] == NEPOKRITO:
                    if i+1 < self.velikost and self.plosca[i+1][j] == NEPOKRITO:
                        stanje = NI_KONEC # Igre ni konec.
                    if j+1 < self.velikost and self.plosca[i][j+1] == NEPOKRITO:
                        stanje = NI_KONEC # Igre ni konec.
        return stanje

    
######################################################################
## Igralec racunalnik

class Racunalnik():
    def __init__(self, gui, algoritem):
        self.gui = gui
        self.algoritem = algoritem
        self.vlakno = None # Vlakno, ki razmislja.

    def igraj(self):
        """Igra potezo, ki jo vrne algoritem."""
        # Naredimo vlakno, ki mu podamo kopijo igre.
        self.vlakno = threading.Thread(target=lambda: self.algoritem.izracunaj_potezo(self.gui.igra.kopija_igre()))
        self.vlakno.start()
        while self.algoritem.poteza is None:
            time.sleep(0.3) # Pocaka 300ms.
            if self.algoritem.poteza: # Algoritem je nasel potezo.
                (x1, y1, x2, y2) = self.algoritem.poteza
                self.gui.naredi_potezo(x1, y1, x2, y2)
                self.vlakno = None
            if self.algoritem.prekini: # Razmislanje je prekinjeno.
                break

    def prekini(self):
        """Prekinemo razmisljanje algortitma."""
        if self.vlakno:
            self.algoritem.koncaj()
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
        self.prekini = False

    def koncaj(self):
        """Metoda, ki jo pokliče GUI, ker je uporabnik zaprl okno ali izbral novo igro."""
        self.prekini = True

    def izracunaj_potezo(self, igra):
        """Izračuna potezo za trenutno stanje dane igre."""
        self.igra = igra # Dobimo kopijo igre.
        self.kdo_sem = self.igra.na_potezi
        self.poteza = None
        poteza = self.minimax(self.globina, True)[0] # Pozenemo minimax.
        if self.prekini is False:
            self.poteza = poteza

    def vrednost_igre(self):
        """vrednost_igre() sešteje vrednosti vseh vrstic/stolpcev na plošči."""
        # Slovar, ki pove, koliko so vredne posamezne vrstice/stolpci, kjer je "p : v":
        # x je stevilo nezasedenih polj v vrstici/stolpcu in y vrednost vrstice/stolpca.
        if self.igra.velikost == 4: # Ce je igralno polje velikosti 4x4.
            vrednosti_vrstic_stolpcev = {
                0 : UTEZ,
                2 : UTEZ//10,
                4 : 0,
                3 : -UTEZ//10,
                1 : -UTEZ
            }
        elif self.igra.velikost == 6: # Ce je igralno polje velikosti 6x6.
            vrednosti_vrstic_stolpcev = {
                0 : UTEZ,
                2 : UTEZ//10,
                4 : UTEZ//100,
                6 : 0,
                5 : -UTEZ//100,
                3 : -UTEZ//10,
                1 : -UTEZ
            }
        elif self.igra.velikost == 8: # Ce je igralno polje velikosti 8x8.
            vrednosti_vrstic_stolpcev = {
                0 : UTEZ,
                2 : UTEZ//10,
                4 : UTEZ//100,
                6 : UTEZ//1000,
                8 : 0,
                7 : -UTEZ//1000,
                5 : -UTEZ//100,
                3 : -UTEZ//10,
                1 : -UTEZ
            }   
        vrednost = 0
        p1 = 0
        p2 = 0
        for i in range(self.igra.velikost):
            for j in range(self.igra.velikost):
                if self.igra.plosca[i][j] == NEPOKRITO:
                    p1 += 1
                if self.igra.plosca[j][i] == NEPOKRITO:
                    p2 += 1        
            vrednost = vrednost + vrednosti_vrstic_stolpcev.get(p1,0) + vrednosti_vrstic_stolpcev.get(p2,0)
        return vrednost

    def minimax(self, globina, maksimiziramo):
        """Glavna metoda minimax. Vrne potezo in njeno vrednost."""
        # Igro prekinemo.
        if self.prekini is True:
            return (None, None)     
        stanje_minimax = self.igra.stanje_igre()
        igralec_minimax = self.igra.na_potezi
        # Igre je konec.
        if stanje_minimax == KONEC: 
            if igralec_minimax == self.kdo_sem:
                return (None, UTEZ)
            elif igralec_minimax == nasprotnik(self.kdo_sem):
                return (None, -UTEZ)
        # Igre ni konec.
        elif stanje_minimax == NI_KONEC: 
            if globina == 0: # Zmanjkalo globine.
                return (None, self.vrednost_igre())
            else:
                globina -=1
                if maksimiziramo:  # Maksimiziramo
                    naj_poteza = None
                    naj_vrednost = -NESKONCNO
                    veljavne = self.igra.veljavne_poteze()
                    for p in range(len(veljavne)):
                        (x1, y1, x2, y2) = veljavne[p]
                        stanje_max = self.igra.naredi_potezo(x1, y1, x2, y2)[1]
                        zgodovina_max = self.igra.zgodovina
                        vrednost = self.minimax(globina, not maksimiziramo)[1]
                        (self.igra.plosca, self.igra.na_potezi) = zgodovina_max  
                        if vrednost > naj_vrednost:
                            naj_vrednost = vrednost
                            naj_poteza = veljavne[p]
                            
                else: # Minimiziramo
                    naj_poteza = None
                    naj_vrednost = NESKONCNO
                    veljavne = self.igra.veljavne_poteze()
                    for p in range(len(veljavne)):
                        (x1, y1, x2, y2) = veljavne[p]
                        stanje_mini = self.igra.naredi_potezo(x1, y1, x2, y2)[1]
                        zgodovina_mini = self.igra.zgodovina
                        vrednost = self.minimax(globina, not maksimiziramo)[1]
                        (self.igra.plosca, self.igra.na_potezi) = zgodovina_mini
                        if vrednost < naj_vrednost:
                            naj_vrednost = vrednost
                            naj_poteza = veljavne[p]      
 
                return (naj_poteza, naj_vrednost)
        
        
#####################################################################
## Algoritem alfa-beta
            
######################################################################
## Igralec človek

class Clovek():
    def __init__(self, gui):
        self.gui = gui
        self.pozicija = None

    def igraj(self):
        # Smo na potezi. Zaenkrat ne naredimo nic, ampak
        # cakamo, da bo uporanik kliknil na ploščo.
        pass

    def prekini(self):
        # Clovek igorira prekinitev razmisljanja.
        pass

    def klik(self, pozicija1):
        self.pozicija = pozicija1 # Zapise pozicijo1.
        
    def spust(self, pozicija2):
        if self.pozicija:
            self.gui.naredi_potezo(self.pozicija[0], self.pozicija[1], pozicija2[0], pozicija2[1])
            self.pozicija = None


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
        self.nacin = 1
        self.velikost = 4
        self.tezavnost = 2
        
        # Če uporabnik zapre okno.
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

        self.napis = tkinter.StringVar(master, value = "Dobrodošli!")
        tkinter.Label(master, textvariable = self.napis).grid(row = self.velikost + 1, column = 1)
        
        self.pripravi_igro(master)

    def pripravi_igro(self, master):
        self.naredi_polje(master, self.velikost) # Igralno območje
        self.naredi_crte(self.velikost) # Črte na igralnem polju
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
        self.napis.set("Dobrodošli v Cram! Igra je pripravljena in ste na potezi.")
        self.rdeci.igraj()
        
    def koncaj_igro(self, zmagovalec):
        self.napis.set("Zmagal je {0}.".format(zmagovalec))

    def prekini_igro(self, master):
        """Sporoci igralcem, da nehajo razmisljati in zapre okno."""
        self.rdeci.prekini()
        self.modri.prekini()
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
        master.resizable(0,0) # Onemogoči resize.

    def naredi_crte(self, velikost):
        d = ENOTA
        for i in range(1, velikost):
            self.plosca.create_line(i*d, 0*d, i*d, velikost*d, fill="light slate grey", width=3)
            self.plosca.create_line(0*d, i*d, velikost*d, i*d, fill="light slate grey", width=3)

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

    def plosca_spust(self, event):
        """Obdela spuste na plosco."""
        i2 = event.x // ENOTA
        j2 = event.y // ENOTA
        if self.igra.na_potezi == RDECI:
            self.rdeci.spust((i2,j2)) # Rdeci dobi pozicijo2. 
        elif self.igra.na_potezi == MODRI:
            self.modri.spust((i2,j2)) # Modri dobi pozicijo2.
        else:
            pass

    def pobarvaj_rdece(self, x1, y1, x2, y2):
        self.plosca.create_rectangle(x1*ENOTA, y1*ENOTA, (x1+1)*ENOTA, (y1+1)*ENOTA, fill="red", tag=POKRITO)
        self.plosca.create_rectangle(x2*ENOTA, y2*ENOTA, (x2+1)*ENOTA, (y2+1)*ENOTA, fill="red", tag=POKRITO)
        
    def pobarvaj_modro(self, x1, y1, x2, y2):
        self.plosca.create_rectangle(x1*ENOTA, y1*ENOTA, (x1+1)*ENOTA, (y1+1)*ENOTA, fill="blue", tag=POKRITO)
        self.plosca.create_rectangle(x2*ENOTA, y2*ENOTA, (x2+1)*ENOTA, (y2+1)*ENOTA, fill="blue", tag=POKRITO)

    def naredi_potezo(self, x1, y1, x2, y2):
        """Naredi potezo 1 (klik) in 2 (spust). Ce je neveljavna, ne naredi nic."""
        (igralec, stanje) = self.igra.naredi_potezo(x1, y1, x2, y2)
        if stanje is not None: # Narisemo potezo.
            if igralec == RDECI:
                self.pobarvaj_rdece(x1, y1, x2, y2) # Pobarva rdece.
            elif igralec == MODRI:
                self.pobarvaj_modro(x1, y1, x2, y2) # Pobarva modro.
            if stanje == NI_KONEC: # Igra se nadaljuje.
                if self.igra.na_potezi == RDECI:
                    self.napis.set("Na potezi je rdeči igralec.")
                    self.rdeci.igraj()
                elif self.igra.na_potezi == MODRI:
                    self.napis.set("Na potezi je modri igralec.")
                    self.modri.igraj()
            else: # Igre je konec.
                self.koncaj_igro(igralec)
        else: # Neveljavna poteza.
            pass
        
######################################################################
#GLAVNI PROGRAM
        
root = tkinter.Tk()
root.title("Cram")
aplikacija = Gui(root)
root.mainloop()
