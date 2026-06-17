# Changelog — AI Receptionist Client Setup
> **Document interne — À remplir par le développeur pour chaque client**  
> **Version :** 2.0 — Aligné avec le Kit v5.1  
> **Objectif :** Traçabilité totale, qualité garantie, livraison professionnelle

---

## [DATE] — Client : [NOM_CLIENT]

### 📋 Informations Client (à remplir avant de commencer)

- [ ] **Nom du client / entreprise :** ___________________
- [ ] **Email client :** ___________________
- [ ] **Téléphone client :** ___________________
- [ ] **Adresse :** ___________________
- [ ] **Email Google Calendar :** ___________________
- [ ] **Numéro mobile (urgences) :** ___________________
- [ ] **Horaires d'ouverture :** ___________________
- [ ] **Services proposés :** ___________________
- [ ] **Langues :** ___________________
- [ ] **Jours de fermeture :** ___________________
- [ ] **Prix du setup :** $2,500
- [ ] **Structure de paiement :** 30/40/30
- [ ] **Acompte 30% reçu :** $750 ✅ / ⬜
- [ ] **Date de signature :** ___________________

---

### 🔧 Phase 1 : Configuration (Jour 1-2)

#### Vapi — Assistant Vocal IA
- [ ] Compte Vapi créé au nom du client (email : ___________________)
- [ ] Prompt personnalisé rédigé et validé
- [ ] Voix sélectionnée et testée
- [ ] Langues configurées (FR / AR / EN / ES)
- [ ] Fonctions Vapi configurées :
  - [ ] `book_appointment` — Prise de rendez-vous
  - [ ] `check_availability` — Vérification disponibilité
  - [ ] `transfer_call` — Transfert d'appel
  - [ ] `send_sms` — Envoi SMS
  - [ ] `handle_emergency` — Gestion urgence
- [ ] Numéro de téléphone Twilio acheté : `+...`
- [ ] Webhook Vapi configuré (URL backend)
- [ ] Tests vocaux internes réalisés (5 appels)

#### Backend — Serveur FastAPI
- [ ] Repo GitHub créé / cloné
- [ ] Environnement Python configuré (requirements.txt)
- [ ] FastAPI app structurée
- [ ] Endpoints créés :
  - [ ] POST `/webhook` — Réception appels Vapi
  - [ ] POST `/calendar` — Création événements Google
  - [ ] POST `/sms` — Envoi SMS Twilio
  - [ ] GET `/dashboard` — Données temps réel
  - [ ] GET `/health` — Health check
- [ ] Sécurité HMAC implémentée (signature webhook)
- [ ] Logs structurés configurés
- [ ] Variables d'environnement sécurisées (.env)

#### Google Calendar
- [ ] Compte Google Calendar partagé avec le compte service
- [ ] OAuth 2.0 configuré (credentials.json)
- [ ] Test de création d'événement réussi
- [ ] Rappels SMS configurés (1h + 30min)
- [ ] Titre et description standardisés

---

### 🎨 Phase 2 : Dashboard & Frontend (Jour 2-3)

- [ ] Dashboard HTML/CSS créé
- [ ] Logo et couleurs du client intégrés
- [ ] Connexion API backend fonctionnelle
- [ ] Auto-refresh 30 secondes implémenté
- [ ] Filtres (numéro, statut, date) fonctionnels
- [ ] Responsive design (PC, mobile, tablette)
- [ ] Hébergement GitHub Pages / Render configuré
- [ ] URL dashboard : `https://...`

---

### 📱 Phase 3 : SMS Twilio (Jour 3)

- [ ] Compte Twilio créé au nom du client
- [ ] Numéro d'envoi configuré
- [ ] Template SMS de confirmation rédigé :
  > *"Votre rendez-vous est confirmé le [date] à [heure]. [Nom entreprise]. Pour modifier, appelez-nous."*
- [ ] Template SMS de rappel rédigé (optionnel)
- [ ] Test d'envoi SMS réussi
- [ ] SMS reçu sur téléphone de test

---

### 🧪 Phase 4 : Tests & Validation (Jour 3-4)

#### Scénario 1 : Prise de rendez-vous standard
- [ ] Appel test réalisé
- [ ] IA a proposé des créneaux corrects
- [ ] RDV créé dans Google Calendar
- [ ] SMS de confirmation reçu
- [ ] Dashboard affiche l'appel avec statut "completed"
- [ ] Transcription correcte

#### Scénario 2 : Demande de renseignements
- [ ] Appel test réalisé
- [ ] IA a donné les bonnes informations (horaires, tarifs, adresse)
- [ ] IA a proposé de prendre un RDV
- [ ] Dashboard affiche l'appel avec statut "completed"

#### Scénario 3 : Urgence + transfert
- [ ] Appel test réalisé avec mot-clé urgence
- [ ] IA a reconnu l'urgence
- [ ] IA a donné la procédure correcte
- [ ] Transfert vers numéro mobile testé (si configuré)
- [ ] Dashboard affiche l'appel avec statut "transferred"

#### Scénario 4 : Appel en dehors des horaires
- [ ] Appel test réalisé à 20h00
- [ ] IA a décroché et proposé des RDV
- [ ] RDV créé dans Google Calendar
- [ ] SMS reçu

#### Scénario 5 : Langue secondaire
- [ ] Appel test en arabe / anglais / espagnol
- [ ] IA a basculé de langue correctement
- [ ] Conversation fluide et compréhensible

#### Tests techniques
- [ ] 10 appels de simulation réalisés
- [ ] Taux de succès : _____% (objectif : ≥ 90%)
- [ ] Webhook HMAC validé (pas de faille de sécurité)
- [ ] Logs complets et lisibles
- [ ] Pas d'erreur 500 dans les 24 dernières heures

---

### 🚀 Phase 5 : Déploiement (Jour 4-5)

- [ ] Backend déployé sur Render : `https://...`
- [ ] Dashboard hébergé sur GitHub Pages / Render : `https://...`
- [ ] Variables d'environnement configurées en production
- [ ] Webhook Vapi pointe vers l'URL de production
- [ ] Health check réussi (endpoint `/health` renvoie 200)
- [ ] SSL/HTTPS activé sur toutes les URLs
- [ ] Pas de données sensibles en dur dans le code
- [ ] .gitignore configuré (pas de .env ni credentials en clair)

---

### 📦 Phase 6 : Livraison (Jour 5)

- [ ] **Guide Client** envoyé par email (document 08)
- [ ] **Lien dashboard** testé et fonctionnel depuis le téléphone du client
- [ ] **Comptes Vapi/Twilio** remis au client (identifiants + mots de passe)
- [ ] **Google Calendar** vérifié — les RDV apparaissent bien
- [ ] **Facture acompte 30%** envoyée (si pas déjà fait)
- [ ] **Facture 40% livraison** envoyée
- [ ] **Appel Zoom de formation** réalisé (30 min)
  - [ ] Démonstration live du numéro AI
  - [ ] Explication du dashboard
  - [ ] Explication de Google Calendar
  - [ ] Explication des coûts récurrents
  - [ ] Réponse aux questions du client
  - [ ] Réponse aux questions de l'assistante
- [ ] **Enregistrement Zoom** envoyé au client (si enregistré)

---

### 📅 Phase 7 : Support (Jour 5-35)

- [ ] **Jour 5-7 :** Vérification quotidienne des logs (5 min/jour)
- [ ] **Jour 7 :** Email de check-in au client : "Tout fonctionne bien ?"
- [ ] **Jour 14 :** Email de check-in : "Besoin d'ajustements ?"
- [ ] **Jour 21 :** Email de check-in : "Statistiques du mois"
- [ ] **Jour 30 :** Email de validation : "Êtes-vous satisfait ?"
- [ ] **Jour 35 :** Facture finale 30% envoyée
- [ ] **Modification du prompt** (1x incluse) : réalisée / non demandée
- [ ] **Bugs signalés** : _____ / corrigés : _____
- [ ] **Taux de satisfaction client** : _____% (objectif : ≥ 90%)

---

### 📝 Notes & Leçons Apprises

**Ce qui a bien fonctionné :**
- 

**Ce qui a été difficile :**
- 

**Ce que je ferais différemment la prochaine fois :**
- 

**Feedback du client :**
- 

**Feedback de l'assistante :**
- 

---

### ✅ Checklist Finale — Avant de Clôturer le Dossier

- [ ] Tous les comptes sont au nom du client
- [ ] Le client a les identifiants de tous les comptes
- [ ] Le client sait comment recharger Vapi et Twilio
- [ ] Le client a épingle le dashboard sur son téléphone
- [ ] L'assistante a été formée et est à l'aise
- [ ] Le client est satisfait (taux de réussite ≥ 90%)
- [ ] La facture finale est payée
- [ ] Le dossier est archivé avec ce changelog
- [ ] Le client sait comment me contacter pour du support post-30j

---

*Changelog AI Receptionist v2.0 — Interne développeur*  
*"Qualité avant vitesse. Traçabilité avant improvisation."*
