# Vizualni slog, izpeljava koncepta, anti-slop

## Privzeti slog: konceptualna uredniška fotografija

En sam resničen, fizičen motiv, posnet kot naslovnica resne poslovne revije (Economist, Bloomberg Businessweek, HBR, MIT Sloan). Značilnosti:

- **En motiv, en fokus.** Ne kolaž, ne scena z desetimi elementi. Slika ima eno točko, kamor gre oko.
- **Disciplinirana paleta.** Nadzorovan kontrast, ena restriktivna poudarna barva (po znamki - glej spodaj), sicer nevtralno. Nič mavričnih gradientov.
- **Veliko negativnega prostora.** ≥ 35 % praznine na eni strani (levo ali desno) za naknadni overlay naslova. Negativni prostor je del koncepta, ne ostanek.
- **Naravna ali nadzorovano studijska svetloba.** Eno-virna, usmerjena, z mehkimi sencami.
- **Fotografska resničnost.** Bere se kot posnetek, ne kot 3D render ali vektorska ilustracija.

Register je premišljen, ne dobeseden. Slika ima napetost, ne pojasnila.

## Voltaža: feed ni revija

Uredniška zadržanost je protistrup proti AI slopu - ni pa dovoljenje za nizko napetost. Tiha, subtilna absurdnost dela na naslovnici revije, kjer bralec že gleda. V feedu ima slika pol sekunde proti vsemu šumu okoli sebe. Zadržan **slog** in zadržana **napetost** nista isto: slog ostane miren, anomalija pa mora biti glasna.

Privzeti vzvodi visoke voltaže (izberi vsaj enega, kadar je cilj feed/og:image):

- **Človeški obraz** - najmočnejši magnet za oko; resen, ocenjujoč izraz ob nemogoči situaciji (deadpan) proda tezo bolje kot katerikoli predmet sam. Stopnjevanje: **Igorjev lastni obraz** (prek referenčne fotografije, pravila v razdelku o ljudeh) za publiko, ki ga pozna, ustavi scroll pred dekodiranjem prizora - najmočnejša različica tega vzvoda, posebej za LinkedIn.
- **Nemogoča situacija, odigrana resno** - razgovor za službo z zvezkom, sestanek s praznim stolom, ki ima priponko.
- **Nemogoče merilo** - predmet absurdno velik/majhen za svoj kontekst.
- **Kričeča anomalija v redu** - vrsta enakih elementov, eden nemogoč.
- **Številka kot anomalija** - funkcionalni mikro-tekst (cenovna oznaka, znesek), ki sam nosi tezo; npr. dva enaka predmeta z dvema cenama. Najhitrejše branje od vseh vzvodov, a veže pogoje iz pravila o mikro-tekstu (SKILL.md). Modeli kratke, dobesedno navedene napise rišejo zanesljivo; v promptu jih zapiši v narekovajih, vse drugo besedilo pa izrecno prepovej.
- **Resnični artefakt** - pravi screenshot, dokument ali graf ima avtentičnost, ki je generirana slika nima; poslovni bralec se pri dokumentu ustavi. A pokaže navadno le premiso, ne obrata teze, drobni tekst pri og:image velikosti umre, tuj UI pa odpira vprašanja pravic. Privzeto ga uporabi kot sliko **v članku**, kot key visual le, če je artefakt sam po sebi šokanten in berljiv v sličici.

Test voltaže: »pameten, ko ga pogledaš« ni dovolj - vprašaj se, ali slika *prisili* pogled. Koncepti s tiho duhovitostjo (predmet rahlo narobe, brez človeka) so legitimni za slike **v članku**, ne za key visual v feedu.

## Thumbnail test (obvezen)

Key visual se v feedu odloči pri ~120 px širine na telefonu. Koncept, ki dela na 1200 px in umre v sličici, ni scroll stopper. Pred izborom koncepta preveri:

- **Silhueta:** ali je motiv prepoznaven kot črna silhueta na svetlem polju (ali obratno)? Če potrebuje detajl, da ga razumeš, pade.
- **Kontrast:** ena velika svetlostna razlika (temno/svetlo), ne deset majhnih.
- **Štetje elementov:** v sličici naj bo berljiv natanko en element. Dva sta že gneča.

Koncept, ki pade na thumbnail testu, zavrzi ali poenostavi - tudi če je metafora pametna.

## Ljudje v kadru

Obrazi so najmočnejši zaustavljalec scrolla - uredniške naslovnice jih uporabljajo namerno. Ljudje so **dovoljeni in pogosto zaželeni**, z varovali:

### Igor kot avtor v kadru (poseben vzvod)

Igorjev obraz je njegov podpis: avatar na kolumnah, LinkedIn prisotnost, odri in webinarji v regiji. Za publiko, ki ga pozna, prepoznaven avtor ustavi scroll *pred* dekodiranjem prizora - to je voltaža, ki je noben generiran obraz ne doseže, in hkrati avtentičnost (avtor stoji za tezo dobesedno).

- Kdaj ponuditi: pri kolumnah z osebnim hookom v prvi osebi in pri vizualih, ki gredo primarno na **LinkedIn** (tam je obraz = byline). Ponudi kot varianto ob brezosebnem konceptu, ne kot edino pot.
- Kako: prek **referenčne slike** - Igor priloži svojo fotografijo, Nano Banana ga umesti v prizor (»place the person from the reference photo in …«); tudi ChatGPT sprejme priloženo fotografijo. Brez referenčne fotografije Igorja nikoli ne generiraj po opisu.
- Ista pravila kot za vse: deadpan, v prizoru (ne komentira prizora s prezentersko gesto), en fokus, thumbnail test - tudi znan obraz mora biti pri 120 px prepoznaven, kar pomeni dovolj velik v kadru in brez tekmujočih con.
- Verifikacija podobnosti: pred objavo naj podobnost potrdi nekdo, ki Igorja dobro pozna (avtor je slab sodnik lastnega obraza). »Skoraj podoben« je slabše od generičnega obraza - dolina med »Igor« in »nekdo podoben Igorju« zbode ravno bralce, ki ga poznajo.
- Velja izključno za Igorja (lastna podoba, lastna privolitev). Nobene druge resnične osebe, nikoli.

### Generirane osebe

- Generična oseba, nikoli resnična ali prepoznavna; brez podobnosti z javnimi osebami.
- En človek, ne skupina. Skupina = stock.
- Gesta ali pogled nosi napetost teze (odvrnjen pogled, čakanje, ignoriranje), ne poziranje. **Izraz je nosilni element:** pri konceptih z nemogočo situacijo deadpan resnost proda tezo - nasmeh, kažoči prsti ali »prezenterska« poza isti prizor spremenijo v stock fotografijo. V prompt zato vedno zapiši izraz eksplicitno (»calm, serious, matter-of-fact expression«), pri dveh osebah za vsako posebej.
- Pogled naravnost v kamero je legitimen dodatni zaustavljalec - očesni stik v feedu deluje; uporabi ga, kadar kompozicija prenese.
- Roke: enostavne drže (na mizi, v žepu, ob telefonu), ne prepleteni prsti - modeli tam grešijo.
- Če koncept deluje enako močno brez človeka, vzemi različico brez - manj tveganja pri generiranju.

## Metoda izpeljave koncepta

Vizual ne ilustrira **teme**, nosi **tezo**. Postopek:

1. Vzemi tezo (kontraintuitivno trditev kolumne).
2. Vprašaj: katera *napetost* je v tej tezi? (zanemarjeno vredno / prazno tam, kjer bi moralo biti polno / drago, kar tretiramo kot poceni / red, ki skriva nered / nagrada, ki kaznuje …)
3. Najdi **fizičen objekt, prizor ali gesto**, ki to napetost utelesi - lateralno, ne dobesedno.
4. Test dobesednosti: če je motiv očiten prevod teme v sliko (»AI« → robot, »rast« → graf navzgor, »povezovanje« → roke v krogu), zavrzi. Lateralno premakni.
5. **Test robustnosti:** ali anomalija preživi nenatančno izvedbo? Generativni model poze, drže in orientacije pogosto zgreši. Če poanta stoji na natančni pozi ali postavitvi (»zvezek sedi kot človek«, »pogled je obrnjen točno tja«), je koncept krhek - ena površna generacija ga spremeni v navaden prizor. Anomalija mora biti v tem, **kaj** je v kadru (napačen predmet na pravem mestu, predmet z atributom, ki mu ne pripada), ne v tem, **kako** je postavljeno. Krhek koncept ojačaj z nezgrešljivim atributom (npr. predmet »nosi« priponko, vozel na vrvici, prevrnjen element v vrsti enakih) ali ga zavrzi.
6. Thumbnail test (zgoraj).

### Mini primeri izpeljave (ilustrativni - različne napetosti, ne predloge motivov)

**A - zanemarjeno vredno.** Teza: klic, ki ga ne dvignete, je vaš najdražji izgubljen kanal. Napetost: najdražje vstopno mesto tretiramo kot najcenejše. Dobesedno (zavrzi): klicni center s slušalkami. Lateralno: bankovec za 100 €, zataknjen pod nogo pisarniške mize, da ne maje - vrednost, uporabljena kot podloga. Thumbnail: zelena lisa na nevtralnem polju, bere se.

**B - nagrada, ki kaznuje.** Teza: akcije za nove kupce kaznujejo zveste stranke. Napetost: lojalnost se splača manj kot nezvestoba. Dobesedno (zavrzi): dva kupca, eden z darilom. Lateralno: dve enaki kavi na pultu, ena z elegantno zapisano nižjo ceno na kartončku - fotografirano hladno, simetrično, da asimetrija cene zbode. Thumbnail: dva enaka objekta, ena anomalija - bere se.

**C - red, ki skriva nered (s človekom).** Teza: urejen CRM dashboard skriva razpadajočo prodajo. Napetost: gladka površina, gnilo jedro. Lateralno: oseba s hrbtom proti nam zaliva eno samo popolno umetno rastlino v sicer prazni pisarni. Gesta nosi absurd. Thumbnail: ena figura + ena rastlina, visok kontrast - bere se.

**D - strukturna/številčna teza → preklop na grafični poster.** Teza: 8,5 % opuščenih klicev pomeni vsak dvanajsti gost izgubljen. Napetost je v razmerju, ne v prizoru. Fotografija razmerja ne nosi → grafični poster: dvanajst enakih stolov v vrsti na ravni barvni ploskvi, eden prazen-prevrnjen. Še vedno brez teksta, še vedno negativni prostor.

Primeri so kalibracija metode. Ne recikliraj njihovih motivov - izpelji svežega iz konkretne teze.

## Anti-slop seznam - interni filter, NE za v prompt

Ti elementi bralcu signalizirajo »AI, preskoči«. Seznam uporabi kot **kontrolni filter koncepta in prompta** - če se kateri element pojavlja v tvojem konceptu ali formulaciji, popravi koncept. V sam prompt seznama NE prilepljaj v celoti (dolgi »avoid« seznami pri generativnih modelih znajo priklicati ravno naštete elemente); v prompt gre le kratka omejitvena vrstica (glej prompt-recipes.md).

- moder/cijan sij, hologrami, »glowing« vmesniki
- roboti, androidi, robotska roka
- nevronska mreža, vezje-možgani, »data streams«, binarni dež
- lebdeči prosojni UI paneli, plavajoče ikone, HUD grafika
- generičen stisk rok, ekipa ob mizi, poslovnež zre v mesto ob sončnem vzhodu
- teal-and-orange gradient, mavrični prelivi, neon
- bleski, »lens flare«, pretirana bokeh megla
- plastičen 3D render videz (razen pri namernem grafičnem posterju)
- stock-kolažni občutek, vodni žigi, logotipi
- tekst, napisi, številke v sliki - razen funkcionalnega mikro-teksta, ki je sam anomalija (pravila v SKILL.md); dekorativni napisi nikoli
- prepleteni prsti, kompleksne drže rok

## Kompozicija za 1.91:1 (1200×630)

- Fokus po pravilu tretjin, **ne** na sredini; nasprotna stran ostane prazna za naslov.
- Eye-level ali rahel kot; ekstremna perspektiva le, če jo koncept zahteva.
- Srednja do plitka globinska ostrina; ozadje podpira, ne tekmuje.
- En vir svetlobe; sence so del kompozicije.
- Prazna stran naj bo zares prazna (gladka stena, megla, barvna ploskev), ne »skoraj prazna«.

## Palete po znamkah

Kolumna lahko meri na eno od treh znamk družine FrodX. Paleto izberi glede na temo. Vedno velja: ena restriktivna poudarna barva na samem motivu, sicer nevtralno polje.

| Znamka | Status | Poudarna barva | Register / ton |
|---|---|---|---|
| **FrodX** (privzeto) | **zaklenjeno** | **#2465C9** (modra) + črna | uredniško-korporativen, resen; črn/ogljen motiv, modra kot edini poudarek na belem ali temno nevtralnem polju |
| **Kinetara** | **zaklenjeno** | **monokromno: črna** na beli/svetli podlagi (logotip je namerno enobarven) | topel, empatičen, glasovni/človeški; voice AI, »missed call«; vizuali brez barvnega poudarka - črn/temen motiv na svetlem nevtralnem polju, kontrast nosi svetloba, ne barva; dovoljen tudi povsem črno-bel fotografski videz |
| **InstantFeedback** | **zaklenjeno** | **#00A4BD** (teal) + **#D564C4** (magenta); besedilo #374147 | svetel, podatkovno-dashboard, moderni SaaS; teal primarni, magenta drugi pop |

Vir barv: FrodX iz logotipa (#2465C9 + črna); InstantFeedback iz logotipa (teal #00A4BD + magenta #D564C4 - meta theme-color #0891b2 je le UI odtenek); Kinetara po Igorjevi potrditvi (logotip je namerno enobarven - črn na svetlem). Vse tri palete so zaklenjene. Ne izmišljaj si barv.

### Logika izbire palete (po temi)

- Tema o **Kinetari**, glasovnih agentih, missed-call, voice AI → Kinetara paleta. Ref: `kinetara.ai`.
- Tema o **InstantFeedbacku**, povratnih informacijah, NPS/CSAT, response rate → InstantFeedback. Ref: `getinstantfeedback.com`.
- Vse ostalo (CX, CRM, HubSpot, SAP, loyalty, prodaja, splošna AI transformacija) → **FrodX privzetek**. Ref: `frodx.com`.

Pri mejni temi (npr. Kinetara case v splošni CX kolumni na FrodX blogu) privzemi FrodX in v izhodu ponudi Kinetara paleto kot alternativo.

## Kdaj odkloniti na grafični poster

Ko je teza **strukturna ali številčna** (cena, razmerje, sistem - primer D zgoraj), uredniška fotografija lahko zataji. Tedaj preklopi na **krepek grafični poster**: en objekt ali ponavljajoč vzorec z eno anomalijo na ravni barvni ploskvi znamke, plakatni kontrast, še vedno čist (brez teksta), še vedno negativni prostor. Anti-slop filter in thumbnail test veljata enako. V izhodu povej, da si odklonil in zakaj.
