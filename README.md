# 🎯 PyQt6 Macro Recorder - Clone Jitbit

Un clone moderne et ergonomique de Jitbit Macro Recorder développé en Python 3.12 avec PyQt6.

## ✨ Fonctionnalités

### 🎙️ Enregistrement
- **Capture automatique** des mouvements de souris et clics
- **Enregistrement des touches clavier** et texte saisi
- **Enregistrement intelligent** avec timestamps précis
- **Interface visuelle en temps réel** des actions capturées

### ▶️ Lecture et Automation
- **Lecture fidèle** des macros enregistrées
- **Vitesse variable** (0.1x à 5.0x)
- **Répétition configurable** (1 à 999 fois)
- **Délai avant lecture** personnalisable
- **Lecture pas à pas** avec indicateur visuel

### 🎨 Interface Moderne
- **Design PyQt6 moderne** avec style Fusion
- **Interface ergonomique** et intuitive
- **Thème clair professionnel**
- **Animations et feedback visuel**
- **Responsive design**

### 📁 Gestion des Fichiers
- **Sauvegarde/Chargement** au format JSON
- **Format lisible** et éditable manuellement
- **Gestion des versions** et métadonnées
- **Import/Export** simple

### ⌨️ Raccourcis Clavier
- **F9**: Démarrer/Arrêter l'enregistrement
- **F10**: Jouer/Pause
- **F11**: Arrêter la lecture
- **Ctrl+N**: Nouvelle macro
- **Ctrl+O**: Ouvrir macro
- **Ctrl+S**: Sauvegarder

### 🛠️ Fonctionnalités Avancées
- **Édition des actions** (à venir)
- **Conditions logiques** (à venir)
- **Détection d'images** (à venir)
- **Compilation en EXE** (via auto-py-to-exe)

## 🚀 Installation

### Prérequis
- Python 3.12 ou plus récent
- pip (gestionnaire de packages Python)

### Installation automatique
```bash
# Cloner ou télécharger le projet
git clone [URL_DU_REPO]
cd macro-recorder-clone

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python macro_recorder_jitbit_clone.py
```

### Installation manuelle
```bash
# Installer les dépendances une par une
pip install PyQt6
pip install pyautogui

# Lancer l'application
python macro_recorder_jitbit_clone.py
```

## 📦 Dépendances

- **PyQt6** (>= 6.0.0) - Interface graphique moderne
- **pyautogui** (>= 0.9.50) - Automation souris/clavier

## 🎮 Utilisation

### Premier lancement
1. **Démarrez** l'application en exécutant le fichier Python
2. L'interface moderne s'ouvre avec tous les contrôles disponibles
3. **Lisez** les instructions dans la barre de statut

### Enregistrer une macro
1. **Cliquez** sur "🔴 Démarrer" ou appuyez sur **F9**
2. **Effectuez** vos actions (souris et clavier)
3. **Cliquez** sur "⏹️ Arrêter" ou appuyez sur **F9** à nouveau
4. Les actions apparaissent dans la liste avec timestamps

### Jouer une macro
1. **Sélectionnez** la vitesse désirée (curseur)
2. **Configurez** le nombre de répétitions
3. **Cliquez** sur "▶️ Jouer" ou appuyez sur **F10**
4. **Observez** la lecture en temps réel

### Sauvegarder/Charger
1. **Menu Fichiers** → "💾 Sauver" pour sauvegarder
2. **Menu Fichiers** → "📂 Ouvrir" pour charger
3. Les fichiers sont au **format JSON** lisible

## 🏗️ Architecture

### Structure du Code
```
macro_recorder_jitbit_clone.py
├── MacroAction          # Structure de données pour les actions
├── MacroRecorder        # Classe d'enregistrement
├── MacroPlayer          # Classe de lecture
├── ModernButton         # Bouton avec style moderne
├── ActionListWidget     # Liste stylisée des actions
└── MacroRecorderUI      # Interface principale
```

### Classes Principales

#### `MacroAction`
Dataclass représentant une action enregistrée:
- `action_type`: Type d'action (mouse_click, key_press, etc.)
- `timestamp`: Moment de l'action
- `data`: Données spécifiques à l'action

#### `MacroRecorder`
Gère l'enregistrement des actions:
- Capture en temps réel des événements
- Calcul automatique des timestamps
- Émission de signaux PyQt6

#### `MacroPlayer`
Gère la lecture des macros:
- Lecture fidèle avec délais précis
- Contrôle de vitesse et répétitions
- Gestion des erreurs

#### `MacroRecorderUI`
Interface utilisateur principale:
- Design moderne avec PyQt6
- Gestion complète des événements
- Mise à jour temps réel

## 🎨 Personnalisation

### Modifier les Styles
Le code utilise des feuilles de style CSS dans PyQt6:
```python
# Exemple de personnalisation des couleurs
self.setStyleSheet("""
    QPushButton {
        background: qlineargradient(...);
        border-radius: 8px;
        color: white;
    }
""")
```

### Ajouter des Actions
Pour ajouter de nouveaux types d'actions:
1. Étendre l'enum des `action_type`
2. Modifier `MacroRecorder._record_loop()`
3. Mettre à jour `MacroPlayer._execute_action()`
4. Adapter l'affichage dans `ActionListWidget`

## 🔧 Développement

### Mode Debug
Activez le mode debug en modifiant:
```python
# En haut du fichier
DEBUG = True
pyautogui.PAUSE = 0.5  # Ralentit pour debug
```

### Tests
```bash
# Tests unitaires (à implémenter)
python -m pytest tests/

# Tests d'interface
python macro_recorder_jitbit_clone.py --test
```

### Compilation en Exécutable
```bash
# Avec auto-py-to-exe (recommandé)
pip install auto-py-to-exe
auto-py-to-exe

# Ou avec pyinstaller
pip install pyinstaller
pyinstaller --onefile --windowed macro_recorder_jitbit_clone.py
```

## 🚫 Limitations Actuelles

- **Enregistrement limité** aux mouvements souris basiques
- **Pas de détection d'images** sur écran
- **Pas de conditions logiques** dans les macros
- **Raccourcis globaux** nécessitent des modules supplémentaires
- **Pas d'édition avancée** des actions

## 🛣️ Roadmap

### Version 1.1
- [ ] Enregistrement complet clavier
- [ ] Édition des actions enregistrées
- [ ] Pause/reprise de l'enregistrement
- [ ] Export vers différents formats

### Version 1.2
- [ ] Détection d'images à l'écran
- [ ] Conditions logiques (if/then)
- [ ] Variables dans les macros
- [ ] Templates de macros courantes

### Version 2.0
- [ ] Raccourcis clavier globaux
- [ ] Interface multi-onglets
- [ ] Macros collaboratives
- [ ] API REST pour automation

## 🤝 Contribution

Les contributions sont les bienvenues !

1. **Fork** le projet
2. **Créez** une branche feature (`git checkout -b feature/AmazingFeature`)
3. **Commitez** vos changements (`git commit -m 'Add AmazingFeature'`)
4. **Push** vers la branche (`git push origin feature/AmazingFeature`)
5. **Ouvrez** une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👨‍💻 Auteur

**Assistant IA - Ingénieur Développement Software**
- Spécialisé en interfaces Python modernes
- Expert PyQt6 et automation

## 🙏 Remerciements

- **Jitbit Software** pour l'inspiration du design original
- **Riverbank Computing** pour PyQt6
- **Communauté Python** pour pyautogui
- **Utilisateurs** pour les retours et suggestions

## 📞 Support

Pour toute question ou problème:
1. **Consultez** la documentation ci-dessus
2. **Vérifiez** les issues existantes
3. **Créez** une nouvelle issue si nécessaire
4. **Contactez** le développeur

---

**Bon coding ! 🚀**
