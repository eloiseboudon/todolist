// frontend/src/utils/categoryUtils.ts

/**
 * Mapping des icônes de catégories
 * Convertit les noms d'icônes en emojis
 */
const CATEGORY_ICONS: Record<string, string> = {
    // Catégories principales
    'folder': '📁',
    'personal': '🛀🏽',
    'shopping': '🛒',
    'health': '💊',
    'education': '🎓',
    'travel': '✈️',
    'home': '🏠',
    'finance': '💰',
    'hobbies': '🎨',

    // Catégories famille et social
    'family': '👨‍👩‍👧‍👦',
    'friends': '🤼‍♀️',
    'social': '🎪',

    // Catégories activités
    'sport': '⚽',
    'fitness': '💪',
    'music': '🎵',
    'books': '📚',
    'movies': '🎬',
    'games': '🎮',

    // Catégories technologie
    'work': '💻',
    'development': '⚙️',
    'design': '🎨',
    'mobile': '📱',

    // Catégories vie quotidienne
    'food': '🍔',
    'cooking': '👨‍🍳',
    'car': '🚗',
    'pets': '🐕',
    'garden': '🌱',
    'cleaning': '🧹',

    // Catégories business
    'meeting': '🤹🏾‍♂️',
    'project': '📊',
    'marketing': '📈',
    'sales': '💼',

    // Catégories créativité
    'art': '🎨',
    'writing': '✍️',
    'photography': '📸',
    'video': '🎥',

    // Catégories bien-être
    'meditation': '🧘',
    'yoga': '🤸',
    'sleep': '😴',
    'mental-health': '🧠',

    // Par défaut
    'default': '📋',
    'other': '📌',
    'misc': '🔖',

    'love': '🧡',
    'users': '👤',
    'receipt': '📄',

};

/**
 * Obtient l'emoji correspondant à une icône de catégorie
 * @param iconName - Le nom de l'icône
 * @returns L'emoji correspondant ou l'emoji par défaut
 */
export function getCategoryIcon(iconName: string): string {
    if (!iconName || typeof iconName !== 'string') {
        return CATEGORY_ICONS.default;
    }

    const normalizedName = iconName.toLowerCase().trim();
    return CATEGORY_ICONS[normalizedName] || CATEGORY_ICONS.default;
}

/**
 * Obtient la liste de toutes les icônes disponibles
 * @returns Un objet avec les noms et emojis des icônes
 */
export function getAvailableIcons(): Record<string, string> {
    return { ...CATEGORY_ICONS };
}

/**
 * Vérifie si une icône existe dans le mapping
 * @param iconName - Le nom de l'icône à vérifier
 * @returns true si l'icône existe, false sinon
 */
export function isValidCategoryIcon(iconName: string): boolean {
    if (!iconName || typeof iconName !== 'string') {
        return false;
    }

    const normalizedName = iconName.toLowerCase().trim();
    return normalizedName in CATEGORY_ICONS;
}

/**
 * Génère une couleur par défaut pour une catégorie basée sur son nom
 * @param categoryName - Le nom de la catégorie
 * @returns Une couleur hexadécimale
 */
export function generateCategoryColor(categoryName: string): string {
    if (!categoryName) return '#3B82F6'; // Bleu par défaut

    // Couleurs prédéfinies agréables
    const colors = [
        '#3B82F6', // Bleu
        '#10B981', // Vert
        '#F59E0B', // Jaune/Orange
        '#EF4444', // Rouge
        '#8B5CF6', // Violet
        '#06B6D4', // Cyan
        '#84CC16', // Lime
        '#F97316', // Orange
        '#EC4899', // Rose
        '#6366F1', // Indigo
    ];

    // Utiliser le nom pour générer un index déterministe
    let hash = 0;
    for (let i = 0; i < categoryName.length; i++) {
        hash = categoryName.charCodeAt(i) + ((hash << 5) - hash);
    }

    const index = Math.abs(hash) % colors.length;
    return colors[index];
}

/**
 * Valide une couleur hexadécimale
 * @param color - La couleur à valider
 * @returns true si la couleur est valide, false sinon
 */
export function isValidHexColor(color: string): boolean {
    if (!color || typeof color !== 'string') {
        return false;
    }

    const hexColorRegex = /^#[0-9A-Fa-f]{6}$/;
    return hexColorRegex.test(color);
}

/**
 * Type pour une catégorie simplifiée (utilisé dans les composants)
 */
export interface CategoryDisplay {
    id: number;
    name: string;
    color: string;
    icon: string;
    emoji: string; // L'emoji généré automatiquement
}

/**
 * Prépare une catégorie pour l'affichage
 * @param category - La catégorie à préparer
 * @returns La catégorie avec l'emoji généré
 */
export function prepareCategoryForDisplay(category: {
    id: number;
    name: string;
    color: string;
    icon: string;
}): CategoryDisplay {
    return {
        ...category,
        emoji: getCategoryIcon(category.icon)
    };
}