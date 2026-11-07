const { Sequelize } = require('sequelize');

function createDatabase() {
  return new Sequelize({
    dialect: 'sqlite',
    storage: process.env.DB_STORAGE || './data/notes.sqlite',
    logging: false
  });
}

module.exports = { createDatabase };
