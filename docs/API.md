# API Documentation - Devis Châssis Aluminium

## Base URL
```
http://localhost:5000/api
```

## Authentication

Toutes les routes marquées 🔒 nécessitent une authentification via session.
Les routes marquées 🔑 nécessitent le rôle admin.

### Session Management
L'authentification utilise les sessions Flask. Après un login réussi, un cookie de session est automatiquement créé.

---

## Endpoints

### 1. Authentication

#### POST /api/auth/login
Connexion utilisateur

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response 200:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "admin",
    "full_name": "Administrateur",
    "role": "admin",
    "created_at": "2025-10-03T20:00:00"
  }
}
```

**Error 401:**
```json
{
  "error": "Invalid credentials"
}
```

---

#### POST /api/auth/logout 🔒
Déconnexion utilisateur

**Response 200:**
```json
{
  "success": true
}
```

---

#### GET /api/auth/check
Vérifier le statut d'authentification

**Response 200 (authentifié):**
```json
{
  "authenticated": true,
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "full_name": "Administrateur"
  }
}
```

**Response 200 (non authentifié):**
```json
{
  "authenticated": false
}
```

---

### 2. Catalog

#### GET /api/catalog/chassis-types
Liste des types de châssis

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "Baie vitrée coulissante",
    "description": "Grande ouverture coulissante",
    "min_width": 1000,
    "max_width": 5000,
    "min_height": 1000,
    "max_height": 3000
  }
]
```

---

#### GET /api/catalog/profile-series
Liste des séries de profilés

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "Série Fine",
    "description": "Profilé élégant pour utilisation standard",
    "price_per_meter": 35.00
  }
]
```

---

#### GET /api/catalog/glazing-types
Liste des types de vitrage

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "10mm - Simple",
    "description": "Simple vitrage 10mm",
    "thickness_mm": 10,
    "price_per_m2": 85.00
  }
]
```

---

#### GET /api/catalog/finishes
Liste des finitions

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "Anodisé bronze",
    "description": "Finition anodisée bronze",
    "price_coefficient": 1.25
  }
]
```

---

#### GET /api/catalog/accessories
Liste des accessoires

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "Charnière invisible (unité)",
    "unit_price": 18.00,
    "incompatible_series": null
  }
]
```

---

#### GET /api/config
Configuration générale (TVA, coefficient de pertes)

**Response 200:**
```json
{
  "vat_rate": 20.0,
  "loss_coefficient": 1.1
}
```

---

### 3. Quotes

#### POST /api/calculate 🔒
Calcul du prix d'un devis

**Request Body:**
```json
{
  "width": 1200,
  "height": 1000,
  "chassis_type": "Fenêtre 1/2 vantaux",
  "profile_series": "Série Fine",
  "glazing_type": "4/6/4 - Double",
  "finish": "Anodisé bronze",
  "accessories": ["Charnière standard (unité)"],
  "discount": 0
}
```

**Response 200:**
```json
{
  "surface_m2": 1.200,
  "perimeter_m": 4.40,
  "base_surface": 125.40,
  "base_linear": 154.00,
  "accessories": [
    {
      "name": "Charnière standard (unité)",
      "price": 12.00
    }
  ],
  "accessories_total": 12.00,
  "finish_coefficient": 1.25,
  "subtotal_with_finish": 364.25,
  "labor": 80.00,
  "total_before_discount": 444.25,
  "discount_percent": 0,
  "discount_amount": 0.00,
  "total_ht": 444.25,
  "vat_rate": 20.00,
  "vat_amount": 88.85,
  "total_ttc": 533.10
}
```

**Error 400:**
```json
{
  "error": "Width must be between 500 and 1800 mm"
}
```

---

#### POST /api/quotes 🔒
Créer un nouveau devis

**Request Body:**
```json
{
  "chassis_type": "Fenêtre 1/2 vantaux",
  "width": 1200,
  "height": 1000,
  "profile_series": "Série Fine",
  "glazing_type": "4/6/4 - Double",
  "finish": "Anodisé bronze",
  "accessories": ["Charnière standard (unité)"],
  "discount": 0,
  "price_ht": 444.25,
  "price_ttc": 533.10,
  "breakdown": {
    "surface_m2": 1.200,
    "total_ttc": 533.10
  }
}
```

**Response 200:**
```json
{
  "quote_number": "DEV-20251003-0001",
  "quote_id": 1
}
```

---

#### GET /api/quotes/stats 🔒
Statistiques des devis

**Response 200:**
```json
{
  "total": 15,
  "thisMonth": 8,
  "totalAmount": 8500.50,
  "avgAmount": 566.70
}
```

---

#### GET /api/quotes/recent?limit=10 🔒
Liste des devis récents

**Query Parameters:**
- `limit` (optional): Nombre de devis à retourner (défaut: 10)

**Response 200:**
```json
[
  {
    "id": 1,
    "quote_number": "DEV-20251003-0001",
    "quote_date": "2025-10-03",
    "total_price": 533.10,
    "chassis_type_name": "Fenêtre 1/2 vantaux",
    "client_name": "Entreprise ABC",
    "created_at": "2025-10-03T20:30:00"
  }
]
```

---

#### GET /api/quotes/{quote_id}/pdf 🔒
Générer et télécharger le PDF d'un devis

**Response 200:**
- Content-Type: application/pdf
- Content-Disposition: attachment
- Fichier PDF du devis

**Error 404:**
```json
{
  "error": "Quote not found"
}
```

**Error 507:**
```json
{
  "error": "PDF too large (550.2KB > 500KB limit)"
}
```

---

### 4. Users

#### GET /api/users 🔑
Liste de tous les utilisateurs

**Response 200:**
```json
[
  {
    "id": 1,
    "username": "admin",
    "full_name": "Administrateur",
    "role": "admin",
    "created_at": "2025-10-03T20:00:00"
  }
]
```

---

#### POST /api/users 🔑
Créer un nouvel utilisateur

**Request Body:**
```json
{
  "username": "john.doe",
  "password": "secure_password",
  "full_name": "John Doe",
  "role": "user"
}
```

**Response 200:**
```json
{
  "success": true,
  "user": {
    "id": 2,
    "username": "john.doe",
    "full_name": "John Doe",
    "role": "user",
    "created_at": "2025-10-03T21:00:00"
  }
}
```

**Error 400:**
```json
{
  "error": "Username already exists"
}
```

---

#### DELETE /api/users/{user_id} 🔑
Supprimer un utilisateur

**Response 200:**
```json
{
  "success": true,
  "message": "User deleted"
}
```

**Error 400:**
```json
{
  "error": "Cannot delete your own account"
}
```

---

### 5. Settings

#### GET /api/settings?section=company 🔒
Récupérer les paramètres

**Query Parameters:**
- `section` (optional): Filtrer par section (company, quote, pdf, currency, theme)

**Response 200:**
```json
[
  {
    "id": 1,
    "section": "company",
    "key": "name",
    "value": "Mon Entreprise"
  }
]
```

---

#### POST /api/settings 🔑
Mettre à jour les paramètres

**Request Body:**
```json
{
  "section": "company",
  "settings": {
    "name": "Mon Entreprise",
    "address": "123 Rue Example",
    "phone": "+212 5 12 34 56 78"
  }
}
```

**Response 200:**
```json
{
  "success": true
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Succès |
| 400 | Mauvaise requête |
| 401 | Non authentifié |
| 403 | Accès interdit (admin requis) |
| 404 | Resource non trouvée |
| 500 | Erreur serveur |
| 507 | Fichier trop volumineux |

---

## Data Models

### User
```typescript
{
  id: number
  username: string
  full_name: string
  role: "admin" | "user"
  created_at: datetime
}
```

### ChassisType
```typescript
{
  id: number
  name: string
  description: string
  min_width: number
  max_width: number
  min_height: number
  max_height: number
}
```

### Quote
```typescript
{
  id: number
  quote_number: string
  quote_date: string
  chassis_type: string
  width: number
  height: number
  profile_series: string
  glazing_type: string
  finish: string
  accessories: string[]
  discount_percent: number
  price_ht: number
  price_ttc: number
  details: object
  created_at: datetime
}
```

---

## Notes

- Tous les montants sont en MAD (Dirham Marocain)
- Les dimensions sont en millimètres
- Les surfaces sont en m²
- Les périmètres sont en mètres
- La TVA par défaut est de 20%
