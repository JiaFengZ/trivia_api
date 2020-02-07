export function formatCategories(categories) {
  let data = {};
  categories.forEach(category => {
    data[category.id] = category.type
  });
  return data;
}