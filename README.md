# 📋 TaskFlow

![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostGre](https://img.shields.io/badge/Postgre-EC4899?style=for-the-badge&logo=postgre&logoColor=white)
![Status](https://img.shields.io/badge/Status-En%20développement-orange?style=for-the-badge)

**TaskFlow** est une application de gestion de tâches moderne et intuitive, construite avec une architecture full-stack robuste. L'application combine un frontend Vue.js réactif avec un backend Python performant pour offrir une expérience utilisateur fluide et professionnelle.

## ✨ Fonctionnalités

- 📝 **Gestion de tâches intuitive** - Créer, éditer, supprimer des tâches
- 🎯 **Système de priorités** - Organiser vos tâches par importance
- ✅ **Suivi de progression** - Marquer les tâches comme terminées
- 🎨 **Interface moderne** - Design system cohérent avec animations fluides
- 📱 **Responsive** - Compatible desktop, tablette et mobile
- 📤 **Export des données**

## 🔮 Roadmap

- [ ] **Authentification utilisateur**
- [ ] **Catégories de tâches**
- [ ] **Dates d'échéance**
- [ ] **Notifications**
- [ ] **Mode sombre**
- [ ] **API mobile**
- [ ] **Import des données**

## 🚀 Run
cd /Users/eloise/Developpements/todolist-v2/backend
cd /Users/eloise/Developpements/todolist-v2/frontend
Check Makefile to run local servers


## Git
git init

git config --global user.name "eloiseboudon"
git config --global user.email "boudon.eloise@gmail.com"

git remote add origin https://github.com/eloiseboudon/todolist.git

🔄 1. Merger feature → dev
bash# S'assurer que vous êtes sur votre branche feature et que tout est commité
git status
git add .
git commit -m "feat: [description de votre feature]"

### Basculer vers dev
git checkout dev

### Merger votre feature dans dev
git merge feature/[nom-de-votre-branche]

### Pusher dev avec les nouveaux changements
git push origin dev
🚀 2. Merger dev → main (si la feature est stable)
bash# Basculer vers main
git checkout main

### Merger dev dans main
git merge dev

### Pusher main avec les nouveaux changements
git push origin main
🧹 3. Nettoyer (optionnel)
bash# Supprimer la branche feature localement (si plus nécessaire)
git branch -d feature/[nom-de-votre-branche]

### Supprimer la branche feature sur GitHub (si elle existe)
git push origin --delete feature/[nom-de-votre-branche]


### Connexion SSH :

git remote set-url origin git@github.com:eloiseboudon/todolist.git

### Puis configurer une clé SSH si pas encore fait
ssh-keygen -t ed25519 -C "boudon.eloise@gmail.com"

pass

Your public key has been saved in /Users/eloise/.ssh/id_ed25519.pub
The key fingerprint is:
SHA256:YJuMTmepdj5y8j026asaY92Tn9TzBrp9kO+eE6y84jQ boudon.eloise@gmail.com
The key's randomart image is:
+--[ED25519 256]--+
|                 |
|                 |
|      o          |
|     + =         |
|    o B S    o   |
|   o = . . .+ o  |
|    B o +.Eoo= . |
|   oo=o.==o+oo=. |
|    .*+=+==oo*=. |
+----[SHA256]-----+




## 👩‍💻 Auteur

**Eloise Boudon**
- GitHub: [@eloiseboudon](https://github.com/eloiseboudon)
- Email: boudon.eloise@gmail.com