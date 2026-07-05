# ERD — HitRadar PostgreSQL Schema

> **Dự án:** HitRadar Pro | **Feature:** 1.2 — Database Architecture
> **Người thiết kế:** Đạt | **Ngày:** 2026-07-05

---

## 1. Raw Layer ERD

```mermaid
erDiagram
    RAW_TRACKS {
        TEXT id PK
        TEXT name
        SMALLINT popularity
        INTEGER duration_ms
        SMALLINT explicit
        TEXT artists
        TEXT id_artists
        TEXT release_date
        DOUBLE_PRECISION danceability
        DOUBLE_PRECISION energy
        SMALLINT key
        DOUBLE_PRECISION loudness
        SMALLINT mode
        DOUBLE_PRECISION speechiness
        DOUBLE_PRECISION acousticness
        DOUBLE_PRECISION instrumentalness
        DOUBLE_PRECISION liveness
        DOUBLE_PRECISION valence
        DOUBLE_PRECISION tempo
        SMALLINT time_signature
        TIMESTAMPTZ _import_ts
    }

    RAW_ARTISTS {
        TEXT id PK
        DOUBLE_PRECISION followers
        TEXT genres
        TEXT name
        SMALLINT popularity
        TIMESTAMPTZ _import_ts
    }

    RAW_ARTIST_JSON {
        TEXT artist_id PK
        JSONB raw_values
        INTEGER value_count
        TEXT semantic_status
        TEXT source_file
        TIMESTAMPTZ _import_ts
    }
```

---

## 2. Clean Layer ERD

```mermaid
erDiagram
    TRACKS {
        TEXT track_id PK
        TEXT name
        SMALLINT popularity
        INTEGER duration_ms
        NUMERIC duration_min
        BOOLEAN explicit
        DATE release_date
        SMALLINT release_year
        SMALLINT release_month
        SMALLINT decade
        DOUBLE_PRECISION danceability
        DOUBLE_PRECISION energy
        SMALLINT key
        DOUBLE_PRECISION loudness
        SMALLINT mode
        DOUBLE_PRECISION speechiness
        DOUBLE_PRECISION acousticness
        DOUBLE_PRECISION instrumentalness
        DOUBLE_PRECISION liveness
        DOUBLE_PRECISION valence
        DOUBLE_PRECISION tempo
        SMALLINT time_signature
        TIMESTAMPTZ _clean_ts
    }

    ARTISTS {
        TEXT artist_id PK
        TEXT name
        BIGINT followers
        SMALLINT popularity
        TIMESTAMPTZ _clean_ts
    }

    GENRES {
        SERIAL genre_id PK
        TEXT genre_name
        TEXT normalized_genre_name
    }

    TRACK_ARTISTS {
        TEXT track_id PK
        TEXT artist_id PK
        SMALLINT artist_order
        BOOLEAN is_main_artist
    }

    ARTIST_GENRES {
        TEXT artist_id PK
        INTEGER genre_id PK
        TEXT source
    }

    ARTIST_RELATIONS {
        TEXT artist_id PK
        TEXT related_artist_id PK
        SMALLINT relation_order
        TEXT source
    }

    TRACKS ||--o{ TRACK_ARTISTS : "has artists"
    ARTISTS ||--o{ TRACK_ARTISTS : "performs in"
    ARTISTS ||--o{ ARTIST_GENRES : "belongs to"
    GENRES ||--o{ ARTIST_GENRES : "includes"
    ARTISTS ||--o{ ARTIST_RELATIONS : "related to"
```

---

## 3. Analytics Layer (Views)

```mermaid
erDiagram
    VW_TRACKS_OVERVIEW {
        TEXT track_id
        TEXT name
        SMALLINT popularity
        NUMERIC duration_min
        BOOLEAN explicit
        SMALLINT release_year
        SMALLINT decade
        DOUBLE_PRECISION danceability
        DOUBLE_PRECISION energy
        DOUBLE_PRECISION valence
    }

    VW_TRACKS_BY_DECADE {
        SMALLINT decade
        BIGINT track_count
        NUMERIC avg_popularity
        NUMERIC avg_danceability
        NUMERIC avg_energy
        NUMERIC avg_valence
        NUMERIC avg_tempo
    }

    VW_AUDIO_TRENDS {
        SMALLINT release_year
        NUMERIC avg_danceability
        NUMERIC avg_energy
        NUMERIC avg_valence
        NUMERIC avg_acousticness
        NUMERIC avg_instrumentalness
        NUMERIC avg_speechiness
    }

    VW_TOP_ARTISTS {
        TEXT artist_id
        TEXT artist_name
        BIGINT track_count
        NUMERIC avg_track_popularity
        BIGINT followers
    }

    VW_GENRE_TRENDS {
        TEXT genre_name
        SMALLINT decade
        BIGINT track_count
        NUMERIC avg_popularity
    }

    VW_ML_TRAINING_DATASET {
        TEXT track_id
        SMALLINT popularity
        INTEGER duration_ms
        NUMERIC duration_min
        BOOLEAN explicit
        SMALLINT release_year
        SMALLINT decade
        DOUBLE_PRECISION danceability
        DOUBLE_PRECISION energy
        SMALLINT key
        DOUBLE_PRECISION loudness
        SMALLINT mode
        DOUBLE_PRECISION speechiness
        DOUBLE_PRECISION acousticness
        DOUBLE_PRECISION instrumentalness
        DOUBLE_PRECISION liveness
        DOUBLE_PRECISION valence
        DOUBLE_PRECISION tempo
        SMALLINT time_signature
        INTEGER n_artists
    }
```

---

## 4. Cross-Layer Data Flow

```mermaid
flowchart TD
    subgraph SOURCE["Source Files (raw data)"]
        T["tracks.csv\n586,672 rows"]
        A["artists.csv\n1,162,095 rows"]
        J["dict_artists.json\n573,856 keys\n(RELATED_ARTIST_GRAPH)"]
    end

    subgraph RAW["Raw Layer (schema: raw)"]
        RT["raw_tracks"]
        RA["raw_artists"]
        RJ["raw_artist_json"]
    end

    subgraph CLEAN["Clean Layer (schema: clean)"]
        CT["tracks"]
        CA["artists"]
        CG["genres"]
        CTA["track_artists"]
        CAG["artist_genres"]
        CAR["artist_relations"]
    end

    subgraph ANALYTICS["Analytics Layer (schema: analytics)"]
        V1["vw_tracks_overview"]
        V2["vw_tracks_by_decade"]
        V3["vw_audio_trends"]
        V4["vw_top_artists"]
        V5["vw_genre_trends"]
        V6["vw_ml_training_dataset"]
    end

    T -->|Feature 1.3 import| RT
    A -->|Feature 1.3 import| RA
    J -->|Feature 1.3 import| RJ

    RT -->|Feature 1.4 parse & clean| CT
    RT -->|explode id_artists| CTA
    RA -->|Feature 1.4 parse & clean| CA
    RA -->|explode genres| CG
    CA & CG -->|link| CAG
    RJ -->|Feature 1.4 parse| CAR

    CT & CA & CTA -->|Feature 1.6 views| V1
    CT -->|Feature 1.6 views| V2
    CT -->|Feature 1.6 views| V3
    CT & CTA & CA -->|Feature 1.6 views| V4
    CT & CTA & CAG & CG -->|Feature 1.6 views| V5
    CT & CTA -->|Feature 1.6 ML handoff| V6
```
