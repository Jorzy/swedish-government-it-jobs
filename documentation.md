# IT, AI och RPA Jobbsökningsportal - Dokumentation

## Översikt

Denna uppdaterade jobbsökningsportal tillhandahåller en omfattande plattform för att hitta IT-, AI- och RPA-jobb i både Göteborg och Kungsbacka. Systemet har förbättrats för att använda JobTech API som primär datakälla med RapidAPI som backup, och inkluderar nu utökade jobbkategorier och platser.

## Huvudfunktioner

1. **Flera jobbkategorier**:
   - IT-jobb
   - AI-jobb
   - RPA-jobb (Robotic Process Automation)

2. **Flera platser**:
   - Göteborg
   - Kungsbacka

3. **Förbättrad filtrering**:
   - Filtrera efter jobbkategori (med flikar)
   - Filtrera efter arbetsgivare
   - Filtrera efter plats
   - Filtrera efter aktiva/utgångna annonser
   - Filtrera efter meningsfulla arbetsgivare
   - Sök i alla fält

4. **Konsultexkludering**:
   - Alla jobbannonser exkluderar automatiskt konsultuppdrag

5. **Markering av meningsfulla arbetsgivare**:
   - Visuell markering av jobb från meningsfulla organisationer
   - Möjlighet att filtrera för att endast visa meningsfulla arbetsgivare

6. **Automatiska uppdateringar**:
   - Dagliga uppdateringar via GitHub Actions
   - Manuellt uppdateringsalternativ

## Systemkomponenter

1. **Jobbskrapare** (`scripts/jobtech_job_scraper.py`):
   - Använder JobTech API som primär datakälla
   - Använder RapidAPI som backup (begränsad till en gång per vecka)
   - Söker efter jobb i flera kategorier och platser
   - Exkluderar konsultuppdrag
   - Markerar meningsfulla arbetsgivare

2. **Webbgränssnitt** (`index.html`):
   - Flikbaserat gränssnitt för olika jobbkategorier
   - Responsiv design för alla enheter
   - Avancerade filtreringsalternativ
   - Visuell markering av meningsfulla arbetsgivare

3. **GitHub Actions Workflow** (`.github/workflows/update-jobs.yml`):
   - Kör jobbskraparen dagligen
   - Uppdaterar jobbannonser automatiskt
   - Kan utlösas manuellt

## Installation och konfiguration

1. **GitHub Repository-konfiguration**:
   - Ladda upp alla filer till ditt GitHub-repository
   - Se till att repository-strukturen matchar de tillhandahållna filerna
   - Se till att `.github/workflows`-katalogen är korrekt uppladdad

2. **GitHub Pages-konfiguration**:
   - Aktivera GitHub Pages i dina repository-inställningar
   - Ställ in källan till huvudgrenen

3. **API-nyckel (Valfritt)**:
   - För RapidAPI-backup, uppdatera `RAPIDAPI_KEY`-variabeln i `scripts/jobtech_job_scraper.py`
   - JobTech API kräver ingen API-nyckel

## Användning

1. **Visa jobb**:
   - Navigera till webbplatsen
   - Använd flikarna för att växla mellan jobbkategorier
   - Använd filtren för att begränsa resultaten

2. **Uppdatera jobb**:
   - Jobb uppdateras automatiskt varje dag
   - Klicka på "Uppdatera nu"-knappen för omedelbara uppdateringar
   - Alternativt, utlös GitHub Actions-arbetsflödet manuellt

## Felsökning

1. **Inga jobb visas**:
   - Kontrollera om JSON-filerna finns i ditt repository
   - Verifiera att GitHub Actions-arbetsflödet körs korrekt
   - Kontrollera efter felmeddelanden i GitHub Actions-loggarna

2. **GitHub Actions-fel**:
   - Se till att repository har rätt behörigheter inställda
   - Kontrollera att arbetsflödesfilen är korrekt formaterad
   - Verifiera att Python-beroendena är korrekt installerade

## Framtida förbättringar

1. **Fler jobbkällor**:
   - Lägg till fler jobbkällor för omfattande täckning
   - Implementera fler specialiserade sökningar

2. **E-postaviseringar**:
   - Lägg till alternativ för e-postaviseringar när nya jobb publiceras

3. **Användarkonton**:
   - Låt användare spara favoritjobb
   - Tillhandahåll personliga jobbrekommendationer

## Kontakt

För eventuella problem eller förslag, vänligen öppna ett ärende på GitHub-repositoryt.
