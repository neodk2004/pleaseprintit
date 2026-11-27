"""Übersetzungen ohne Zusatzpaket: Schlüssel ist der deutsche Text, dazu (Englisch, Französisch).
Fehlt ein Eintrag, erscheint der deutsche Text. test_i18n.py prüft, dass jeder _()/t()-Text hier steht.
Neue Sprache: Kürzel in LANGS ergänzen und jedem Eintrag eine weitere Spalte geben."""

LANGS = {"de": "Deutsch", "en": "English", "fr": "Français"}
DEFAULT = "de"

T = {
    # --- Allgemein, Navigation ---
    "Zum Inhalt": ("Skip to content", "Aller au contenu"),
    "PleasePrintit – Startseite": ("PleasePrintit – home", "PleasePrintit – accueil"),
    "Hauptmenü": ("Main menu", "Menu principal"),
    "Werkstatt": ("Workshop", "Atelier"),
    "Aufträge": ("Requests", "Demandes"),
    "Freunde": ("Friends", "Amis"),
    "Einstellungen": ("Settings", "Réglages"),
    "Profil": ("Profile", "Profil"),
    "Hell/Dunkel umschalten": ("Toggle light/dark", "Basculer clair/sombre"),
    "Abmelden": ("Sign out", "Se déconnecter"),
    "Privat, nur für Freunde": ("Private, friends only", "Privé, réservé aux amis"),
    "Impressum": ("Legal notice", "Mentions légales"),
    "Datenschutz": ("Privacy", "Confidentialité"),
    "Sprache": ("Language", "Langue"),
    "Vorschau": ("Preview", "Aperçu"),
    "Ein 3D-Drucker druckt ein Herz": ("A 3D printer printing a heart", "Une imprimante 3D imprime un cœur"),
    "Traurig": ("Sad", "Triste"),
    "Ablauf": ("Progress", "Étapes"),
    "Zurück": ("Back", "Retour"),
    "Rechtliches": ("Legal", "Informations légales"),
    "Speichern": ("Save", "Enregistrer"),
    # --- Mail an die Werkstatt bei neuem Auftrag ---
    "Benachrichtigung": ("Notification", "Notification"),
    "Deine Adresse für eine Mail, sobald ein Freund einen Druckwunsch einreicht oder eine Rückfrage schreibt. Leer = keine Mails.":
        ("Your address for an e-mail whenever a friend submits a print request or asks a question. Empty = no e-mails.",
         "Ton adresse pour recevoir un e-mail dès qu'un ami envoie une demande d'impression ou pose une question. Vide = pas d'e-mails."),
    "Mails pausieren (Adresse bleibt gespeichert)": ("Pause e-mails (address stays saved)",
                                                     "Mettre les e-mails en pause (l'adresse reste enregistrée)"),
    "Dafür muss der Mailversand in der .env eingerichtet sein.":
        ("This requires e-mail sending to be set up in the .env file.",
         "Pour cela, l'envoi d'e-mails doit être configuré dans le fichier .env."),
    # --- Push-Nachricht an die Werkstatt über ntfy ---
    "Push-Nachricht über ntfy": ("Push notification via ntfy", "Notification push via ntfy"),
    "Statt oder zusätzlich zur Mail: eine Nachricht aufs Handy über ntfy (ntfy.sh oder dein eigener Server), sobald ein Freund einen Druckwunsch einreicht oder eine Rückfrage schreibt. Trag die Adresse deines Themas ein. Für ein geschütztes Thema einen Zugangstoken (tk_…) oder Benutzer:Passwort, wird verschlüsselt gespeichert und nie wieder angezeigt. Leer = keine Push-Nachrichten.":
        ("Instead of or in addition to e-mail: a message on your phone via ntfy (ntfy.sh or your own server) whenever a friend submits a print request or asks a question. Enter the address of your topic. For a protected topic, add an access token (tk_…) or user:password, it is stored encrypted and never shown again. Empty = no push notifications.",
         "À la place de l'e-mail ou en plus : un message sur ton téléphone via ntfy (ntfy.sh ou ton propre serveur) dès qu'un ami envoie une demande d'impression ou pose une question. Saisis l'adresse de ton sujet. Pour un sujet protégé, ajoute un jeton d'accès (tk_…) ou utilisateur:mot de passe, il est enregistré chiffré et n'est plus jamais affiché. Vide = pas de notifications push."),
    "Adresse des Themas": ("Topic address", "Adresse du sujet"),
    "Zugang (optional)": ("Access (optional)", "Accès (facultatif)"),
    "Push-Nachrichten pausieren (Adresse bleibt gespeichert)": ("Pause push notifications (address stays saved)",
                                                                "Mettre les notifications push en pause (l'adresse reste enregistrée)"),
    "Testnachricht senden": ("Send test message", "Envoyer un message de test"),
    "Testnachricht ist raus.": ("Test message sent.", "Message de test envoyé."),
    "Versand fehlgeschlagen:": ("Sending failed:", "Échec de l'envoi :"),
    "Das sieht nicht wie die Adresse eines ntfy-Themas aus, z. B. https://ntfy.example.org/druck.":
        ("That doesn't look like the address of an ntfy topic, e.g. https://ntfy.example.org/print.",
         "Cela ne ressemble pas à l'adresse d'un sujet ntfy, par ex. https://ntfy.example.org/impression."),
    "Testnachricht von PleasePrintit": ("Test message from PleasePrintit", "Message de test de PleasePrintit"),
    "Klappt! Hier meldet sich PleasePrintit bei neuen Druckwünschen und Rückfragen.":
        ("It works! PleasePrintit will notify you here about new print requests and questions.",
         "Ça marche ! PleasePrintit te préviendra ici des nouvelles demandes d'impression et des questions."),
    "Neuer Druckwunsch von {name}": ("New print request from {name}", "Nouvelle demande d'impression de {name}"),
    # --- Rückfragen und interne Notiz am Auftrag ---
    "Rückfragen": ("Questions", "Questions"),
    "Nachricht": ("Message", "Message"),
    "Senden": ("Send", "Envoyer"),
    "Noch keine Nachrichten. Fragen zum Auftrag kannst du hier stellen, die andere Seite bekommt eine Mail.":
        ("No messages yet. Ask questions about this request here; the other side gets an e-mail.",
         "Pas encore de messages. Pose ici tes questions sur la demande ; l'autre côté reçoit un e-mail."),
    "z. B. Geht das auch in Schwarz?": ("e.g. Could this be done in black?", "p. ex. C'est possible en noir ?"),
    "Neuer Kommentar von {name}": ("New comment from {name}", "Nouveau commentaire de {name}"),
    "Neue Nachricht von der Werkstatt": ("New message from the workshop", "Nouveau message de l'atelier"),
    "Interne Notiz": ("Internal note", "Note interne"),
    # --- Warteschlange, Nochmal drucken, Foto ---
    "Platz {n} in der Warteschlange": ("Position {n} in the queue", "Position {n} dans la file d'attente"),
    "Nochmal drucken": ("Print again", "Imprimer à nouveau"),
    "Foto vom fertigen Druck": ("Photo of the finished print", "Photo de l'impression terminée"),
    "Foto ersetzen": ("Replace photo", "Remplacer la photo"),
    "Foto hochladen": ("Upload photo", "Téléverser la photo"),
    "Der Freund sieht es im Auftrag und bekommt es mit der Mail „Gedruckt“.":
        ("Your friend sees it on the request and gets it with the “Printed” e-mail.",
         "Ton ami la voit dans la demande et la reçoit avec l'e-mail « Imprimé »."),
    "(sieht nur die Werkstatt)": ("(only the workshop sees this)", "(visible uniquement par l'atelier)"),
    "z. B. 0,2 mm, mit Stützen, Platte 2": ("e.g. 0.2 mm, with supports, plate 2", "p. ex. 0,2 mm, avec supports, plateau 2"),
    "(optional)": ("(optional)", "(facultatif)"),
    "oder": ("or", "ou"),
    "ich": ("me", "moi"),
    "Gespeichert.": ("Saved.", "Enregistré."),

    # --- Status ---
    "Neu": ("New", "Nouveau"),
    "Eingereicht": ("Submitted", "Envoyé"),
    "Geplant": ("Planned", "Planifié"),
    "Gedruckt": ("Printed", "Imprimé"),
    "Unterwegs": ("On its way", "En route"),
    "Zugestellt": ("Delivered", "Livré"),
    "Abgelehnt": ("Declined", "Refusé"),
    "Status": ("Status", "Statut"),

    # --- Anmeldung, Einladung, Passwort ---
    "Deine Druckwünsche. Sortiert statt im Chat.": ("Your print requests. Sorted, not lost in chat.",
                                                    "Tes demandes d’impression. Triées, pas perdues dans le chat."),
    "Link oder Datei einreichen, Farbe wählen, Status verfolgen – die Werkstatt erledigt den Rest.":
        ("Send a link or file, pick a colour, follow the status – the workshop does the rest.",
         "Envoie un lien ou un fichier, choisis une couleur, suis le statut – l’atelier s’occupe du reste."),
    "Privat · nur auf Einladung": ("Private · invite only", "Privé · sur invitation"),
    "Anmelden": ("Sign in", "Se connecter"),
    "Melde dich an, dann geht es direkt weiter – genau dorthin, wo du hinwolltest.":
        ("Sign in and you’ll go straight to where you wanted to be.",
         "Connecte-toi et tu arriveras directement là où tu voulais aller."),
    "Name": ("Name", "Nom"),
    "Passwort": ("Password", "Mot de passe"),
    "Passwort vergessen?": ("Forgot your password?", "Mot de passe oublié ?"),
    "Noch kein Konto? Du brauchst einen Einladungslink von der Werkstatt.":
        ("No account yet? You need an invite link from the workshop.",
         "Pas encore de compte ? Il te faut un lien d’invitation de l’atelier."),
    "Passwort vergessen": ("Forgot password", "Mot de passe oublié"),
    "Kein Problem.": ("No problem.", "Pas de souci."),
    "Wenn zu deinen Angaben eine E-Mail-Adresse hinterlegt ist, ist jetzt ein Link unterwegs.":
        ("If there is an email address for what you entered, a link is on its way.",
         "Si une adresse e-mail correspond à ta saisie, un lien est en route."),
    "Der Link gilt 24 Stunden. Schau auch im Spam-Ordner nach.":
        ("The link is valid for 24 hours. Check your spam folder too.",
         "Le lien est valable 24 heures. Pense à vérifier tes spams."),
    "Keine Mail bekommen? Dann hast du vermutlich keine Adresse im Profil hinterlegt – frag die Werkstatt nach einem Passwort-Link.":
        ("No email? You probably haven’t added an address to your profile – ask the workshop for a password link.",
         "Pas d’e-mail ? Tu n’as sans doute pas d’adresse dans ton profil – demande un lien à l’atelier."),
    "Gib deinen Namen oder deine E-Mail-Adresse ein. Hast du im Profil eine Adresse hinterlegt, schicken wir dir einen Link zum Zurücksetzen.":
        ("Enter your name or email address. If your profile has an address, we’ll send you a reset link.",
         "Saisis ton nom ou ton adresse e-mail. Si ton profil contient une adresse, on t’envoie un lien de réinitialisation."),
    "Name oder E-Mail": ("Name or email", "Nom ou e-mail"),
    "Link schicken": ("Send link", "Envoyer le lien"),
    "Keine E-Mail hinterlegt? Die Werkstatt kann dir einen Passwort-Link schicken.":
        ("No email saved? The workshop can send you a password link.",
         "Pas d’e-mail enregistré ? L’atelier peut t’envoyer un lien."),
    "Frag die Werkstatt – sie schickt dir einen Link, mit dem du ein neues Passwort setzen kannst.":
        ("Ask the workshop – they’ll send you a link to set a new password.",
         "Demande à l’atelier – il t’enverra un lien pour choisir un nouveau mot de passe."),
    "Zur Anmeldung": ("Back to sign in", "Retour à la connexion"),
    "Einladung": ("Invitation", "Invitation"),
    "Willkommen!": ("Welcome!", "Bienvenue !"),
    "Wähle einen Namen und ein Passwort, dann kannst du Druckwünsche einreichen.":
        ("Choose a name and a password, then you can send print requests.",
         "Choisis un nom et un mot de passe, puis tu pourras envoyer des demandes d’impression."),
    "3–30 Zeichen: Buchstaben, Ziffern, Punkt, Strich": ("3–30 characters: letters, digits, dot, dash",
                                                          "3 à 30 caractères : lettres, chiffres, point, tiret"),
    "mindestens 8 Zeichen": ("at least 8 characters", "au moins 8 caractères"),
    "Konto anlegen": ("Create account", "Créer le compte"),
    "Neues Passwort": ("New password", "Nouveau mot de passe"),
    "Hallo {name}!": ("Hi {name}!", "Salut {name} !"),
    "Wähle ein neues Passwort. Danach bist du direkt angemeldet.":
        ("Choose a new password. You’ll be signed in right after.",
         "Choisis un nouveau mot de passe. Tu seras connecté juste après."),
    "Passwort speichern": ("Save password", "Enregistrer le mot de passe"),

    # --- Auftragsliste ---
    "Werkstatt · Warteschlange": ("Workshop · queue", "Atelier · file d’attente"),
    "Hallo {name}": ("Hi {name}", "Salut {name}"),
    "Meine Aufträge": ("My requests", "Mes demandes"),
    "Alle Aufträge": ("All requests", "Toutes les demandes"),
    "Neuer Auftrag": ("New request", "Nouvelle demande"),
    "Nach Status filtern": ("Filter by status", "Filtrer par statut"),
    "Alle": ("All", "Toutes"),
    "Titel, Link, Datei oder Freund …": ("Title, link, file or friend …", "Titre, lien, fichier ou ami …"),
    "Suchen": ("Search", "Rechercher"),
    "Person": ("Person", "Personne"),
    "Alle Personen": ("Everyone", "Tout le monde"),
    "Ich selbst": ("Myself", "Moi-même"),
    "Art": ("Type", "Type"),
    "Links & Dateien": ("Links & files", "Liens et fichiers"),
    "Nur Links": ("Links only", "Liens uniquement"),
    "Nur Dateien": ("Files only", "Fichiers uniquement"),
    "Filtern": ("Filter", "Filtrer"),
    "{n} Stück": ("{n} pcs", "{n} pièce(s)"),
    "Nichts gefunden": ("Nothing found", "Rien trouvé"),
    "Keine Aufträge passen zu diesem Filter.": ("No requests match this filter.", "Aucune demande ne correspond à ce filtre."),
    "Filter zurücksetzen": ("Reset filter", "Réinitialiser le filtre"),
    "Noch nichts in der Warteschlange": ("Nothing in the queue yet", "Rien dans la file pour l’instant"),
    "Ein Link (Printables, Instagram, Etsy …) oder eine STL-, 3MF- oder STEP-Datei genügt.":
        ("A link (Printables, Instagram, Etsy …) or an STL, 3MF or STEP file is all it takes.",
         "Un lien (Printables, Instagram, Etsy …) ou un fichier STL, 3MF ou STEP suffit."),
    "Ersten Wunsch einreichen": ("Send your first request", "Envoyer ta première demande"),

    # --- Neuer Auftrag ---
    "Was soll gedruckt werden?": ("What should be printed?", "Que faut-il imprimer ?"),
    "Modell": ("Model", "Modèle"),
    "Link zum Modell": ("Link to the model", "Lien vers le modèle"),
    "Egal woher: Printables, MakerWorld, Thingiverse, aber auch Instagram, TikTok, Etsy, Amazon …":
        ("From anywhere: Printables, MakerWorld, Thingiverse, but also Instagram, TikTok, Etsy, Amazon …",
         "D’où tu veux : Printables, MakerWorld, Thingiverse, mais aussi Instagram, TikTok, Etsy, Amazon …"),
    "Vorschau klappt nicht? Eigenes Bild und Titel angeben":
        ("Preview not working? Add your own image and title", "L’aperçu ne marche pas ? Ajoute ta propre image et ton titre"),
    "Bild zum Link": ("Image for the link", "Image pour le lien"),
    "(optional, JPG, PNG, GIF oder WebP bis 5 MB)":
        ("(optional, JPG, PNG, GIF or WebP up to 5 MB)", "(facultatif, JPG, PNG, GIF ou WebP jusqu’à 5 Mo)"),
    "Manche Seiten (z. B. MakerWorld) verbieten den automatischen Abruf. Dann gibst du Titel (unten) und Bild selbst an.":
        ("Some sites (e.g. MakerWorld) forbid automatic fetching. Then enter the title (below) and an image yourself.",
         "Certains sites (p. ex. MakerWorld) interdisent la récupération automatique. Indique alors toi-même le titre (en bas) et une image."),
    "STL, 3MF oder STEP hierher ziehen": ("Drop an STL, 3MF or STEP here", "Dépose un STL, 3MF ou STEP ici"),
    "oder klicken zum Auswählen · bis 100 MB": ("or click to choose · up to 100 MB", "ou clique pour choisir · jusqu’à 100 Mo"),
    "Druckbereich der Werkstatt: max. {dims} mm": ("Workshop build volume: max. {dims} mm",
                                                   "Volume d’impression de l’atelier : max. {dims} mm"),
    "(0 = beliebig)": ("(0 = any)", "(0 = illimité)"),
    "Filament & Farbe": ("Filament & colour", "Filament et couleur"),
    "Filament und Farbe": ("Filament and colour", "Filament et couleur"),
    "„Random“ heißt: Die Werkstatt sucht die Farbe aus.": ("“Random” means the workshop picks the colour.",
                                                           "« Au hasard » : l’atelier choisit la couleur."),
    "Tipp: Unter Einstellungen legst du Filamente und Farben an, aus denen Freunde wählen.":
        ("Tip: add the filaments and colours friends can choose from in the settings.",
         "Astuce : ajoute dans les réglages les filaments et couleurs parmi lesquels tes amis choisissent."),
    "Stückzahl & Titel": ("Quantity & title", "Quantité et titre"),
    "Stückzahl": ("Quantity", "Quantité"),
    "Titel": ("Title", "Titre"),
    "sonst aus Link oder Dateiname": ("otherwise taken from link or file name", "sinon tiré du lien ou du nom de fichier"),
    "Auftrag einreichen": ("Send request", "Envoyer la demande"),
    "Random": ("Random", "Au hasard"),
    "Random – freie Wahl": ("Random – your choice", "Au hasard – à ton choix"),

    # --- Auftrag (Detail) ---
    "Auftrag": ("Request", "Demande"),
    "eingereicht {at}": ("submitted {at}", "envoyée le {at}"),
    "Von": ("From", "De"),
    "Filament": ("Filament", "Filament"),
    "Datei": ("File", "Fichier"),
    "Link": ("Link", "Lien"),
    "Maße": ("Dimensions", "Dimensions"),
    "Volumen": ("Volume", "Volume"),
    "Gewicht": ("Weight", "Poids"),
    "(gesamt)": ("(total)", "(total)"),
    "Materialkosten (Schätzung)": ("Material cost (estimate)", "Coût du matériau (estimation)"),
    "grob aus dem Modellvolumen": ("rough, from the model volume", "approximatif, d’après le volume"),
    "Für einen Preis trag in den Einstellungen den Preis pro kg ein.":
        ("For a price, enter the price per kg in the settings.",
         "Pour obtenir un prix, saisis le prix au kg dans les réglages."),
    "Vorschau von {site}": ("Preview from {site}", "Aperçu de {site}"),
    "Vorschau deines Modells": ("Preview of your model", "Aperçu de ton modèle"),
    "Leider nicht – warum?": ("Sorry, not this time – why?", "Désolé, pas cette fois – pourquoi ?"),
    "Leider nicht": ("Sorry, not this time", "Désolé, pas cette fois"),
    "Die Werkstatt kann diesen Wunsch nicht drucken.": ("The workshop can’t print this request.",
                                                        "L’atelier ne peut pas imprimer cette demande."),
    "Mit anderem Filament neu einreichen": ("Resubmit with a different filament", "Renvoyer avec un autre filament"),
    "Dein Modell wird übernommen – du musst nichts neu hochladen. Es bekommt eine neue Auftragsnummer.":
        ("Your model is carried over – no need to upload again. It gets a new request number.",
         "Ton modèle est repris – rien à renvoyer. Il reçoit un nouveau numéro de demande."),
    "Neu einreichen": ("Resubmit", "Renvoyer"),
    "Neu eingereicht als #{nr}": ("Resubmitted as #{nr}", "Renvoyée sous le n° {nr}"),
    "Neuen Wunsch einreichen": ("Send a new request", "Envoyer une nouvelle demande"),
    "Mit anderem Filament neu eingereicht als": ("Resubmitted with a different filament as",
                                                 "Renvoyée avec un autre filament sous le n°"),
    "Abgelehnt: {reason}": ("Declined: {reason}", "Refusée : {reason}"),
    "Der Freund liest: „{text}“": ("Your friend reads: “{text}”", "Ton ami lit : « {text} »"),
    "Modell wird geladen …": ("Loading model …", "Chargement du modèle …"),
    "Ziehen zum Drehen · Mausrad oder zwei Finger zum Zoomen": ("Drag to rotate · scroll or pinch to zoom",
                                                                 "Glisse pour tourner · molette ou deux doigts pour zoomer"),
    "Status setzen": ("Set status", "Changer le statut"),
    "Ablehnen mit Grund": ("Decline with a reason", "Refuser avec un motif"),
    "(ein Klick genügt)": ("(one click is enough)", "(un clic suffit)"),
    "Freitext": ("Free text", "Texte libre"),
    "(sieht der Freund genau so)": ("(your friend sees it exactly like this)", "(ton ami le verra tel quel)"),
    "z. B. Lass uns kurz telefonieren": ("e.g. Let’s have a quick call", "p. ex. Appelle-moi vite fait"),
    "Mit Freitext ablehnen": ("Decline with free text", "Refuser avec ce texte"),
    "Datei herunterladen": ("Download file", "Télécharger le fichier"),
    "Link öffnen": ("Open link", "Ouvrir le lien"),
    "3D-Datei ersetzen": ("Replace 3D file", "Remplacer le fichier 3D"),
    "3D-Datei hinterlegen": ("Attach 3D file", "Joindre un fichier 3D"),
    "STL, 3MF oder STEP": ("STL, 3MF or STEP", "STL, 3MF ou STEP"),
    "(bis 100 MB)": ("(up to 100 MB)", "(jusqu’à 100 Mo)"),
    "Datei hinterlegen": ("Attach file", "Joindre le fichier"),
    "Vorschaubild ersetzen": ("Replace preview image", "Remplacer l’aperçu"),
    "Neues Bild": ("New image", "Nouvelle image"),
    "(JPG, PNG, GIF oder WebP, bis 5 MB)": ("(JPG, PNG, GIF or WebP, up to 5 MB)", "(JPG, PNG, GIF ou WebP, jusqu’à 5 Mo)"),
    "Bild ersetzen": ("Replace image", "Remplacer l’image"),

    # --- Ablehnungsgründe: Kurzform (gespeichert) und ausformuliert ---
    "Zu komplex": ("Too complex", "Trop complexe"),
    "Druckdauer zu lang": ("Takes too long to print", "Impression trop longue"),
    "Zu groß für den Drucker": ("Too big for the printer", "Trop grand pour l’imprimante"),
    "Filament nicht vorrätig": ("Filament not in stock", "Filament indisponible"),
    "Material zu teuer": ("Material too expensive", "Matériau trop cher"),
    "Modell fehlerhaft": ("Faulty model", "Modèle défectueux"),
    "Das Modell ist für meinen Drucker leider zu komplex – zum Beispiel wegen vieler Stützstrukturen oder sehr feiner Details.":
        ("Unfortunately the model is too complex for my printer – for example because of lots of supports or very fine details.",
         "Le modèle est malheureusement trop complexe pour mon imprimante – par exemple à cause de nombreux supports ou de détails très fins."),
    "Der Druck würde sehr lange dauern und den Drucker zu lange blockieren. Vielleicht klappt es mit einer kleineren Version?":
        ("The print would take very long and block the printer for too long. Maybe a smaller version would work?",
         "L’impression durerait très longtemps et bloquerait l’imprimante trop longtemps. Une version plus petite pourrait peut-être marcher ?"),
    "Das Modell ist größer als mein Druckbereich. Wenn es sich verkleinern oder in Teile zerlegen lässt, versuch es gern noch einmal.":
        ("The model is bigger than my build volume. If it can be scaled down or split into parts, feel free to try again.",
         "Le modèle dépasse mon volume d’impression. S’il peut être réduit ou découpé en morceaux, n’hésite pas à réessayer."),
    "Das gewünschte Filament habe ich gerade nicht da. Magst du eine andere Farbe oder ein anderes Material wählen?":
        ("I don’t have the filament you asked for right now. Would you like to pick another colour or material?",
         "Je n’ai pas le filament demandé en ce moment. Tu veux choisir une autre couleur ou un autre matériau ?"),
    "Das Material für diesen Druck wäre leider zu teuer. Lass uns kurz sprechen, ob es eine günstigere Lösung gibt.":
        ("The material for this print would unfortunately be too expensive. Let’s talk about a cheaper option.",
         "Le matériau pour cette impression serait malheureusement trop cher. Parlons-en pour trouver une solution moins chère."),
    "Die Datei hat Fehler (zum Beispiel Löcher im Modell) und lässt sich so nicht sauber drucken. Hast du vielleicht eine andere Version?":
        ("The file has errors (for example holes in the model) and can’t be printed cleanly. Do you have another version?",
         "Le fichier contient des erreurs (par exemple des trous dans le modèle) et ne s’imprime pas proprement. Tu aurais une autre version ?"),

    # --- Profil ---
    "Für dich gedruckt": ("Printed for you", "Imprimé pour toi"),
    "1 Teil": ("1 part", "1 pièce"),
    "{n} Teile": ("{n} parts", "{n} pièces"),
    "Material ca.": ("Material approx.", "Matériau env."),
    "Grobe Schätzung ohne Strom und Druckzeit – falls du dich mal mit einer Rolle Filament oder einem Kaffee revanchieren magst.":
        ("Rough estimate without electricity and print time – in case you’d like to return the favour with a spool of filament or a coffee.",
         "Estimation grossière, sans électricité ni temps d’impression – au cas où tu voudrais rendre la pareille avec une bobine de filament ou un café."),
    "Noch nichts gedruckt. Sobald ein Auftrag fertig ist, siehst du hier, was zusammengekommen ist.":
        ("Nothing printed yet. Once a request is done, you’ll see the total here.",
         "Rien d’imprimé pour l’instant. Dès qu’une demande est terminée, tu verras le total ici."),
    "Benachrichtigung per E-Mail": ("Email notifications", "Notifications par e-mail"),
    "Freiwillig: Trag deine Adresse ein, dann bekommst du eine Mail, sobald sich der Status eines Auftrags ändert oder die Werkstatt dir schreibt. Feld leeren = keine Mails mehr.":
        ("Optional: add your address and you’ll get an email whenever a request’s status changes or the workshop writes to you. Clear the field = no more emails.",
         "Facultatif : indique ton adresse et tu recevras un e-mail à chaque changement de statut ou quand l’atelier t’écrit. Champ vide = plus d’e-mails."),
    "E-Mail-Adresse": ("Email address", "Adresse e-mail"),
    "du@beispiel.de": ("you@example.com", "toi@exemple.fr"),
    "Testmail schicken": ("Send test email", "Envoyer un e-mail de test"),
    "Die Werkstatt hat den Mailversand noch nicht eingerichtet.": ("The workshop hasn’t set up email yet.",
                                                                   "L’atelier n’a pas encore configuré l’envoi d’e-mails."),
    "Gilt für die ganze App und für deine Status-Mails.": ("Applies to the whole app and to your status emails.",
                                                          "S’applique à toute l’application et à tes e-mails de statut."),
    "Was gespeichert wird": ("What is stored", "Ce qui est enregistré"),
    "Dein Name, dein Passwort (nur verschlüsselt), deine Aufträge mit Dateien, deine Sprache und – falls eingetragen – deine E-Mail-Adresse. Nur die Werkstatt sieht deine Aufträge. Die Adresse wird nur für Status-Mails genutzt und nicht weitergegeben.":
        ("Your name, your password (hashed only), your requests with files, your language and – if entered – your email address. Only the workshop sees your requests. The address is used for status emails only and never shared.",
         "Ton nom, ton mot de passe (uniquement chiffré), tes demandes avec fichiers, ta langue et – si tu l’as saisie – ton adresse e-mail. Seul l’atelier voit tes demandes. L’adresse ne sert qu’aux e-mails de statut et n’est jamais transmise."),

    # --- Einstellungen ---
    "Werkstatt · Einstellungen": ("Workshop · settings", "Atelier · réglages"),
    "Drucker & Material": ("Printer & material", "Imprimante et matériau"),
    "Druckbereich": ("Build volume", "Volume d’impression"),
    "Größtes Modell, das dein Drucker schafft. Freunde können größere Dateien nicht einreichen (Drehen wird berücksichtigt). Leer = keine Grenze.":
        ("Largest model your printer can handle. Friends can’t submit bigger files (rotation is taken into account). Empty = no limit.",
         "Plus grand modèle que ton imprimante peut produire. Tes amis ne peuvent pas envoyer de fichiers plus grands (la rotation est prise en compte). Vide = pas de limite."),
    "Kostenschätzung": ("Cost estimate", "Estimation des coûts"),
    "Gewicht = Modellvolumen × Dichte × Materialanteil. Ein Druck ist nicht massiv: Wände + Füllung ergeben meist 30–60 % eines Vollkörpers. Vergleiche ab und zu mit deinem Slicer und stell den Wert nach.":
        ("Weight = model volume × density × material share. A print isn’t solid: walls + infill usually come to 30–60 % of a solid body. Compare with your slicer now and then and adjust.",
         "Poids = volume du modèle × densité × part de matériau. Une impression n’est pas pleine : parois + remplissage font en général 30 à 60 % d’un volume plein. Compare de temps en temps avec ton slicer et ajuste."),
    "Materialanteil": ("Material share", "Part de matériau"),
    "Filamente und Farben": ("Filaments and colours", "Filaments et couleurs"),
    "Freunde wählen daraus beim Einreichen. Jedes Filament hat automatisch „Random“: Dann entscheidest du die Farbe.":
        ("Friends choose from these when submitting. Every filament automatically has “Random”: then you decide the colour.",
         "Tes amis choisissent parmi ceux-ci. Chaque filament a automatiquement « Au hasard » : c’est alors toi qui choisis la couleur."),
    "Filament {name} löschen": ("Delete filament {name}", "Supprimer le filament {name}"),
    "Filament löschen": ("Delete filament", "Supprimer le filament"),
    "Preis": ("Price", "Prix"),
    "z. B. 20": ("e.g. 20", "p. ex. 20"),
    "Dichte": ("Density", "Densité"),
    "Farbe {name} löschen": ("Delete colour {name}", "Supprimer la couleur {name}"),
    "Farbe": ("Colour", "Couleur"),
    "Farbname, z. B. Schwarz": ("Colour name, e.g. Black", "Nom de couleur, p. ex. Noir"),
    "Farbname": ("Colour name", "Nom de couleur"),
    "Noch keine Filamente. Leg unten das erste an, z. B. „PLA“.": ("No filaments yet. Add the first one below, e.g. “PLA”.",
                                                                    "Pas encore de filament. Ajoute le premier ci-dessous, p. ex. « PLA »."),
    "Filament-Sorte": ("Filament type", "Type de filament"),
    "Filament-Sorte wählen …": ("Choose filament type …", "Choisis le type de filament …"),
    "Die Dichte wird passend zur Sorte vorausgefüllt. Trag noch deinen Preis pro kg ein.":
        ("The density is pre-filled for the type. Just add your price per kg.",
         "La densité est préremplie selon le type. Ajoute encore ton prix au kilo."),
    "Impressum & Datenschutz": ("Legal notice & privacy", "Mentions légales et confidentialité"),
    "Öffentlich, verlinkt auf der Anmeldeseite und unten auf jeder Seite. Name, Anschrift und E-Mail stehen verschleiert im HTML und werden erst im Browser zusammengesetzt – Adress- und Mail-Sammler finden sie so nicht.":
        ("Public, linked on the sign-in page and at the bottom of every page. Name, address and email are obfuscated in the HTML and only assembled in the browser – address and email harvesters won’t find them.",
         "Public, lié depuis la page de connexion et en bas de chaque page. Nom, adresse et e-mail sont masqués dans le HTML et assemblés seulement dans le navigateur – les collecteurs d’adresses ne les trouvent pas."),
    "Straße und Hausnummer": ("Street and number", "Rue et numéro"),
    "PLZ und Ort": ("Postcode and city", "Code postal et ville"),
    "E-Mail": ("Email", "E-mail"),
    "Telefon": ("Phone", "Téléphone"),
    "Vorname Nachname": ("First name Last name", "Prénom Nom"),
    "Musterweg 1": ("1 Example Street", "1 rue de l’Exemple"),
    "12345 Musterstadt": ("12345 Sample Town", "75000 Ville"),
    "Impressum ansehen": ("View legal notice", "Voir les mentions légales"),
    "Noch nicht gespeichert – oben steht die Vorlage. Lies sie einmal durch, pass sie an und speichere.":
        ("Not saved yet – the template is shown above. Read it once, adjust it and save.",
         "Pas encore enregistré – le modèle est affiché ci-dessus. Lis-le, adapte-le et enregistre."),
    "Datenschutz ansehen": ("View privacy page", "Voir la page confidentialité"),

    # --- Freunde verwalten ---
    "Werkstatt · Zugänge": ("Workshop · access", "Atelier · accès"),
    "Einladungslink erzeugen": ("Create invite link", "Créer un lien d’invitation"),
    "Offene Einladungen": ("Open invitations", "Invitations en attente"),
    "Jeder Link funktioniert einmal und gilt {days} Tage. Kopieren und z. B. per WhatsApp schicken.":
        ("Each link works once and is valid for {days} days. Copy it and send it, e.g. via WhatsApp.",
         "Chaque lien fonctionne une fois et reste valable {days} jours. Copie-le et envoie-le, p. ex. par WhatsApp."),
    "Einladungslink vom {day}": ("Invite link from {day}", "Lien d’invitation du {day}"),
    "Offene Passwort-Links": ("Open password links", "Liens de mot de passe en attente"),
    "Gilt einmal und {hours} Stunden. Schick den Link nur an die Person, der er gehört.":
        ("Works once and for {hours} hours. Only send the link to the person it belongs to.",
         "Valable une fois et pendant {hours} heures. N’envoie le lien qu’à la personne concernée."),
    "Passwort-Link für {name}": ("Password link for {name}", "Lien de mot de passe pour {name}"),
    "seit {date}": ("since {date}", "depuis le {date}"),
    "bekommt Status-Mails": ("gets status emails", "reçoit les e-mails de statut"),
    "gesperrt": ("blocked", "bloqué"),
    "{n} Auftr.": ("{n} req.", "{n} dem."),
    "Materialkosten aller gedruckten Teile (Schätzung)": ("Material cost of all printed parts (estimate)",
                                                         "Coût matériau de toutes les pièces imprimées (estimation)"),
    "Link für ein neues Passwort erzeugen": ("Create a link for a new password", "Créer un lien pour un nouveau mot de passe"),
    "Passwort-Link": ("Password link", "Lien mot de passe"),
    "Sperren": ("Block", "Bloquer"),
    "Entsperren": ("Unblock", "Débloquer"),
    "Noch niemand dabei. Erzeuge oben einen Einladungslink.": ("Nobody here yet. Create an invite link above.",
                                                              "Personne pour l’instant. Crée un lien d’invitation ci-dessus."),
    "Status-Mails: eingerichtet – Freunde mit E-Mail-Adresse werden bei jeder Statusänderung benachrichtigt.":
        ("Status emails: set up – friends with an email address are notified on every status change.",
         "E-mails de statut : configurés – les amis avec une adresse sont prévenus à chaque changement."),
    "Status-Mails: aus. Trag einen SMTP-Zugang in die .env ein.": ("Status emails: off. Add SMTP settings to the .env.",
                                                                    "E-mails de statut : désactivés. Ajoute un accès SMTP dans le .env."),

    # --- Rechtliches ---
    "Impressum wird geladen …": ("Loading legal notice …", "Chargement des mentions légales …"),
    "Bitte JavaScript aktivieren, um das Impressum zu sehen.": ("Please enable JavaScript to see the legal notice.",
                                                               "Active JavaScript pour voir les mentions légales."),
    "Noch nicht eingetragen.": ("Not filled in yet.", "Pas encore renseigné."),
    "Dieser Text wird von der Werkstatt gepflegt und steht nur in ihrer Sprache zur Verfügung.":
        ("This text is maintained by the workshop and is only available in its language.",
         "Ce texte est rédigé par l’atelier et n’existe que dans sa langue."),
    "Angaben gemäß § 5 DDG": ("Information pursuant to § 5 DDG (German Digital Services Act)",
                              "Informations selon le § 5 DDG (loi allemande sur les services numériques)"),
    "Kontakt": ("Contact", "Contact"),
    "Verantwortlich für den Inhalt": ("Responsible for the content", "Responsable du contenu"),
    "Anschrift wie oben": ("address as above", "adresse ci-dessus"),
    "Privates, nicht-kommerzielles Angebot für einen geschlossenen Freundeskreis.":
        ("Private, non-commercial service for a closed circle of friends.",
         "Service privé et non commercial pour un cercle d’amis fermé."),

    # --- Mails ---
    "Warum?": ("Why?", "Pourquoi ?"),
    "Gewicht (Schätzung)": ("Weight (estimate)", "Poids (estimation)"),
    "Auftrag ansehen": ("View request", "Voir la demande"),
    "Dein Druckwunsch ist eingegangen.": ("Your print request has arrived.", "Ta demande d’impression est bien arrivée."),
    "Dein Druckwunsch ist eingeplant – bald liegt er auf dem Druckbett.":
        ("Your print request is planned – it’ll be on the print bed soon.",
         "Ta demande est planifiée – elle sera bientôt sur le plateau."),
    "Dein Druckwunsch ist fertig gedruckt und kann abgeholt werden.":
        ("Your print request is done and ready to pick up.", "Ta demande est imprimée et prête à être récupérée."),
    "Preis aushandeln": ("Negotiate price", "Négocier le prix"),
    "abgemacht": ("agreed", "convenu"),
    "Angebot der Werkstatt": ("Workshop offer", "Offre de l’atelier"),
    "Gegenvorschlag des Freundes": ("Friend’s counteroffer", "Contre-proposition de l’ami"),
    "Der Freund muss annehmen oder einen Gegenvorschlag machen. Bis dahin wird nicht gedruckt.": ("The friend has to accept or make a counteroffer. Nothing is printed until then.", "L’ami doit accepter ou faire une contre-proposition. Rien n’est imprimé d’ici là."),
    "Annehmen": ("Accept", "Accepter"),
    "Bitte eine Zahl eingeben.": ("Please enter a number.", "Saisissez un nombre."),
    "Nächster Schritt": ("Next step", "Étape suivante"),
    "Ablehnen": ("Decline", "Refuser"),
    "Grund": ("Reason", "Motif"),
    "Status frei ändern (Korrektur)": ("Change status freely (correction)", "Changer le statut librement (correction)"),
    "Währung": ("Currency", "Devise"),
    "Für Preise, Guthaben und Mails. Es wird nichts umgerechnet, nur das Kürzel ändert sich.": ("For prices, credit and emails. Nothing is converted, only the label changes.", "Pour les prix, le crédit et les e-mails. Rien n’est converti, seul le sigle change."),
    "Bitte den Preis als Zahl eingeben, z. B. 12,50.": ("Please enter the price as a number, e.g. 12.50.", "Saisissez le prix sous forme de nombre, p. ex. 12,50."),
    "Auf diesen Preis lässt sich gerade nicht antworten. Lade die Seite neu, vielleicht hat sich schon etwas geändert.": ("This price can’t be answered right now. Reload the page, something may have changed.", "Impossible de répondre à ce prix pour le moment. Rechargez la page, quelque chose a peut-être changé."),
    "Bitte den Betrag als Zahl eingeben, z. B. 10 oder -5.": ("Please enter the amount as a number, e.g. 10 or -5.", "Saisissez le montant sous forme de nombre, p. ex. 10 ou -5."),
    "Der Betrag muss zwischen 0,01 und 1000 liegen (mit Minus zum Abziehen).": ("The amount must be between 0.01 and 1000 (use a minus to deduct).", "Le montant doit être compris entre 0,01 et 1000 (avec un moins pour déduire)."),
    "Bitte den Aufschlag als Zahl eingeben, z. B. 20.": ("Please enter the surcharge as a number, e.g. 20.", "Saisissez la majoration sous forme de nombre, p. ex. 20."),
    "Du bist nicht angemeldet, oder die Sitzung ist abgelaufen. Bitte melde dich neu an.": ("You are not signed in, or your session has expired. Please sign in again.", "Vous n’êtes pas connecté, ou votre session a expiré. Reconnectez-vous."),
    "Das hat nicht geklappt": ("That didn’t work", "Ça n’a pas marché"),
    "Das hat nicht geklappt. Bitte prüfe deine Eingabe und versuche es noch einmal.": ("That didn’t work. Please check your input and try again.", "Ça n’a pas marché. Vérifiez votre saisie et réessayez."),
    "Dafür hast du keine Berechtigung.": ("You don’t have permission to do that.", "Vous n’avez pas l’autorisation de faire cela."),
    "Diese Seite oder dieser Auftrag existiert nicht (mehr).": ("This page or order does not exist (any more).", "Cette page ou cette commande n’existe pas (ou plus)."),
    "Diese Aktion ist hier nicht möglich.": ("This action isn’t possible here.", "Cette action n’est pas possible ici."),
    "Das wurde schon erledigt.": ("That has already been done.", "C’est déjà fait."),
    "Es ist ein Fehler aufgetreten. Bitte versuche es noch einmal.": ("Something went wrong. Please try again.", "Une erreur s’est produite. Réessayez."),
    "Zurück zur Übersicht": ("Back to overview", "Retour à l’aperçu"),
    "Als abgemacht eintragen": ("Mark as agreed", "Marquer comme convenu"),
    "Zum Beispiel, wenn ihr euch schon mündlich geeinigt habt.": ("For example, if you already agreed verbally.", "Par exemple, si vous êtes déjà d’accord oralement."),
    "Mein Gegenvorschlag": ("My counteroffer", "Ma contre-proposition"),
    "Senden": ("Send", "Envoyer"),
    "Die Werkstatt antwortet. Bis dahin wird nicht gedruckt.": ("The workshop will reply. Nothing is printed until then.", "L’atelier répond. Rien n’est imprimé d’ici là."),
    "Neues Angebot": ("New offer", "Nouvelle offre"),
    "Angebot senden": ("Send offer", "Envoyer l’offre"),
    "Der Freund bekommt eine Mail und antwortet im Auftrag. Gedruckt wird erst, wenn der Preis abgemacht ist.": ("The friend gets an email and replies in the request. Printing starts once the price is agreed.", "L’ami reçoit un e-mail et répond dans la demande. L’impression démarre une fois le prix convenu."),
    "Der Preis ist noch nicht abgemacht.": ("The price hasn’t been agreed yet.", "Le prix n’est pas encore convenu."),
    "Für ein Angebot brauchst du einen Preis.": ("You need a price for an offer.", "Il faut un prix pour une offre."),
    "Angebot der Werkstatt: {price}": ("Workshop offer: {price}", "Offre de l’atelier : {price}"),
    "Preis abgemacht: {price}": ("Price agreed: {price}", "Prix convenu : {price}"),
    "Gegenvorschlag: {price}": ("Counteroffer: {price}", "Contre-proposition : {price}"),
    "Gegenvorschlag": ("Counteroffer", "Contre-proposition"),
    "Limit offener Aufträge": ('Open request limit', 'Limite de demandes ouvertes'),
    "So viele Aufträge darf ein Freund gleichzeitig offen haben (neu oder geplant). Die Werkstatt hat kein Limit.": ('This many requests a friend may have open at once (new or planned). The workshop has no limit.', 'Nombre de demandes qu’un ami peut avoir ouvertes en même temps (nouvelles ou planifiées). L’atelier n’a pas de limite.'),
    "Offene Aufträge pro Freund": ('Open requests per friend', 'Demandes ouvertes par ami'),
    "Sendungsverfolgung": ("Tracking", "Suivi du colis"),
    "Sendungsnummer oder Verfolgungs-Link": ("Tracking number or link", "Numéro ou lien de suivi"),
    "(wird mit „Unterwegs“ per Mail verschickt)": ("(sent by email with “On its way”)", "(envoyé par e-mail avec « En route »)"),
    "Dein Druck ist unterwegs zu dir.": ("Your print is on its way to you.", "Ton impression est en route."),
    "Dein Druck ist angekommen. Viel Freude damit!": ("Your print has arrived. Enjoy!", "Ton impression est arrivée. Bon amusement !"),
    "Dein Druckwunsch kann leider nicht gedruckt werden.": ("Unfortunately your print request can’t be printed.",
                                                            "Ta demande ne peut malheureusement pas être imprimée."),
    "Du bekommst diese Mail, weil du in PleasePrintit eine E-Mail-Adresse hinterlegt hast.":
        ("You’re getting this email because you added an email address in PleasePrintit.",
         "Tu reçois cet e-mail parce que tu as indiqué une adresse dans PleasePrintit."),
    "Keine Mails mehr? Adresse im Profil löschen:": ("No more emails? Remove the address in your profile:",
                                                     "Plus d’e-mails ? Supprime l’adresse dans ton profil :"),
    "Passwort zurücksetzen": ("Reset password", "Réinitialiser le mot de passe"),
    "Dein Link für ein neues Passwort – gilt {hours} Stunden.": ("Your link for a new password – valid for {hours} hours.",
                                                                 "Ton lien pour un nouveau mot de passe – valable {hours} heures."),
    "Du hast einen Link für ein neues Passwort angefordert. Ein Klick genügt – danach bist du direkt angemeldet.":
        ("You asked for a link to set a new password. One click is enough – you’ll be signed in right after.",
         "Tu as demandé un lien pour un nouveau mot de passe. Un clic suffit – tu seras connecté juste après."),
    "Du hast einen Link für ein neues Passwort angefordert:": ("You asked for a link to set a new password:",
                                                               "Tu as demandé un lien pour un nouveau mot de passe :"),
    "Neues Passwort setzen": ("Set new password", "Choisir un nouveau mot de passe"),
    "Der Link gilt {hours} Stunden und nur einmal.": ("The link is valid for {hours} hours and works once.",
                                                     "Le lien est valable {hours} heures et une seule fois."),
    "Du warst das nicht? Dann ignoriere diese Mail einfach – dein Passwort bleibt, wie es ist.":
        ("Wasn’t you? Just ignore this email – your password stays as it is.",
         "Ce n’était pas toi ? Ignore simplement cet e-mail – ton mot de passe ne change pas."),

    # --- Meldungen aus app.py ---
    "Du hast schon {n} offene Aufträge. Warte, bis welche gedruckt sind.":
        ("You already have {n} open requests. Wait until some are printed.",
         "Tu as déjà {n} demandes en cours. Attends que certaines soient imprimées."),
    "Dein Speicherplatz ({mb} MB) ist voll.": ("Your storage ({mb} MB) is full.", "Ton espace de stockage ({mb} Mo) est plein."),
    "Zu viele Fehlversuche. Bitte 15 Minuten warten.": ("Too many failed attempts. Please wait 15 minutes.",
                                                        "Trop d’échecs. Merci d’attendre 15 minutes."),
    "Name oder Passwort falsch.": ("Wrong name or password.", "Nom ou mot de passe incorrect."),
    "Diese Einladung ist ungültig oder abgelaufen.": ("This invitation is invalid or has expired.",
                                                      "Cette invitation est invalide ou a expiré."),
    "Name: 3–30 Zeichen, nur Buchstaben, Ziffern, . _ -": ("Name: 3–30 characters, only letters, digits, . _ -",
                                                           "Nom : 3 à 30 caractères, uniquement lettres, chiffres, . _ -"),
    "Passwort: mindestens 8 Zeichen.": ("Password: at least 8 characters.", "Mot de passe : au moins 8 caractères."),
    "Dieser Name ist schon vergeben.": ("This name is already taken.", "Ce nom est déjà pris."),
    "Bitte entweder einen Link oder eine 3D-Datei angeben.": ("Please provide either a link or a 3D file.",
                                                              "Indique soit un lien, soit un fichier 3D."),
    "Bitte einen Link mit http:// oder https:// eingeben.": ("Please enter a link starting with http:// or https://.",
                                                             "Saisis un lien commençant par http:// ou https://."),
    "Bitte Filament und Farbe auswählen.": ("Please choose a filament and colour.", "Choisis un filament et une couleur."),
    "Das Modell ({dims} mm) passt nicht in den Druckbereich ({bed} mm).":
        ("The model ({dims} mm) doesn’t fit the build volume ({bed} mm).",
         "Le modèle ({dims} mm) ne tient pas dans le volume d’impression ({bed} mm)."),
    "Nur echte STL-, 3MF- oder STEP-Dateien bis 100 MB.": ("Only real STL, 3MF or STEP files up to 100 MB.",
                                                         "Uniquement de vrais fichiers STL, 3MF ou STEP jusqu’à 100 Mo."),
    "Die Datei ist zu groß (max. 100 MB).": ("The file is too big (max. 100 MB).", "Le fichier est trop gros (max. 100 Mo)."),
    "Nur JPG, PNG, GIF oder WebP bis 5 MB.": ("Only JPG, PNG, GIF or WebP up to 5 MB.", "Uniquement JPG, PNG, GIF ou WebP jusqu’à 5 Mo."),
    "Das sieht nicht wie eine E-Mail-Adresse aus.": ("That doesn’t look like an email address.",
                                                     "Ça ne ressemble pas à une adresse e-mail."),
    "E-Mail-Adresse gelöscht – du bekommst keine Mails mehr.": ("Email address removed – you won’t get any more emails.",
                                                                "Adresse supprimée – tu ne recevras plus d’e-mails."),
    "Reich zuerst einen Auftrag ein – die Testmail zeigt deinen neuesten.":
        ("Send a request first – the test email shows your latest one.",
         "Envoie d’abord une demande – l’e-mail de test affiche la plus récente."),
    "Versand fehlgeschlagen. Die Werkstatt schaut nach.": ("Sending failed. The workshop will take a look.",
                                                           "L’envoi a échoué. L’atelier va regarder."),
    "Testmail an {to} ist raus.": ("Test email sent to {to}.", "E-mail de test envoyé à {to}."),
    "Zu viele Versuche. Bitte 15 Minuten warten.": ("Too many attempts. Please wait 15 minutes.",
                                                    "Trop de tentatives. Merci d’attendre 15 minutes."),
    "Dieser Link ist ungültig oder abgelaufen.": ("This link is invalid or has expired.", "Ce lien est invalide ou a expiré."),
    "Die E-Mail-Adresse im Impressum sieht nicht richtig aus.": ("The email address in the legal notice doesn’t look right.",
                                                                 "L’adresse e-mail des mentions légales semble incorrecte."),

    # --- JavaScript (Upload-Prüfung, 3D-Ansicht, Impressum) ---
    "✗ Die Datei ist größer als 100 MB.": ("✗ The file is larger than 100 MB.", "✗ Le fichier dépasse 100 Mo."),
    "{name} wird ausgemessen …": ("Measuring {name} …", "Mesure de {name} …"),
    "Maße: {d} mm": ("Dimensions: {d} mm", "Dimensions : {d} mm"),
    "✓ Maße: {d} mm – passt aufs Druckbett": ("✓ Dimensions: {d} mm – fits the print bed",
                                              "✓ Dimensions : {d} mm – tient sur le plateau"),
    "✗ Maße: {d} mm – zu groß für den Druckbereich ({bed} mm)": ("✗ Dimensions: {d} mm – too big for the build volume ({bed} mm)",
                                                                  "✗ Dimensions : {d} mm – trop grand pour le volume d’impression ({bed} mm)"),
    " – als Werkstatt kannst du trotzdem anlegen.": (" – as the workshop you can still create it.",
                                                     " – en tant qu’atelier, tu peux quand même la créer."),
    ". Bitte verkleinern oder teilen.": (". Please scale it down or split it.", ". Réduis-le ou découpe-le."),
    "Die Datei konnte nicht gelesen werden. Ist es eine echte STL-, 3MF- oder STEP-Datei?":
        ("The file couldn’t be read. Is it a real STL, 3MF or STEP file?",
         "Impossible de lire le fichier. Est-ce un vrai fichier STL, 3MF ou STEP ?"),
    "Maße: {d} mm (B × T × H)": ("Dimensions: {d} mm (W × D × H)", "Dimensions : {d} mm (L × P × H)"),
    "✓ passt aufs Druckbett": ("✓ fits the print bed", "✓ tient sur le plateau"),
    "✗ größer als Druckbereich ({bed} mm)": ("✗ larger than the build volume ({bed} mm)",
                                            "✗ plus grand que le volume d’impression ({bed} mm)"),
    "Modell konnte nicht angezeigt werden.": ("The model couldn’t be displayed.", "Impossible d’afficher le modèle."),

    # --- Einstellungen: Tabs ---
    "Bereiche der Einstellungen": ("Settings sections", "Sections des réglages"),
    "Drucker": ("Printer", "Imprimante"),
    "Filamente": ("Filaments", "Filaments"),

    # --- Archiv ---
    "Archiv": ("Archive", "Archives"),
    "Werkstatt · Archiv": ("Workshop · Archive", "Atelier · Archives"),
    "Archivieren": ("Archive", "Archiver"),
    "Zurückholen": ("Restore", "Restaurer"),
    "Ausgewählte archivieren": ("Archive selected", "Archiver la sélection"),
    "Ausgewählte zurückholen": ("Restore selected", "Restaurer la sélection"),
    "Auftrag {nr} auswählen": ("Select request {nr}", "Sélectionner la demande {nr}"),
    "Archiviert am {at}": ("Archived on {at}", "Archivée le {at}"),
    "Eingereicht ab": ("Submitted from", "Envoyée à partir du"),
    "Eingereicht bis": ("Submitted until", "Envoyée jusqu’au"),
    "Das Archiv ist leer": ("The archive is empty", "Les archives sont vides"),
    "Gedruckte und abgelehnte Aufträge landen hier nach der Frist aus den Einstellungen oder per Knopf.":
        ("Printed and declined requests end up here after the period set in Settings, or with a button.",
         "Les demandes imprimées ou refusées arrivent ici après le délai fixé dans les réglages, ou avec un bouton."),
    "Gedruckte und abgelehnte Aufträge verschwinden nach so vielen Tagen aus der Warteschlange und liegen im Archiv, mit Suche. 0 = nie automatisch, nur per Knopf.":
        ("Printed and declined requests leave the queue after this many days and move to the searchable archive. "
         "0 = never automatically, only with the button.",
         "Les demandes imprimées ou refusées quittent la file après ce nombre de jours et vont dans les archives, "
         "avec recherche. 0 = jamais automatiquement, seulement avec le bouton."),
    "Archivieren nach": ("Archive after", "Archiver après"),
    "Tagen": ("days", "jours"),

    # --- Slicer ---
    "Slicer": ("Slicer", "Trancheur"),
    "Link-Vorschau (optional)": ("Link preview (optional)", "Aperçu des liens (facultatif)"),
    "Manche Seiten sperren den automatischen Abruf von Titel und Bild. Mit eigenem Zugang geht es trotzdem: Thingiverse-App-Token (thingiverse.com/developers) und Cults3D-Nickname mit API-Schlüssel aus deinem Cults-Konto. Die Werte werden verschlüsselt gespeichert und nie wieder angezeigt. Ein leeres Feld lässt den gespeicherten Wert unverändert.":
        ("Some sites block automatic fetching of title and image. With your own access it still works: Thingiverse app token (thingiverse.com/developers) and Cults3D nickname with the API key from your Cults account. Values are stored encrypted and never shown again. An empty field keeps the stored value.",
         "Certains sites bloquent la récupération automatique du titre et de l’image. Avec ton propre accès, ça marche quand même : jeton d’appli Thingiverse (thingiverse.com/developers) et pseudo Cults3D avec la clé API de ton compte Cults. Les valeurs sont chiffrées et jamais réaffichées. Un champ vide conserve la valeur enregistrée."),
    "Thingiverse: App-Token": ("Thingiverse: app token", "Thingiverse : jeton d’appli"),
    "Cults3D: Nickname": ("Cults3D: nickname", "Cults3D : pseudo"),
    "Cults3D: API-Schlüssel": ("Cults3D: API key", "Cults3D : clé API"),
    "(in der .env gesetzt, dort ändern)": ("(set in .env, change it there)", "(défini dans .env, à modifier là-bas)"),
    "✓ gesetzt": ("✓ set", "✓ défini"),
    "nicht lesbar, bitte neu eingeben": ("unreadable, please enter again", "illisible, saisis à nouveau"),
    "Entfernen": ("Remove", "Supprimer"),
    "In {name} öffnen": ("Open in {name}", "Ouvrir dans {name}"),
    "Knöpfe im Auftrag, die die 3D-Datei direkt in deinem Slicer am PC öffnen. Der Slicer muss installiert sein. Der Link gilt eine Stunde.":
        ("Buttons on a request that open the 3D file directly in the slicer on your computer. The slicer must be "
         "installed. The link is valid for one hour.",
         "Des boutons sur la demande qui ouvrent le fichier 3D directement dans le trancheur de ton ordinateur. Le "
         "trancheur doit être installé. Le lien est valable une heure."),

    # --- Trinkgeld ---
    "Trinkgeld": ("Tip", "Pourboire"),
    "Trinkgeld geben": ("Leave a tip", "Laisser un pourboire"),
    "Trinkgeld-Link": ("Tip link", "Lien pour le pourboire"),
    "Freiwillig: Dein Link zu PayPal.me, Ko-fi oder Ähnlichem. Freunde sehen dann einen Knopf im Profil und bei gedruckten Aufträgen. Die App verarbeitet kein Geld. Leer = kein Knopf.":
        ("Optional: your link to PayPal.me, Ko-fi or similar. Friends then see a button in their profile and on "
         "printed requests. The app itself handles no money. Empty = no button.",
         "Facultatif : ton lien PayPal.me, Ko-fi ou similaire. Tes amis voient alors un bouton dans leur profil et "
         "sur les demandes imprimées. L’app ne gère aucun argent. Vide = pas de bouton."),
    "Bitte eine vollständige Adresse mit https:// eintragen, z. B. https://paypal.me/deinname.":
        ("Please enter a full address starting with https://, e.g. https://paypal.me/yourname.",
         "Saisis une adresse complète commençant par https://, p. ex. https://paypal.me/tonnom."),

    # --- Statistik ---
    "Statistik": ("Statistics", "Statistiques"),
    "Werkstatt · Statistik": ("Workshop · Statistics", "Atelier · Statistiques"),
    "Deine Statistik": ("Your statistics", "Tes statistiques"),
    "Gedruckte Teile": ("Printed parts", "Pièces imprimées"),
    "Material": ("Material", "Matière"),
    "Materialkosten": ("Material cost", "Coût de la matière"),
    "Kosten": ("Cost", "Coût"),
    "Ø Wartezeit": ("Avg. waiting time", "Attente moyenne"),
    "{n} Tage": ("{n} days", "{n} jours"),
    "Lieblings-Filament": ("Favourite filament", "Filament préféré"),
    "Monat": ("Month", "Mois"),
    "Letzte 12 Monate": ("Last 12 months", "12 derniers mois"),
    "Letzte 6 Monate": ("Last 6 months", "6 derniers mois"),
    "Eingereicht zählt nach Datum des Auftrags, Gedruckt nach Datum des Drucks. Material und Kosten sind grob aus dem Modellvolumen geschätzt.":
        ("Submitted counts by request date, Printed by print date. Material and cost are rough estimates from the "
         "model volume.",
         "Envoyée compte selon la date de la demande, Imprimée selon la date d’impression. Matière et coût sont "
         "estimés grossièrement à partir du volume du modèle."),
    "Nach Status": ("By status", "Par statut"),
    "Beliebteste Filamente": ("Most popular filaments", "Filaments les plus demandés"),
    "Beliebteste Farben": ("Most popular colours", "Couleurs les plus demandées"),
    "Ablehnungsgründe": ("Reasons for declining", "Motifs de refus"),
    "ohne Grund": ("no reason given", "sans motif"),
    "Noch keine Daten.": ("No data yet.", "Pas encore de données."),
    "Noch nichts abgelehnt.": ("Nothing declined yet.", "Rien de refusé pour l’instant."),
    "Noch keine Zahlen": ("No numbers yet", "Pas encore de chiffres"),
    "Sobald Aufträge eingehen, siehst du hier, was los ist.":
        ("As soon as requests come in, you’ll see what’s going on here.",
         "Dès que des demandes arrivent, tu verras ici ce qui se passe."),
    # --- Vorab zahlen (Haken pro Auftrag oder Guthaben-Konto) ---
    "Vorab zahlen": ("Pay in advance", "Payer d'avance"),
    "Vorab bezahlen": ("Pay in advance", "Payer d'avance"),
    "Vorab zahlen: an": ("Pay in advance: on", "Payer d'avance : oui"),
    "Vorab zahlen: aus": ("Pay in advance: off", "Payer d'avance : non"),
    "Optional: Freunde zahlen die Filament-Kosten vor dem Druck. Die App rechnet nur und merkt sich den Stand – das Geld läuft außerhalb (bar, PayPal …). Eingeschaltet wird es danach pro Freund auf der Freunde-Seite.":
        ("Optional: friends pay the filament cost before printing. The app only calculates and remembers the status – the money changes hands outside it (cash, PayPal …). It is then switched on per friend on the Friends page.",
         "Facultatif : les amis paient le filament avant l'impression. L'application ne fait que calculer et retenir l'état – l'argent passe en dehors (espèces, PayPal …). On l'active ensuite pour chaque ami sur la page Amis."),
    "Aus": ("Off", "Désactivé"),
    "Pro Auftrag bezahlen": ("Pay per request", "Payer par demande"),
    "(Freund sieht den Preis, du setzt den Haken „bezahlt“)":
        ("(friend sees the price, you tick “paid”)", "(l'ami voit le prix, tu coches « payé »)"),
    "Guthaben-Konto": ("Credit account", "Compte crédit"),
    "(du lädst Guthaben auf, Aufträge werden davon bezahlt)":
        ("(you top up credit, requests are paid from it)", "(tu recharges le crédit, les demandes en sont payées)"),
    "Aufschlag für Strom, Verschleiß und Ausschuss": ("Surcharge for power, wear and failed prints",
                                                       "Supplément pour électricité, usure et échecs"),
    "Richtwert 30 %. Preis = Filamentkosten × (1 + Aufschlag). Die Filamentkosten kommen aus dem Preis pro kg unter „Filamente“. Ohne Volumen oder Preis pro kg legst du den Preis am Auftrag selbst fest.":
        ("Rule of thumb 30 %. Price = filament cost × (1 + surcharge). The filament cost comes from the price per kg under “Filaments”. Without volume or price per kg you set the price on the request yourself.",
         "Valeur indicative 30 %. Prix = coût du filament × (1 + supplément). Le coût du filament vient du prix au kg sous « Filaments ». Sans volume ni prix au kg, tu fixes le prix sur la demande."),
    "Guthaben": ("Credit", "Crédit"),
    "Dein Guthaben": ("Your credit", "Ton crédit"),
    "Aufladen": ("Top up", "Recharger"),
    "Betrag in Euro": ("Amount in euros", "Montant en euros"),
    "Aufladen lässt du es bei der Werkstatt. Jeder Auftrag wird davon bezahlt, abgelehnte bekommst du zurück.":
        ("You top it up at the workshop. Every request is paid from it; rejected ones are refunded.",
         "Tu le fais recharger à l'atelier. Chaque demande en est payée ; les refusées sont remboursées."),
    "Aufladung": ("Top-up", "Recharge"),
    "Korrektur": ("Correction", "Correction"),
    "Rückerstattung": ("Refund", "Remboursement"),
    "bezahlt": ("paid", "payé"),
    "offen": ("open", "en attente"),
    "kostenlos": ("free", "gratuit"),
    "€ offen": ("€ open", "€ en attente"),
    "Preis festlegen": ("Set price", "Fixer le prix"),
    "automatisch": ("automatic", "automatique"),
    "Leer = automatisch aus Filamentkosten und Aufschlag. 0 = kostenlos.":
        ("Empty = automatic from filament cost and surcharge. 0 = free.",
         "Vide = automatique d'après le coût du filament et le supplément. 0 = gratuit."),
    "Als bezahlt markieren": ("Mark as paid", "Marquer comme payé"),
    "Haken zurücknehmen": ("Undo tick", "Annuler la coche"),
    "Der Preis steht noch nicht fest. Die Werkstatt legt ihn fest.":
        ("The price is not set yet. The workshop will set it.", "Le prix n'est pas encore fixé. L'atelier le fixera."),
    "Bitte zahl den Betrag an die Werkstatt, bevor gedruckt wird. Sie setzt den Haken, sobald er angekommen ist.":
        ("Please pay the amount to the workshop before printing. It ticks the box once the money has arrived.",
         "Merci de payer le montant à l'atelier avant l'impression. Il coche la case dès que l'argent est arrivé."),
    "Der Preis wird von deinem Guthaben abgebucht ({balance} da). Reicht es nicht, lass es bei der Werkstatt aufladen.":
        ("The price is deducted from your credit ({balance} available). If it is not enough, have it topped up at the workshop.",
         "Le prix est déduit de ton crédit ({balance} disponible). S'il ne suffit pas, fais-le recharger à l'atelier."),
    "Wird automatisch abgebucht, sobald das Guthaben reicht ({balance} da).":
        ("Charged automatically as soon as the credit is enough ({balance} available).",
         "Débité automatiquement dès que le crédit suffit ({balance} disponible)."),
    "Du zahlst vorab: Der Preis wird von deinem Guthaben abgebucht. Dein Guthaben: {balance}.":
        ("You pay in advance: the price is deducted from your credit. Your credit: {balance}.",
         "Tu paies d'avance : le prix est déduit de ton crédit. Ton crédit : {balance}."),
    "Du zahlst vorab: Nach dem Einreichen siehst du den Preis. Gedruckt wird, sobald die Werkstatt die Zahlung bestätigt hat.":
        ("You pay in advance: after submitting you will see the price. Printing starts once the workshop has confirmed the payment.",
         "Tu paies d'avance : après l'envoi tu vois le prix. L'impression commence dès que l'atelier a confirmé le paiement."),
    "Noch nicht bezahlt: Erst die Zahlung bestätigen, das Guthaben aufladen oder einen Preis festlegen.":
        ("Not paid yet: first confirm the payment, top up the credit or set a price.",
         "Pas encore payé : confirme d'abord le paiement, recharge le crédit ou fixe un prix."),
    "Schon bezahlt: Der Preis lässt sich nicht mehr ändern.":
        ("Already paid: the price can no longer be changed.", "Déjà payé : le prix ne peut plus être modifié."),
    "Erst einen Preis festlegen.": ("Set a price first.", "Fixe d'abord un prix."),
    "Das Guthaben kann nicht unter 0 fallen.": ("The credit cannot drop below 0.", "Le crédit ne peut pas passer sous 0."),
}

# Texte, die static/*.js braucht; base.html legt sie für die gewählte Sprache als JSON in die Seite
JS_KEYS = (
    "✗ Die Datei ist größer als 100 MB.", "{name} wird ausgemessen …", "Maße: {d} mm",
    "✓ Maße: {d} mm – passt aufs Druckbett", "✗ Maße: {d} mm – zu groß für den Druckbereich ({bed} mm)",
    " – als Werkstatt kannst du trotzdem anlegen.", ". Bitte verkleinern oder teilen.",
    "Die Datei konnte nicht gelesen werden. Ist es eine echte STL-, 3MF- oder STEP-Datei?", "Maße: {d} mm (B × T × H)",
    "✓ passt aufs Druckbett", "✗ größer als Druckbereich ({bed} mm)", "Modell konnte nicht angezeigt werden.",
    "E-Mail", "Angaben gemäß § 5 DDG", "Kontakt", "Telefon", "Verantwortlich für den Inhalt", "Anschrift wie oben",
    "Privates, nicht-kommerzielles Angebot für einen geschlossenen Freundeskreis.",
)

# Datenschutz-Vorlage für die Einstellungen; "de" setzt app.py (DATENSCHUTZ_TEMPLATE)
PRIVACY_TEMPLATES = {
    "en": """Controller
The person named in the legal notice.

What is stored
– Account: name, password (as a hash only), optional email address and language
– Requests: links, uploaded 3D files, preview images, chosen filament
– One sign-in cookie and one language cookie (technically necessary), no tracking or advertising cookies
– The server briefly logs IP addresses to protect against attacks

Why
Only to accept and work through print requests and – if wanted – to send status updates by email. No sharing with third parties, no analytics, no external fonts or scripts.

Where
On a private server. Status emails are sent through the workshop's email provider.

Your rights
Access, correction and deletion of your data: a short message to the workshop is enough. You can delete your email address yourself in your profile at any time.""",
    "fr": """Responsable
La personne indiquée dans les mentions légales.

Ce qui est enregistré
– Compte : nom, mot de passe (uniquement sous forme de hash), adresse e-mail et langue facultatives
– Demandes : liens, fichiers 3D envoyés, images d'aperçu, filament choisi
– Un cookie de connexion et un cookie de langue (techniquement nécessaires), aucun cookie de suivi ou publicitaire
– Le serveur enregistre brièvement les adresses IP pour se protéger des attaques

Pourquoi
Uniquement pour recevoir et traiter les demandes d'impression et – si tu le souhaites – t'informer du statut par e-mail. Aucune transmission à des tiers, aucun outil d'analyse, aucune police ni script externe.

Où
Sur un serveur privé. Les e-mails de statut passent par le fournisseur e-mail de l'atelier.

Tes droits
Accès, rectification et suppression de tes données : un petit message à l'atelier suffit. Tu peux supprimer toi-même ton adresse e-mail dans ton profil à tout moment.""",
}

_COL = {"en": 0, "fr": 1}


def t(lang, text, /, **kw):
    """Text in der Sprache lang; Platzhalter wie {name} werden mit kw gefüllt."""
    row = T.get(text)
    out = row[_COL[lang]] if row and lang in _COL else text
    return out.format(**kw) if kw else out


def js_texts(lang):
    return {k: t(lang, k) for k in JS_KEYS} if lang in _COL else {}
