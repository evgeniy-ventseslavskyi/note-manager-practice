const { DataTypes } = require('sequelize');

function defineModels(sequelize) {
  const Category = sequelize.define('Category', {
    name: { type: DataTypes.STRING(80), allowNull: false, unique: true },
    description: { type: DataTypes.STRING(255), allowNull: true }
  });
  const Tag = sequelize.define('Tag', {
    name: { type: DataTypes.STRING(50), allowNull: false, unique: true }
  });
  const Note = sequelize.define('Note', {
    title: { type: DataTypes.STRING(150), allowNull: false },
    content: { type: DataTypes.TEXT, allowNull: false }
  });

  Category.hasMany(Note, { foreignKey: { name: 'categoryId', allowNull: false }, onDelete: 'RESTRICT' });
  Note.belongsTo(Category, { foreignKey: { name: 'categoryId', allowNull: false } });
  Note.belongsToMany(Tag, { through: 'NoteTags' });
  Tag.belongsToMany(Note, { through: 'NoteTags' });
  return { Category, Tag, Note };
}

module.exports = { defineModels };
