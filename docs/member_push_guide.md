# Guide de push par membre

Ce fichier indique quelle partie du code chaque membre peut pousser depuis son propre compte GitHub.  
Chaque collaborateur doit cloner le dépôt, créer sa branche, ajouter uniquement les fichiers de sa partie, puis pousser sa branche.

Depot :

```text
https://github.com/AyoubElho/fitness-coach-multi-agent.git
```

Important :

- Ne jamais pousser le fichier `.env`.
- Ne pas pousser `venv/`, `__pycache__/`, `data/vectorstore/` ou les fichiers `.log`.
- Chaque membre doit utiliser son propre compte GitHub pour que la contribution soit associée à son identité.
- Après le push, ouvrir une Pull Request vers `main`.

## 1. OUSSAMA FELOUACH

GitHub : `@oussamafelouach-etu-lgtm`

### Partie code à pousser

```text
#agents/workout_designer.py
#agents/nutrition_planner.py
#rag/ingest.py
#rag/retriever.py
data/documents/
```

### Responsabilités

- Développement de l'agent `workout_designer`.
- Développement de l'agent `nutrition_planner`.
- Intégration du RAG dans les agents.
- Préparation du pipeline d'ingestion des PDF.
- Configuration de la recherche avec ChromaDB.
- Tests du module RAG et des plans générés.

### Commandes Git conseillées

```powershell
git clone https://github.com/AyoubElho/fitness-coach-multi-agent.git
cd fitness-coach-multi-agent
git checkout -b contribution/oussama-rag-agents

git add agents/workout_designer.py agents/nutrition_planner.py rag/ingest.py rag/retriever.py data/documents/
git commit -m "Add workout nutrition and RAG modules"
git push origin contribution/oussama-rag-agents
```

## 2. ETTALEBY MBAREK

GitHub : `@mbarekTrismegistus`

### Partie code à pousser

```text
state.py
graph.py
agents/supervisor.py
agents/goal_analyzer.py
tests/test_graph.py
```

### Responsabilités

- Définition de l'état partagé `FitnessState`.
- Construction du graphe LangGraph.
- Développement du superviseur déterministe.
- Développement de l'agent `goal_analyzer`.
- Routage entre les agents spécialisés.
- Tests du workflow principal.

### Commandes Git conseillées

```powershell
git clone https://github.com/AyoubElho/fitness-coach-multi-agent.git
cd fitness-coach-multi-agent
git checkout -b contribution/mbarek-orchestration

git add state.py graph.py agents/supervisor.py agents/goal_analyzer.py tests/test_graph.py
git commit -m "Add orchestration supervisor and goal analysis"
git push origin contribution/mbarek-orchestration
```

## 3. AYOUB EL HOUANI

GitHub : `@AyoubElho`

### Partie code à pousser

```text
agents/progress_tracker.py
ui/app.py
evaluation/test_cases.py
evaluation/ab_test.py
evaluation/ab_results.json
README.md
docs/images/
docs/demo/
```

### Responsabilités

- Développement de l'agent `progress_tracker`.
- Ajout du point de validation Human-in-the-loop.
- Développement de l'interface Streamlit.
- Affichage des résultats en onglets.
- Export du plan final en Markdown.
- Évaluation A/B des prompts.
- Captures, démonstration et documentation du projet.

### Commandes Git conseillées

```powershell
git clone https://github.com/AyoubElho/fitness-coach-multi-agent.git
cd fitness-coach-multi-agent
git checkout -b contribution/ayoub-ui-evaluation

git add agents/progress_tracker.py ui/app.py evaluation/test_cases.py evaluation/ab_test.py evaluation/ab_results.json README.md docs/images/ docs/demo/
git commit -m "Add progress tracking UI evaluation and documentation"
git push origin contribution/ayoub-ui-evaluation
```

## Vérification avant push

Avant chaque commit, vérifier les fichiers ajoutés :

```powershell
git status --short
git diff --cached --stat
```

Lancer les validations utiles :

```powershell
python -m py_compile ui/app.py
python -m py_compile graph.py
python -m evaluation.ab_test
```
