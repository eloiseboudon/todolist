import { ref, watchEffect } from 'vue';

export type Theme = 'light' | 'dark';

const stored = localStorage.getItem('theme') as Theme | null;
const theme = ref<Theme>(stored || 'light');
document.documentElement.setAttribute('data-theme', theme.value);

export function useTheme() {
  const setTheme = (newTheme: Theme) => {
    theme.value = newTheme;
  };

  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light';
  };

  watchEffect(() => {
    const root = document.documentElement;
    root.setAttribute('data-theme', theme.value);
    localStorage.setItem('theme', theme.value);
  });

  return { theme, setTheme, toggleTheme };
}
