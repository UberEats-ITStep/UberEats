import type { MenuCategory } from '../types/restaurant.types';

export type MenuCategoryFilterState = {
  searchTerm: string;
  selectedCategory: number | 'all';
  showAvailableOnly: boolean;
};

export const filterMenuCategories = (
  categories: MenuCategory[],
  { searchTerm, selectedCategory, showAvailableOnly }: MenuCategoryFilterState,
): MenuCategory[] => {
  const normalizedSearch = searchTerm.trim().toLowerCase();

  return categories
    .map((category) => {
      const filteredItems = category.menu_items.filter((item) => {
        const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
        const matchesAvailability = !showAvailableOnly || item.is_available;
        const haystack = [item.name, item.description, item.category_name]
          .filter(Boolean)
          .join(' ')
          .toLowerCase();
        const matchesSearch = !normalizedSearch || haystack.includes(normalizedSearch);

        return matchesCategory && matchesAvailability && matchesSearch;
      });

      return {
        ...category,
        menu_items: filteredItems,
      };
    })
    .filter((category) => category.menu_items.length > 0);
};
