# AI Receptionist — Private Repository

> **⚠️ REPO PRIVÉ — NE PAS PARTAGER**
> Ce repo contient le code technique + le kit commercial complet.
> C'est le repo connecté à Render pour le déploiement.

## Structure

```
├── backend/          # FastAPI (connecté à Render)
├── tests/            # Tests
├── dashboard/        # Frontend
├── vapi_config/      # Config IA
├── docs/             # Architecture
├── sales/            # ⭐ KIT COMMERCIAL (FR + US)
│   ├── FR/           # 9 documents francophones
│   └── US/           # 9 documents américains
├── private/          # ⭐ Configs clients spécifiques
└── .env              # Secrets (jamais pushé)
```

## Connexion Render

Ce repo est connecté à Render pour le déploiement automatique.
Chaque push sur `main` déclenche un redeploy.

## Règles

1. **Ne jamais rendre ce repo public**
2. **Ne jamais partager le dossier `sales/` avec des tiers**
3. **Les configs clients vont dans `private/`**
