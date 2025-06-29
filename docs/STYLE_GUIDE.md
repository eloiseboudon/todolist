# Style Guide: Fictional Sans

Ce guide propose un nouveau style inspiré par [Fictional Typeface](https://fictional-typeface.com/). Il introduit une nouvelle police principale **Fictional Sans** et quelques recommandations de design.

## Police
- Importez la police via une règle `@font-face` :

```css
@font-face {
  font-family: 'Fictional Sans';
  src: url('../assets/fonts/FictionalSans.woff2') format('woff2');
}
```

- Utiliser `Fictional Sans` comme police par défaut quand la variable CSS `--font-family-fictional` est activée.
- Prévoir une police de secours générique `sans-serif`.

## Utilisation

```css
:root {
  --font-family-fictional: 'Fictional Sans', sans-serif;
}

body[data-style="fictional"] {
  font-family: var(--font-family-fictional);
  background: linear-gradient(135deg, #ff80ab, #ff1744);
  color: #ffffff;
}
```

Pour activer ce style, ajoutez l'attribut `data-style="fictional"` à la balise `<body>`.
